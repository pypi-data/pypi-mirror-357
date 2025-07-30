"""
Retry logic for handling rate limits and transient errors in benchmarks
"""

import asyncio
import random
import re
from typing import Optional, Dict, Any, Callable, List
from rich.console import Console
from datetime import datetime, timedelta
from collections import deque


class RetryableError(Exception):
    """Exception for errors that should be retried"""
    pass


class RateLimitError(RetryableError):
    """Exception for rate limit errors"""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class GlobalRateLimiter:
    """Global rate limiter to manage request rates across all operations"""
    def __init__(self):
        self.last_request_time = datetime.now()
        self.min_request_interval = 0.1  # Start with 100ms between requests
        self.rate_limit_hits = 0
        self.last_rate_limit = None
        
    def update_rate_limit(self, success: bool):
        """Update rate limiting based on success/failure"""
        now = datetime.now()
        if success:
            # Gradually decrease interval if we're succeeding
            if self.rate_limit_hits > 0:
                self.rate_limit_hits = max(0, self.rate_limit_hits - 1)
                if self.rate_limit_hits == 0:
                    self.min_request_interval = max(0.1, self.min_request_interval * 0.8)
        else:
            # Increase interval on rate limit hits
            self.rate_limit_hits += 1
            self.last_rate_limit = now
            self.min_request_interval = min(60, self.min_request_interval * 2)
    
    async def wait_for_next_request(self):
        """Wait appropriate time before next request"""
        now = datetime.now()
        time_since_last = (now - self.last_request_time).total_seconds()
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = datetime.now()


class RetryQueue:
    """Queue for managing retried requests"""
    def __init__(self, max_size: int = 1000):
        self.queue = deque(maxlen=max_size)
        self.in_progress = set()
    
    def add(self, item: Dict[str, Any]):
        """Add item to retry queue if not already present"""
        item_key = (item.get('prompt'), item.get('model_id'))
        if item_key not in self.in_progress:
            self.queue.append(item)
            self.in_progress.add(item_key)
    
    def get(self) -> Optional[Dict[str, Any]]:
        """Get next item from queue"""
        try:
            return self.queue.popleft()
        except IndexError:
            return None
    
    def complete(self, item: Dict[str, Any]):
        """Mark item as completed"""
        item_key = (item.get('prompt'), item.get('model_id'))
        self.in_progress.discard(item_key)
    
    def __len__(self):
        return len(self.queue)


