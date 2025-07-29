"""
Base template system for creating domain-specific benchmarks.
This enables consistent evaluation across different benchmark domains.
"""
from typing import Dict, List, Any, Optional, Type, Union, Callable
from enum import Enum
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

class BenchmarkDomain(Enum):
    """Domains for benchmarking LLMs"""
    SECURITY = "security"
    SAFETY = "safety"
    BUSINESS = "business"
    GENERAL = "general"
    SCIENTIFIC = "scientific"
    MEDICAL = "medical"
    LEGAL = "legal"
    CREATIVE = "creative"
    CUSTOM = "custom"

class BenchmarkTemplate:
    """Base template for creating domain-specific benchmarks"""
    
    def __init__(
        self,
        name: str,
        description: str,
        domain: Union[BenchmarkDomain, str],
        target_model: str,
        eval_models: List[Dict[str, str]] = None,
        metrics: List[str] = None,
        passing_threshold: float = 0.7,
        template_version: str = "1.0",
        max_examples: int = 50,
        verbose: bool = False,
        db = None
    ):
        """
        Initialize benchmark template with configuration
        
        Args:
            name: Name of the benchmark
            description: Description of what this benchmark evaluates
            domain: Domain category for this benchmark
            target_model: The HuggingFace model being evaluated
            eval_models: List of external LLMs to use as evaluators (e.g., {"provider": "openai", "model": "gpt-4"})
            metrics: List of metrics to track (e.g., accuracy, response_quality)
            passing_threshold: Score threshold to consider the benchmark passed
            template_version: Version of the template format
            max_examples: Maximum number of examples to process
            verbose: Whether to log detailed information
            db: Optional database instance for saving results
        """
        self.name = name
        self.description = description
        
        # Convert string to enum if needed
        if isinstance(domain, str):
            try:
                self.domain = BenchmarkDomain[domain.upper()]
            except KeyError:
                self.domain = BenchmarkDomain.CUSTOM
        else:
            self.domain = domain
            
        self.target_model = target_model
        self.eval_models = eval_models or [
            {"provider": "openai", "model": "gpt-4"},
            {"provider": "gemini", "model": "gemini-pro"}
        ]
        self.metrics = metrics or ["accuracy", "relevance", "compliance"]
        self.passing_threshold = passing_threshold
        self.template_version = template_version
        self.max_examples = max_examples
        self.verbose = verbose
        self.db = db
        
        # Initialize results structure
        self.results = {
            "benchmark": {
                "name": self.name,
                "description": self.description,
                "domain": self.domain.value,
                "template_version": self.template_version
            },
            "target_model": self.target_model,
            "eval_models": self.eval_models,
            "metrics": {},
            "examples": [],
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0.0,
            "passed": False
        }
        
        # Store the template as JSON for reference
        self.template_data = {
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "metrics": self.metrics,
            "passing_threshold": self.passing_threshold,
            "template_version": self.template_version
        }
        
        self._log(f"Initialized {self.domain} benchmark template: {self.name}")
    
    def _log(self, message: str, level: str = "info"):
        """Log messages based on verbosity"""
        if not self.verbose:
            return
        
        from rich.console import Console
        console = Console()
        
        if level == "info":
            console.print(f"[blue]{message}[/]")
        elif level == "success":
            console.print(f"[green]{message}[/]")
        elif level == "warning":
            console.print(f"[yellow]{message}[/]")
        elif level == "error":
            console.print(f"[red]{message}[/]")
        else:
            console.print(message)
    
    def save_template(self, output_dir: str = "benchmarks/templates/custom") -> str:
        """Save benchmark template for future use"""
        os.makedirs(output_dir, exist_ok=True)
        template_path = os.path.join(output_dir, f"{self.name.lower().replace(' ', '_')}_template.json")
        
        with open(template_path, 'w') as f:
            json.dump(self.template_data, f, indent=2)
        
        self._log(f"Template saved to {template_path}", "success")
        return template_path
    
    @classmethod
    def load_template(cls, template_path: str):
        """Load benchmark template from file"""
        with open(template_path, 'r') as f:
            template_data = json.load(f)
        
        return cls(
            name=template_data["name"],
            description=template_data.get("description", ""),
            domain=template_data["domain"],
            target_model="",  # To be provided at runtime
            metrics=template_data.get("metrics", []),
            passing_threshold=template_data.get("passing_threshold", 0.7),
            template_version=template_data.get("template_version", "1.0"),
            verbose=False
        )

    def prepare_example(self, example_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a single example for benchmarking
        Override this in domain-specific templates
        """
        # Default implementation just passes through
        return example_data
    
    def format_prompt(self, example: Dict[str, Any]) -> str:
        """
        Format prompt for the target model
        Override this in domain-specific templates
        """
        # Basic default implementation
        if "prompt" in example:
            return example["prompt"]
        elif "instruction" in example:
            return example["instruction"]
        return str(example)
    
    def format_eval_prompt(self, example: Dict[str, Any], target_response: str) -> str:
        """
        Format evaluation prompt for evaluator models
        Override this in domain-specific templates
        """
        # Default implementation for evaluation
        formatted_prompt = f"""
        You are evaluating a language model's response to a given prompt.
        
        Original prompt: {self.format_prompt(example)}
        
        Model's response: {target_response}
        
        Please evaluate the response on the following metrics (score 0-10):
        {', '.join(self.metrics)}
        
        Return your evaluation as a JSON with scores and brief explanation.
        """
        return formatted_prompt
    
    def parse_eval_response(self, eval_response: str) -> Dict[str, Any]:
        """
        Parse evaluation response from evaluator model
        Override this for custom evaluation parsing
        """
        # Try to extract JSON from the response
        try:
            # Find JSON-like content - simple approach, might need enhancement
            import re
            json_match = re.search(r'\{.*\}', eval_response, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group(0))
            
            # Fallback: create basic structure with estimated scores
            scores = {}
            for metric in self.metrics:
                # Look for the metric and a number near it
                pattern = rf"{metric}[^\d]*(\d+(?:\.\d+)?)"
                match = re.search(pattern, eval_response, re.IGNORECASE)
                if match:
                    scores[metric] = float(match.group(1))
                else:
                    scores[metric] = 5.0  # Default middle score
            
            return {
                "scores": scores,
                "explanation": eval_response[:200]  # Truncated explanation
            }
        except Exception as e:
            self._log(f"Error parsing evaluation response: {str(e)}", "error")
            return {"error": str(e)}
    
    def normalize_score(self, score: float, max_score: float = 10.0) -> float:
        """Normalize score to 0-1 range"""
        return min(max(score / max_score, 0.0), 1.0)
    
    async def evaluate_response(self, example: Dict[str, Any], target_response: str):
        """Evaluate target model's response using evaluator models"""
        from ..api.openai_handler import OpenAIHandler
        from ..api.gemini_handler import GeminiHandler
        
        eval_results = []
        
        for eval_model_info in self.eval_models:
            provider = eval_model_info.get("provider", "").lower()
            model = eval_model_info.get("model", "")
            
            try:
                # Format evaluation prompt
                eval_prompt = self.format_eval_prompt(example, target_response)
                
                # Get appropriate handler
                if provider == "openai":
                    handler = OpenAIHandler(model_name=model, verbose=self.verbose)
                    eval_response = await handler.test_prompt(eval_prompt)
                    response_text = eval_response.get("response", "")
                elif provider == "gemini":
                    handler = GeminiHandler(model_name=model, verbose=self.verbose)
                    eval_response = await handler.test_prompt(eval_prompt)
                    response_text = eval_response.get("response", "")
                else:
                    self._log(f"Unsupported provider: {provider}", "warning")
                    continue
                
                # Parse evaluation response
                parsed_eval = self.parse_eval_response(response_text)
                
                # Add to results
                eval_results.append({
                    "evaluator": f"{provider}/{model}",
                    "evaluation": parsed_eval
                })
                
            except Exception as e:
                self._log(f"Error evaluating with {provider}/{model}: {str(e)}", "error")
                eval_results.append({
                    "evaluator": f"{provider}/{model}",
                    "error": str(e)
                })
        
        return eval_results
    
    def calculate_scores(self, eval_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate aggregated scores across all evaluators"""
        scores = {metric: [] for metric in self.metrics}
        
        for eval_result in eval_results:
            evaluation = eval_result.get("evaluation", {})
            if "scores" in evaluation:
                for metric, score in evaluation["scores"].items():
                    if metric in scores:
                        # Normalize to 0-1
                        scores[metric].append(self.normalize_score(float(score)))
        
        # Calculate average for each metric
        aggregated = {}
        for metric, values in scores.items():
            if values:
                aggregated[metric] = sum(values) / len(values)
            else:
                aggregated[metric] = 0.0
        
        # Calculate overall score
        aggregated["overall"] = sum(aggregated.values()) / len(aggregated) if aggregated else 0.0
        
        return aggregated
    
    async def process_example(self, example: Dict[str, Any], model_handler):
        """Process a single benchmark example"""
        try:
            # Prepare example for this domain
            prepared_example = self.prepare_example(example)
            
            # Format prompt for target model
            prompt = self.format_prompt(prepared_example)
            
            # Get response from target model
            target_response = await model_handler.generate_response(prompt)
            
            # Evaluate response using evaluator models
            eval_results = await self.evaluate_response(prepared_example, target_response)
            
            # Calculate scores
            scores = self.calculate_scores(eval_results)
            
            # Prepare result
            result = {
                "prompt": prompt,
                "target_response": target_response,
                "eval_results": eval_results,
                "scores": scores,
                "passed": scores.get("overall", 0) >= self.passing_threshold
            }
            
            return result
            
        except Exception as e:
            self._log(f"Error processing example: {str(e)}", "error")
            return {
                "error": str(e),
                "prompt": self.format_prompt(example),
                "passed": False
            }
    
    async def run_benchmark(self, examples: List[Dict[str, Any]], model_handler=None):
        """Run benchmark on all examples"""
        from ..models.model_loader import ModelLoader
        
        self._log(f"Running {self.domain} benchmark: {self.name}")
        
        # Initialize model handler if not provided
        if model_handler is None:
            model_handler = ModelLoader(self.target_model, verbose=self.verbose)
        
        # Process examples
        example_count = min(len(examples), self.max_examples)
        self.results["total_examples"] = example_count
        
        for i, example in enumerate(examples[:example_count]):
            self._log(f"Processing example {i+1}/{example_count}")
            
            # Process example
            result = await self.process_example(example, model_handler)
            
            # Add to results
            self.results["examples"].append(result)
            
            # Update running metrics
            passed_examples = sum(1 for e in self.results["examples"] if e.get("passed", False))
            self.results["metrics"]["passing_rate"] = passed_examples / (i + 1)
            
            # Calculate running average for each metric
            for metric in self.metrics:
                metric_values = [
                    e.get("scores", {}).get(metric, 0) 
                    for e in self.results["examples"] 
                    if "scores" in e and metric in e["scores"]
                ]
                if metric_values:
                    self.results["metrics"][metric] = sum(metric_values) / len(metric_values)
        
        # Calculate final results
        self._finalize_results()
        
        return self.results
    
    def _finalize_results(self):
        """Finalize benchmark results"""
        # Calculate overall score
        metric_scores = [
            value for key, value in self.results["metrics"].items() 
            if key in self.metrics
        ]
        
        if metric_scores:
            self.results["overall_score"] = sum(metric_scores) / len(metric_scores)
        else:
            self.results["overall_score"] = 0.0
        
        # Determine if benchmark passed
        self.results["passed"] = self.results["overall_score"] >= self.passing_threshold
        
        # Add pass/fail status
        status = "PASSED" if self.results["passed"] else "FAILED"
        self._log(f"Benchmark {status} with score {self.results['overall_score']:.2f}", 
                 "success" if self.results["passed"] else "warning")
    
    def save_results(self, db=None) -> bool:
        """Save benchmark results to the database
        
        Args:
            db: Optional database instance (if not provided during initialization)
            
        Returns:
            bool: Success status
        """
        # Use filesystem backup for local development/testing
        os.makedirs("benchmark_results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(
            "benchmark_results", 
            f"{self.domain.value}_{self.name.lower().replace(' ', '_')}_{timestamp}.json"
        )
        
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self._log(f"Results saved to {results_path} (local backup)", "info")
        
        # Use provided database or instance variable
        database = db or self.db
        
        if not database:
            self._log("No database instance available. Results only saved locally.", "warning")
            return False
            
        try:
            # Generate a benchmark ID if not present
            if 'benchmark_id' not in self.results:
                self.results['benchmark_id'] = str(datetime.now().strftime("%Y%m%d%H%M%S"))
            
            # Save to database
            success = database.save_benchmark_result(self.results)
            
            if success:
                self._log(f"Results saved to database with ID: {self.results.get('benchmark_id')}", "success")
            else:
                self._log("Could not save results to database", "warning")
                
            return success
            
        except Exception as e:
            self._log(f"Error saving results to database: {str(e)}", "error")
            import traceback
            traceback.print_exc()
            return False
    
    def run_benchmark_sync(self, examples: List[Dict[str, Any]], model_handler=None) -> Dict[str, Any]:
        """Synchronous wrapper for the async run_benchmark"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        try:
            return loop.run_until_complete(self.run_benchmark(examples, model_handler))
        finally:
            if loop.is_running():
                loop.close()
