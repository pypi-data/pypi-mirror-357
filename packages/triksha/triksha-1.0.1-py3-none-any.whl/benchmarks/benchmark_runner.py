"""Main benchmark runner that coordinates benchmark processes"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
from rich.console import Console

from .core.base_benchmark import BaseBenchmark
from .prompting.prompt_generator import PromptGenerator
from .api.bypass_tester import BypassTester
from .utils.backup_manager import BackupManager
from utils.env_loader import load_environment

class BenchmarkRunner(BaseBenchmark):
    """Main benchmark coordinator that orchestrates the benchmark process"""
    
    DEFAULT_MODEL = "karanxa/Dravik"
    
    def __init__(self, model_path: Optional[str] = None, verbose: bool = False):
        """Initialize benchmark runner with modular components"""
        # Initialize base benchmark first
        super().__init__(verbose=verbose)
        
        # Get model path from params or environment
        env_settings = {}
        try:
            env_settings = load_environment(verbose=verbose) or {}
        except Exception as e:
            self._log(f"Error loading environment: {str(e)}", "warning")
            
        # Initialize core components
        self.model_name = model_path or env_settings.get("default_model", self.DEFAULT_MODEL)
        self.prompt_generator = PromptGenerator(self.model_name, verbose=verbose)
        self.backup_manager = BackupManager()
        self.bypass_tester = None
        
        # Initialize results structure
        self.results.update({
            "model": self.model_name,
            "bypass_success": {"openai": 0, "gemini": 0}
        })
        
        self._log(f"Initialized benchmark runner with model: {self.model_name}")

    def generate_test_prompts(self, num_prompts: int = 5) -> List[str]:
        """Generate test prompts using prompt generator"""
        prompts = self.prompt_generator.generate_prompts(num_prompts)
        self._log(f"Generated {len(prompts)} test prompts", "success")
        return prompts

    async def run_benchmark(self, prompts: List[str]) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        # Initialize bypass tester if needed
        if not self.bypass_tester:
            self.bypass_tester = BypassTester(verbose=self.verbose)
        
        # Update results with prompt info
        self.results.update({
            "timestamp": datetime.now().isoformat(),
            "total_prompts": len(prompts),
            "metrics": {"test_prompts_generated": len(prompts)}
        })
        
        # Save initial state
        self.backup_manager.save_state(self.results, "started")
        
        try:
            # Process each prompt
            for i, prompt in enumerate(prompts):
                self._log(f"Testing prompt {i+1}/{len(prompts)}", "info")
                
                # Test prompt against APIs
                result = await self.bypass_tester.test_prompt(prompt)
                self.results["detailed_results"].append(result)
                
                # Update success counters
                for api, response in result.get("apis", {}).items():
                    if response.get("success", False):
                        self.results["bypass_success"][api] += 1
                
                # Backup progress periodically
                if (i + 1) % 5 == 0 or i == len(prompts) - 1:
                    self.backup_manager.save_state(
                        self.results, 
                        f"progress_{i+1}"
                    )
            
            # Calculate final scores and save results
            self._calculate_scores()
            self.backup_manager.save_state(self.results, "completed")
            
            self._log("Job completed successfully", "success")
            return self.results
            
        except Exception as e:
            self._log(f"Error during benchmark: {str(e)}", "error")
            self.backup_manager.save_state(self.results, "error")
            raise

    def _calculate_scores(self):
        """Calculate final benchmark scores"""
        total = len(self.results.get("detailed_results", []))
        if total == 0:
            return
        
        # Calculate bypass rates
        self.results["scores"] = {
            "openai_bypass_rate": (self.results["bypass_success"]["openai"] / total) * 100,
            "gemini_bypass_rate": (self.results["bypass_success"]["gemini"] / total) * 100
        }

    def run_benchmark_sync(self, prompts: List[str]) -> Dict[str, Any]:
        """Synchronous wrapper for the async run_benchmark"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.run_benchmark(prompts))
        finally:
            if 'loop' in locals():
                loop.close()
"""Main benchmark runner that coordinates benchmark processes"""