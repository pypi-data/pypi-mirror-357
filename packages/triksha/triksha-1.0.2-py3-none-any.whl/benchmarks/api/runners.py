import time

class APIBenchmarkRunner:
    """Runner for API benchmarks"""
    
    def __init__(self, **kwargs):
        """Initialize with flexible kwargs for compatibility"""
        self.db = kwargs.get('db')
        self.console = kwargs.get('console')
        self.backup_manager = kwargs.get('backup_manager')
        self.openai_model = kwargs.get('openai_model', 'gpt-3.5-turbo')
        self.gemini_model = kwargs.get('gemini_model', 'gemini-pro') 
        self.verbose = kwargs.get('verbose', False)
        self.concurrency = kwargs.get('concurrency', 5)
        self.num_prompts = kwargs.get('num_prompts', 5)  # Store num_prompts from kwargs
    
    def run(self, resume_session=None, force_templates=False):
        """Run the benchmark
        
        Args:
            resume_session: Optional session ID to resume
            force_templates: Whether to force using templates instead of model
            
        Returns:
            Benchmark results
        """
        # Use the stored num_prompts value
        num_prompts = self.num_prompts
        
        # Print the number of prompts we're generating for clarity
        if self.console:
            self.console.print(f"[blue]Running optimized benchmark with {num_prompts} prompts[/]")
        
        # Setup the benchmark runner with optimized generation
        start_time = time.time()
        runner = BenchmarkRunner(model_path="karanxa/Dravik", verbose=self.verbose)
        
        # Generate test prompts with optimized batch processing
        prompts = runner.generate_test_prompts(num_prompts=num_prompts)
        
        if self.console:
            generation_time = time.time() - start_time
            self.console.print(f"[green]Generated {len(prompts)} prompts in {generation_time:.2f}s " + 
                              f"({len(prompts)/generation_time:.2f} prompts/sec)[/]")
        
        if len(prompts) != num_prompts:
            if self.console:
                self.console.print(f"[yellow]Warning: Expected {num_prompts} prompts but generated {len(prompts)}[/]")