class RetryConfig:
    """Configuration for retry logic"""
    def __init__(self, 
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True,
                 global_rate_limiter: Optional[GlobalRateLimiter] = None,
                 retry_queue: Optional[RetryQueue] = None):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.global_rate_limiter = global_rate_limiter or GlobalRateLimiter()
        self.retry_queue = retry_queue or RetryQueue()
    
    def get_delay(self, attempt: int, suggested_delay: Optional[float] = None) -> float:
        """Calculate delay for the given attempt number"""
        if suggested_delay:
            # If the API suggests a specific delay (e.g., Retry-After header), use it
            delay = min(suggested_delay, self.max_delay)
        else:
            # Calculate exponential backoff delay
            delay = self.base_delay * (self.exponential_base ** attempt)
            delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable"""
    error_str = str(error).lower()
    
    # Rate limit errors
    rate_limit_indicators = [
        'rate limit', 'rate_limit', 'ratelimit',
        'too many requests', 'quota exceeded',
        'throttled', 'throttling',
        '429', 'status_code=429'
    ]
    
    # Temporary network/server errors
    temporary_error_indicators = [
        'timeout', 'connection', 'network',
        'temporary', 'temporarily',
        '502', '503', '504',
        'bad gateway', 'service unavailable', 'gateway timeout',
        'internal server error', '500'
    ]
    
    # Check for retryable error patterns
    for indicator in rate_limit_indicators + temporary_error_indicators:
        if indicator in error_str:
            return True
    
    return False


def extract_retry_after(error: Exception) -> Optional[float]:
    """Extract retry-after delay from error message or headers"""
    error_str = str(error)
    
    # Look for retry-after patterns in error message
    
    # Pattern: "retry after X seconds"
    match = re.search(r'retry.*?after.*?(\d+(?:\.\d+)?)', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Pattern: "wait X seconds"
    match = re.search(r'wait.*?(\d+(?:\.\d+)?)\s*seconds?', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Pattern: "try again in X minutes"
    match = re.search(r'try.*?again.*?in.*?(\d+(?:\.\d+)?)\s*minutes?', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1)) * 60
    
    return None


async def retry_with_backoff(
    func,
    *args,
    retry_config: RetryConfig = None,
    console: Console = None,
    prompt_info: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a function with retry logic and exponential backoff
    
    Args:
        func: The function to execute
        *args: Arguments for the function
        retry_config: Configuration for retry behavior
        console: Console for logging
        prompt_info: Information about the prompt being processed
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result dictionary with success/error information
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    if console is None:
        console = Console()
    
    last_error = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            # Wait for rate limiter before making request
            await retry_config.global_rate_limiter.wait_for_next_request()
            
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Update rate limiter on success
            retry_config.global_rate_limiter.update_rate_limit(True)
            
            # If we get here, the function succeeded
            if attempt > 0:
                console.print(f"[green]✓ Retry successful after {attempt} attempt(s)[/]")
            
            return {
                "success": True,
                "result": result,
                "attempts": attempt + 1
            }
            
        except Exception as e:
            last_error = e
            
            # Update rate limiter on failure
            if is_retryable_error(e):
                retry_config.global_rate_limiter.update_rate_limit(False)
            
            # Check if this is the last attempt
            if attempt >= retry_config.max_retries:
                # Add to retry queue if it's a rate limit error
                if is_retryable_error(e) and retry_config.retry_queue is not None:
                    retry_item = {
                        "func": func,
                        "args": args,
                        "kwargs": kwargs,
                        "prompt": kwargs.get("prompt") or args[0] if args else None,
                        "model_id": kwargs.get("model_id"),
                        "attempt": 0,
                        "last_error": str(e)
                    }
                    retry_config.retry_queue.add(retry_item)
                    console.print(f"[yellow]Added to retry queue after exhausting immediate retries[/]")
                break
            
            # Check if the error is retryable
            if not is_retryable_error(e):
                # Non-retryable error, fail immediately
                break
            
            # Calculate delay
            suggested_delay = extract_retry_after(e)
            delay = retry_config.get_delay(attempt, suggested_delay)
            
            # Log the retry attempt
            error_type = "Rate limit" if any(x in str(e).lower() for x in ['rate limit', '429']) else "Error"
            if prompt_info:
                console.print(f"[yellow]{error_type} for {prompt_info}: {str(e)[:100]}...[/]")
            else:
                console.print(f"[yellow]{error_type}: {str(e)[:100]}...[/]")
            
            console.print(f"[cyan]Retrying in {delay:.1f} seconds (attempt {attempt + 1}/{retry_config.max_retries + 1})[/]")
            
            # Wait before retrying
            await asyncio.sleep(delay)
    
    # All retries exhausted
    console.print(f"[red]All retry attempts exhausted. Final error: {str(last_error)[:100]}...[/]")
    
    return {
        "success": False,
        "error": str(last_error),
        "attempts": retry_config.max_retries + 1,
        "queued_for_retry": is_retryable_error(last_error) and retry_config.retry_queue is not None
    }


async def process_retry_queue(
    retry_config: RetryConfig,
    console: Console = None,
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """Process items in the retry queue"""
    if console is None:
        console = Console()
    
    results = []
    while len(retry_config.retry_queue) > 0:
        item = retry_config.retry_queue.get()
        if item is None:
            continue
        
        try:
            # Attempt to process the queued item
            result = await retry_with_backoff(
                item["func"],
                *item["args"],
                retry_config=retry_config,
                console=console,
                prompt_info=f"Queued retry for {item.get('prompt', 'unknown')}",
                **item["kwargs"]
            )
            
            if result["success"]:
                retry_config.retry_queue.complete(item)
                results.append(result)
            else:
                # If still failing and under max retries, re-queue with increased attempt count
                item["attempt"] += 1
                if item["attempt"] < max_retries:
                    retry_config.retry_queue.add(item)
                else:
                    retry_config.retry_queue.complete(item)
                    results.append(result)
        
        except Exception as e:
            console.print(f"[red]Error processing retry queue item: {str(e)}[/]")
            retry_config.retry_queue.complete(item)
            results.append({
                "success": False,
                "error": str(e),
                "attempts": item["attempt"] + 1
            })
    
    return results 