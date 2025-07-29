"""User interface components for benchmarks"""
import os
import json
import asyncio
import time
import re
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import inquirer
from rich.console import Console
from rich.panel import Panel  # Add this import for Panel
from rich.table import Table
from rich import box  # This is also needed for box.ROUNDED
from benchmarks.api.bypass_tester import BypassTester
import shlex
from rich.prompt import Prompt, Confirm

class BenchmarkUI:
    """User interface for benchmark interactions"""
    
    def __init__(self, console: Console, db=None, backup_manager=None):
        """Initialize benchmark UI"""
        self.console = console
        self.db = db
        self.backup_manager = backup_manager
    
    def should_resume_session(self) -> bool:
        """Ask user if they want to resume a previous session"""
        return inquirer.confirm(
            message="Found existing benchmark sessions. Would you like to resume one?",
            default=True
        )
    
    def select_session(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Have user select a session to resume"""
        choices = []
        
        for s in sessions:
            # Create a session display string with safe fallbacks
            timestamp = s.get('timestamp', 'Unknown time')
            stage = s.get('stage', 'Unknown stage')
            
            # Get prompt count with fallback
            if 'total_prompts' in s:
                prompt_info = f"{s['total_prompts']} prompts"
            elif 'examples_tested' in s:
                prompt_info = f"{s['examples_tested']} examples"
            else:
                prompt_info = "unknown count"
                
            # Format display string
            display = f"{timestamp} ({stage}, {prompt_info})"
            
            # Add to choices
            choices.append((display, s))
        
        questions = [
            inquirer.List(
                'session',
                message="Select session to resume",
                choices=choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['session'] if answers else None
    
    def get_benchmark_type(self):
        """Get the type of benchmark to run (external dataset, internal dataset, etc.)"""
        benchmark_type_question = [
            inquirer.List(
                'type',
                message="Select dataset source for red teaming",
                choices=[
                    ('via HuggingFace', 'custom_hf_dataset'),
                    ('via Internal datasets', 'external_dataset'),
                    ('via Triksha AI', 'api'),
                    ('via a Conversation (Soon)', 'conversation_red_teaming'),
                    ('Cancel', None)
                ]
            )
        ]
        
        benchmark_type_answer = inquirer.prompt(benchmark_type_question)
        if not benchmark_type_answer or benchmark_type_answer['type'] is None:
            return None
        
        return benchmark_type_answer['type']
    
    def should_use_kubernetes(self) -> bool:
        """Ask if the user wants to run the benchmark on Kubernetes"""
        try:
            # First check if Kubernetes is available
            try:
                from kubernetes import client, config as k8s_config
                k8s_config.load_kube_config()
                k8s_available = True
            except Exception:
                k8s_available = False
                
            if not k8s_available:
                self.console.print("[yellow]Kubernetes is not available or configured on this system.[/]")
                return False
                
            # If Kubernetes is available, ask the user
            use_k8s = inquirer.confirm(
                message="Would you like to run this benchmark on Kubernetes?",
                default=True
            )
            
            if use_k8s:
                # Show benefits of Kubernetes
                self.console.print(Panel.fit(
                    "[bold green]Benefits of running on Kubernetes:[/]\n\n"
                    "• Better resource management and scalability\n"
                    "• Ability to pause/resume benchmark runs\n"
                    "• Resilience to local machine issues\n"
                    "• Monitoring capabilities via Kubernetes dashboard\n"
                    "• Parallel execution of multiple benchmarks",
                    title="[blue]KUBERNETES BENEFITS[/]",
                    border_style="blue"
                ))
                
            return use_k8s
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Error checking Kubernetes availability: {str(e)}[/]")
            return False

    async def _get_available_api_models(self) -> Dict[str, List[str]]:
        """Get available models for benchmarking"""
        self.console.print("[blue]Getting available API models...[/]")
        try:
            models = await BypassTester.get_available_models()
            return models
        except Exception as e:
            self.console.print(f"[yellow]Error getting available models: {str(e)}[/]")
            return {
                "openai": [
                    ("GPT-4o", "gpt-4o"),
                    ("GPT-4 Turbo", "gpt-4-turbo"),
                    ("GPT-4", "gpt-4"),
                    ("GPT-3.5 Turbo", "gpt-3.5-turbo"),
                    ("GPT-3.5 Turbo 16k", "gpt-3.5-turbo-16k")
                ],
                "gemini": [
                    ("Gemini 2.0 Flash", "gemini-2.0-flash"),
                    ("Gemini 1.5 Pro", "gemini-1.5-pro"),
                    ("Gemini 1.5 Flash", "gemini-1.5-flash"),
                    ("Gemini Pro", "gemini-pro"),
                    ("Gemini Pro Vision", "gemini-pro-vision")
                ]
            }

    async def _fetch_models_async(self):
        """Fetch available models asynchronously and display them in UI-friendly format"""
        try:
            from benchmarks.api.bypass_tester import BypassTester
            
            self.console.print("[dim]Fetching available models from API providers...[/]")
            
            # Show a spinner while fetching models
            with self.console.status("[bold green]Querying APIs for available models...[/]", spinner="dots"):
                try:
                    models = await BypassTester.get_available_models(console=self.console)
                    
                    # Transform the models into the format expected by the UI
                    formatted_models = {
                        "openai": [],
                        "gemini": [],
                        "custom": []
                    }
                    
                    # Format OpenAI models with proper width constraints
                    for model_id in models["openai"]:
                        # Create display name with proper formatting
                        display_name = model_id.replace("gpt-", "GPT-").replace("-turbo", " Turbo")
                        # Limit display name length to prevent UI overflow
                        if len(display_name) > 25:
                            display_name = display_name[:22] + "..."
                        formatted_models["openai"].append((display_name, model_id))
                    
                    # Format Gemini models with proper width constraints
                    for model_id in models["gemini"]:
                        # Create display name with proper formatting
                        display_name = model_id.replace("gemini-", "Gemini ").replace("-", " ").title()
                        # Limit display name length to prevent UI overflow
                        if len(display_name) > 25:
                            display_name = display_name[:22] + "..."
                        formatted_models["gemini"].append((display_name, model_id))
                    
                    # Format custom models if available
                    if "custom" in models:
                        for model_id in models["custom"]:
                            # Create display name with proper formatting
                            display_name = f"Custom: {model_id}"
                            # Limit display name length to prevent UI overflow
                            if len(display_name) > 25:
                                display_name = display_name[:22] + "..."
                            formatted_models["custom"].append((display_name, model_id))
                    
                    return formatted_models
                    
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not fetch models from APIs: {str(e)}[/]")
                    # Return fallback models with proper formatting
                    return {
                        "openai": [
                            ("GPT-4o", "gpt-4o"),
                            ("GPT-4 Turbo", "gpt-4-turbo"),
                            ("GPT-4", "gpt-4"),
                            ("GPT-3.5 Turbo", "gpt-3.5-turbo")
                        ],
                        "gemini": [
                            ("Gemini 1.5 Pro", "gemini-1.5-pro"),
                            ("Gemini 1.5 Flash", "gemini-1.5-flash"),
                            ("Gemini Pro", "gemini-pro")
                        ],
                        "custom": []
                    }
                    
        except Exception as e:
            self.console.print(f"[red]Error fetching models: {str(e)}[/]")
            # Return minimal fallback
            return {
                "openai": [("GPT-3.5 Turbo", "gpt-3.5-turbo")],
                "gemini": [("Gemini Pro", "gemini-pro")],
                "custom": []
            }

    def get_api_benchmark_config(self) -> Optional[Dict[str, Any]]:
        """Get configuration for API benchmark with dynamic model listing"""
        try:
            # Ask if user wants to use default configuration or customize
            mode_question = [
                inquirer.List(
                    'config_mode',
                    message="Choose configuration mode",
                    choices=[
                        ('Use default settings', 'default'),
                        ('Customize benchmark settings', 'advanced')
                    ],
                    default='advanced'
                )
            ]
            
            mode_answers = inquirer.prompt(mode_question)
            if not mode_answers:
                return None
            
            config_mode = mode_answers['config_mode']
            
            # Force model fetching to ensure we have the latest models
            self.console.print("[cyan]Fetching available models for benchmarking...[/]")
            models = asyncio.run(self._fetch_models_async())
            
            if not models or not models["openai"] or not models["gemini"]:
                self.console.print("[yellow]Warning: Could not fetch all required models.[/]")
                # Use fallback default models
                models = {
                    "openai": [
                        ("GPT-4o", "gpt-4o"),
                        ("GPT-4 Turbo", "gpt-4-turbo"),
                        ("GPT-4", "gpt-4"),
                        ("GPT-3.5 Turbo", "gpt-3.5-turbo")
                    ],
                    "gemini": [
                        ("Gemini 1.5 Pro", "gemini-1.5-pro"),
                        ("Gemini Pro", "gemini-pro"),
                        ("Gemini 1.5 Flash", "gemini-1.5-flash")
                    ]
                }
                self.console.print("[yellow]Using fallback model list.[/]")
            
            if config_mode == 'default':
                # Use default settings
                return {
                    'model_openai': 'gpt-3.5-turbo',  # Clean model names without provider prefix
                    'model_gemini': 'gemini-pro',     # Clean model names without provider prefix
                    'force_templates': False,
                    'num_prompts': 5,
                    'verbose': False,
                    'concurrency': 5  # Default to 5 concurrent requests
                }
            else:
                # Advanced configuration
                advanced_questions = []
                
                # OpenAI model selection
                advanced_questions.append(
                    inquirer.List(
                        'model_openai',
                        message="Select OpenAI model to test",
                        choices=[(name, model_id) for name, model_id in models["openai"]],
                        default='gpt-3.5-turbo' if any(m[1] == 'gpt-3.5-turbo' for m in models["openai"]) else None
                    )
                )
                
                # Gemini model selection
                advanced_questions.append(
                    inquirer.List(
                        'model_gemini',
                        message="Select Gemini model to test",
                        choices=[(name, model_id) for name, model_id in models["gemini"]],
                        default='gemini-pro' if any(m[1] == 'gemini-pro' for m in models["gemini"]) else None
                    )
                )
                
                # Prompt generation strategy
                advanced_questions.append(
                    inquirer.List(
                        'generation_method',
                        message="Prompt generation strategy",
                        choices=[
                            ('Dravik model with template guidance (recommended)', 'model'),
                            ('Use templates only (no model required)', 'templates')
                        ],
                        default='model'
                    )
                )
                
                # Number of prompts
                advanced_questions.append(
                    inquirer.List(
                        'num_prompts',
                        message="Number of prompts to test",
                        choices=[
                            ('Quick test (5 prompts)', 5),
                            ('Small benchmark (10 prompts)', 10),
                            ('Medium benchmark (20 prompts)', 20),
                            ('Large benchmark (50 prompts)', 50),
                            ('Comprehensive benchmark (100 prompts)', 100)
                        ]
                    )
                )
                
                # Concurrency
                advanced_questions.append(
                    inquirer.List(
                        'concurrency',
                        message="API request concurrency (higher = faster but may hit rate limits)",
                        choices=[
                            ('Low (3 concurrent requests)', 3),
                            ('Medium (5 concurrent requests)', 5),
                            ('High (10 concurrent requests)', 10)
                        ],
                        default=5
                    )
                )
                
                # Ask other questions
                advanced_answers = inquirer.prompt(advanced_questions)
                if not advanced_answers:
                    return None
                
                # Determine if we're forcing templates
                force_templates = advanced_answers['generation_method'] == 'templates'
                
                # Get OpenAI credentials if not already present
                if not os.environ.get("OPENAI_API_KEY"):
                    api_key_question = [
                        inquirer.Password(
                            'openai_api_key',
                            message="Enter your OpenAI API key (leave empty to skip OpenAI testing)",
                        )
                    ]
                    
                    api_key_answer = inquirer.prompt(api_key_question)
                    if api_key_answer and api_key_answer.get('openai_api_key'):
                        os.environ["OPENAI_API_KEY"] = api_key_answer['openai_api_key']
                        self.console.print("[green]OpenAI API key set.[/]")
                    else:
                        self.console.print("[yellow]No OpenAI API key provided. OpenAI models will be skipped.[/]")
                
                # Get Google API key if not already present
                if not os.environ.get("GOOGLE_API_KEY"):
                    api_key_question = [
                        inquirer.Password(
                            'google_api_key',
                            message="Enter your Google API key (leave empty to skip Gemini testing)",
                        )
                    ]
                    
                    api_key_answer = inquirer.prompt(api_key_question)
                    if api_key_answer and api_key_answer.get('google_api_key'):
                        api_key = api_key_answer.get('google_api_key', '').strip()
                        os.environ["GOOGLE_API_KEY"] = api_key
                        self.console.print("[green]Google API key set.[/]")
                        
                        # Store API key for future use using BenchmarkCommands storage
                        try:
                            from cli.commands.benchmark.command import BenchmarkCommands
                            benchmark_commands = BenchmarkCommands()
                            benchmark_commands._store_api_key("GOOGLE_API_KEY", api_key)
                        except Exception:
                            # Silently fail if we can't store the key
                            pass
                    else:
                        self.console.print("[yellow]No Google API key provided. Gemini models will be skipped.[/]")
                
                # Return the config
                return {
                    'model_openai': advanced_answers['model_openai'],  # Clean model name
                    'model_gemini': advanced_answers['model_gemini'],  # Clean model name
                    'force_templates': force_templates,
                    'num_prompts': advanced_answers['num_prompts'],
                    'verbose': False,  # Always set to False for now
                    'concurrency': advanced_answers['concurrency']
                }
        except Exception as e:
            self.console.print(f"[red]Error configuring benchmark: {str(e)}[/]")
            return None

    def get_flexible_benchmark_config(self) -> Optional[Dict[str, Any]]:
        """Get configuration for flexible benchmark"""
        try:
            self.console.print(Panel("[bold]Flexible Benchmark Configuration[/]", border_style="cyan"))
            
            # Get the benchmark domain
            domains = [
                ("General capabilities", "general"),
                ("Coding and programming", "coding"),
                ("Mathematical reasoning", "math"),
                ("Scientific understanding", "science"),
                ("Safety and alignment", "safety"),
                ("Custom domain", "custom")
            ]
            
            domain_q = [
                inquirer.List(
                    'domain',
                    message="Select benchmark domain",
                    choices=domains
                )
            ]
            
            domain_ans = inquirer.prompt(domain_q)
            if not domain_ans:
                return None
                
            domain = domain_ans['domain']
            
            # For custom domain, ask for benchmark name
            benchmark_name = None
            if domain == "custom":
                name_q = [
                    inquirer.Text(
                        'name',
                        message="Enter custom benchmark name",
                        validate=lambda _, x: x.strip() != ""
                    )
                ]
                name_ans = inquirer.prompt(name_q)
                if not name_ans:
                    return None
                    
                benchmark_name = name_ans['name']
            
            # Get target model
            model_q = [
                inquirer.Text(
                    'model',
                    message="Model to benchmark (HF repo ID or local path)",
                    default="karanxa/Dravik"
                )
            ]
            
            model_ans = inquirer.prompt(model_q)
            if not model_ans:
                return None
                
            target_model = model_ans['model']
            
            # Get evaluation models
            eval_models_choices = [
                ("OpenAI GPT-4", {"provider": "openai", "model": "gpt-4"}),
                ("OpenAI GPT-3.5 Turbo", {"provider": "openai", "model": "gpt-3.5-turbo"}),
                ("Google Gemini Pro", {"provider": "gemini", "model": "gemini-pro"}),
                ("None (self-evaluation only)", None)
            ]
            
            eval_q = [
                inquirer.Checkbox(
                    'eval_models',
                    message="Select evaluation models (space to select, enter to confirm)",
                    choices=eval_models_choices[:3]  # Exclude "None" option from multi-select
                )
            ]
            
            eval_ans = inquirer.prompt(eval_q)
            if not eval_ans:
                return None
                
            eval_models = eval_ans['eval_models']
            
            # Get number of examples
            examples_q = [
                inquirer.Text(
                    'max_examples',
                    message="Maximum number of examples to evaluate",
                    default="10",
                    validate=lambda _, x: x.isdigit() and 1 <= int(x) <= 100
                )
            ]
            
            examples_ans = inquirer.prompt(examples_q)
            if not examples_ans:
                return None
                
            max_examples = int(examples_ans['max_examples'])
            
            # Ask if user wants to use Kubernetes
            use_kubernetes = self.should_use_kubernetes()
            
            # Return complete config
            return {
                "domain": domain,
                "benchmark_name": benchmark_name,
                "target_model": target_model,
                "eval_models": eval_models,
                "max_examples": max_examples,
                "use_kubernetes": use_kubernetes
            }
            
        except Exception as e:
            self.console.print(f"[bold red]Error in flexible benchmark configuration: {str(e)}[/]")
            return None

    def get_internal_dataset_config(self) -> Optional[Dict[str, Any]]:
        """Get configuration for internal dataset benchmark"""
        try:
            # Skip dataset type selection and go directly to static templates
            dataset_type = "static"
            
            # Get model types and models to benchmark
            selected_models = self.get_model_types_for_benchmark()
            if not selected_models:
                self.console.print("[yellow]No models selected. Cancelling benchmark.[/]")
                return None
            
            # Ask for job type - usecase specific or generic
            self.console.print(Panel(
                "[bold cyan]Red Teaming Job Type[/]\n\n"
                "[bold green]Usecase-Specific:[/] Generate prompts tailored to your specific target model and use case.\n"
                "[bold yellow]Generic:[/] Generate standard adversarial prompts for general testing.\n",
                title="[blue]JOB TYPE SELECTION[/]",
                border_style="blue"
            ))
            
            job_type_question = [
                inquirer.List(
                    'job_type',
                    message="Select red teaming job type:",
                    choices=[
                        ('Usecase-Specific (AI-enhanced prompts)', 'usecase_specific'),
                        ('Generic (standard category prompts)', 'generic')
                    ],
                    default='usecase_specific'
                )
            ]
            
            job_type_answer = inquirer.prompt(job_type_question)
            if not job_type_answer:
                return None
            
            job_type = job_type_answer.get('job_type', 'usecase_specific')
            
            # Get other parameters
            params_questions = []
            # Always add prompt count since we're using static templates
            params_questions.append(
                inquirer.Text(
                    'prompt_count',
                    message="How many prompts to generate/use?",
                    default="10",
                    validate=lambda _, x: x.isdigit() and int(x) > 0
                )
            )
            params_questions.extend([
                inquirer.Text(
                    'concurrency',
                    message="Concurrency (number of simultaneous requests)",
                    default="3",
                    validate=lambda _, x: x.isdigit() and int(x) > 0 and int(x) <= 20
                ),
                inquirer.Text(
                    'max_tokens',
                    message="Maximum response tokens",
                    default="1000",
                    validate=lambda _, x: x.isdigit() and int(x) > 0
                ),
                inquirer.Text(
                    'max_retries',
                    message="Maximum retries for rate limits/errors (0-10)",
                    default="3",
                    validate=lambda _, x: x.isdigit() and 0 <= int(x) <= 10
                ),
                inquirer.Text(
                    'retry_delay',
                    message="Base retry delay in seconds (1-30)",
                    default="2",
                    validate=lambda _, x: x.replace('.', '', 1).isdigit() and 1 <= float(x) <= 30
                )
            ])
            # Only prompt for temperature if an Ollama model is selected
            has_ollama = any((isinstance(m, str) and m.startswith('ollama:')) or (isinstance(m, dict) and (m.get('provider') == 'ollama' or m.get('type') == 'ollama')) for m in selected_models)
            if has_ollama:
                params_questions.append(
                    inquirer.Text(
                        'temperature',
                        message="Temperature (0.0-1.0)",
                        default="0.7",
                        validate=lambda _, x: (x.replace('.', '', 1).isdigit() and float(x) >= 0 and float(x) <= 1)
                    )
                )
            
            params_answer = inquirer.prompt(params_questions)
            if not params_answer:
                return None
            
            config = {
                "dataset_type": dataset_type,
                "models": selected_models,
                "concurrency": int(params_answer['concurrency']),
                "max_tokens": int(params_answer['max_tokens']),
                "prompt_count": int(params_answer['prompt_count']),
                "job_type": job_type,  # Add job type to config
                "max_retries": int(params_answer['max_retries']),
                "retry_delay": float(params_answer['retry_delay'])
            }
            if has_ollama:
                config["temperature"] = float(params_answer['temperature'])
            # Always set Markov chain as the generation method without asking
            config["generation_method"] = 'markov'
            
            # Only ask for context and Gemini details if usecase-specific is selected
            if job_type == 'usecase_specific':
                # First ask about verbosity
                verbosity_option = [
                    inquirer.Confirm(
                        'verbose',
                        message="Show detailed generation progress?",
                        default=False
                    )
                ]
                
                verbosity_answer = inquirer.prompt(verbosity_option)
                if verbosity_answer:
                    config["verbose"] = verbosity_answer.get('verbose', False)
                
                # Ask about target model context
                self.console.print(Panel(
                    "[bold cyan]Target Model Context[/]\n\n"
                    "Providing context about the target model will help generate more specific red teaming prompts.\n"
                    "You can provide the system prompt, use case, or general description of the target model.",
                    title="[blue]CONTEXT COLLECTION[/]",
                    border_style="blue"
                ))
                
                # First ask if user wants to provide context
                context_option = [
                    inquirer.Confirm(
                        'provide_context',
                        message="Would you like to provide context about the target model?",
                        default=True
                    )
                ]
                
                context_answer = inquirer.prompt(context_option)
                if context_answer and context_answer.get('provide_context', True):
                    # Offer different types of context
                    context_type_option = [
                        inquirer.List(
                            'context_type',
                            message="What type of context would you like to provide?",
                            choices=[
                                ('System prompt', 'system_prompt'),
                                ('Use case description', 'use_case'),
                                ('Both', 'both')
                            ],
                            default='use_case'
                        )
                    ]
                    
                    context_type_answer = inquirer.prompt(context_type_option)
                    if context_type_answer:
                        context_type = context_type_answer.get('context_type', 'use_case')
                        
                        target_context = {}
                        
                        if context_type in ['system_prompt', 'both']:
                            self.console.print("\n[cyan]System Prompt Collection[/]")
                            system_prompt = self._get_multiline_input(
                                "Enter the system prompt of the target model:",
                                required=True
                            )
                            
                            if system_prompt:
                                target_context['system_prompt'] = system_prompt
                            else:
                                self.console.print("[yellow]System prompt is required when selected.[/]")
                                return None
                        
                        if context_type in ['use_case', 'both']:
                            use_case_question = [
                                inquirer.Text(
                                    'use_case',
                                    message="Describe the use case of the target model (e.g., 'e-commerce customer support'):",
                                    validate=lambda _, x: len(x.strip()) > 0
                                )
                            ]
                            
                            use_case_answer = inquirer.prompt(use_case_question)
                            if use_case_answer:
                                target_context['use_case'] = use_case_answer.get('use_case', '')
                        
                        # Additional optional details
                        self.console.print("\n[cyan]Additional Details (Optional)[/]")
                        additional_details = self._get_multiline_input(
                            "Any additional details about the target model:",
                            required=False
                        )
                        
                        if additional_details:
                            target_context['additional_details'] = additional_details
                        
                        # Add the collected context to the config
                        config["target_model_context"] = target_context
                        
                        # Summarize the provided context
                        self.console.print("\n[green]✓ Target model context collected[/]")
                        if 'system_prompt' in target_context:
                            self.console.print(f"[dim]System prompt: {target_context['system_prompt'][:50]}...[/]" if len(target_context['system_prompt']) > 50 else f"[dim]System prompt: {target_context['system_prompt']}[/]")
                        if 'use_case' in target_context:
                            self.console.print(f"[dim]Use case: {target_context['use_case']}[/]")
                
                # Removed model provider selection prompt
                # Always use Gemini as default provider for prompt validation
                provider = 'gemini'
                config["model_provider"] = provider
                
                # Always use Gemini 1.5 Flash as the default validation model without asking
                config["validation_model"] = 'gemini-1.5-flash'
                
                # Check for Gemini API key
                api_key = os.environ.get("GOOGLE_API_KEY")
                
                if not api_key:
                    self.console.print("[yellow]Warning: GOOGLE_API_KEY not found in environment variables[/]")
                    api_key_option = [
                        inquirer.Text(
                            'api_key',
                            message="Enter your Google API key:",
                            validate=lambda _, x: len(x.strip()) > 0
                        )
                    ]
                    
                    api_key_answer = inquirer.prompt(api_key_option)
                    if api_key_answer:
                        api_key = api_key_answer.get('api_key', '').strip()
                        os.environ["GOOGLE_API_KEY"] = api_key
                        config["google_api_key"] = api_key
                        
                        # Store API key for future use using BenchmarkCommands storage
                        try:
                            from cli.commands.benchmark.command import BenchmarkCommands
                            benchmark_commands = BenchmarkCommands()
                            benchmark_commands._store_api_key("GOOGLE_API_KEY", api_key)
                        except Exception:
                            # Silently fail if we can't store the key
                            pass
            else:
                # For generic jobs, set basic defaults without requiring context or API keys
                config["verbose"] = False
                config["model_provider"] = 'gemini'  # Set for consistency but won't be used
                config["validation_model"] = 'gemini-1.5-flash'  # Set for consistency but won't be used
                
                self.console.print("[green]✓ Generic job configured - no AI enhancement will be used[/]")
            
            return config
            
        except Exception as e:
            self.console.print(f"[bold red]Error getting configuration: {str(e)}[/]")
            import traceback
            traceback.print_exc()
            return None

    def get_external_dataset_config(self) -> Optional[Dict[str, Any]]:
        """Get a simplified configuration for external dataset benchmarking.
        Only asks for models and concurrency."""
        config = {}
        
        # Select models
        models = self._get_models_for_benchmark()
        if not models:
            return None
        config["models"] = models
        
        # Set concurrency
        concurrency = self._get_concurrency()
        if concurrency is None:
            return None
        config["concurrency"] = concurrency
        
        # Set basic defaults needed for benchmarks
        config["max_tokens"] = 4096  # Reasonable default
        config["temperature"] = 0.0  # Zero for deterministic outputs
        config["requests_per_minute"] = 0  # No rate limiting by default
        
        return config

    def _get_models_for_benchmark(self):
        """Get models for benchmarking from the user with multi-select and API key management."""
        # Fetch available models
        import asyncio
        models = asyncio.run(self._fetch_models_async())
        
        # Display available models in a compact table format
        self.console.print("\n[bold cyan]Available Models:[/]")
        
        # Create a compact table showing available models
        model_table = Table(show_header=True, header_style="bold cyan", box=None, width=80)
        model_table.add_column("Provider", style="cyan", width=12)
        model_table.add_column("Available Models", style="green", width=65)
        
        # Format model lists for display
        if models.get("openai"):
            openai_list = ", ".join([name for name, _ in models["openai"][:4]])  # Show first 4
            if len(models["openai"]) > 4:
                openai_list += f" (+{len(models['openai'])-4} more)"
            model_table.add_row("OpenAI", openai_list)
        
        if models.get("gemini"):
            gemini_list = ", ".join([name for name, _ in models["gemini"][:4]])  # Show first 4
            if len(models["gemini"]) > 4:
                gemini_list += f" (+{len(models['gemini'])-4} more)"
            model_table.add_row("Gemini", gemini_list)
        
        if models.get("custom"):
            custom_list = ", ".join([name for name, _ in models["custom"][:3]])  # Show first 3
            if len(models["custom"]) > 3:
                custom_list += f" (+{len(models['custom'])-3} more)"
            model_table.add_row("Custom", custom_list)
        
        self.console.print(model_table)
        
        # Only prompt for providers the user actually wants to use
        selected_openai_models, openai_api_keys = [], [""]
        selected_gemini_models, gemini_api_keys = [], [""]
        selected_custom_models = []
        
        # Ask which providers to use with improved formatting
        provider_choices = []
        if models.get("openai"): 
            provider_choices.append(f"OpenAI ({len(models['openai'])} models)")
        if models.get("gemini"): 
            provider_choices.append(f"Gemini ({len(models['gemini'])} models)")
        if models.get("custom"): 
            provider_choices.append(f"Custom ({len(models['custom'])} models)")
        
        if not provider_choices:
            self.console.print("[red]No models available for benchmarking.[/]")
            return None
            
        provider_question = [
            inquirer.Checkbox(
                'providers',
                message="Select providers to use (space to select, enter to confirm)",
                choices=provider_choices
            )
        ]
        provider_answer = inquirer.prompt(provider_question)
        if not provider_answer or not provider_answer["providers"]:
            return None
        selected_providers = provider_answer["providers"]
        
        # Only show model selection for selected providers
        if any("OpenAI" in p for p in selected_providers):
            self.console.print("\n[bold cyan]OpenAI Model Selection:[/]")
            # Create more compact choices for OpenAI models
            openai_choices = []
            for name, model_id in models["openai"]:
                # Create compact display format
                choice_text = f"{name:<20} ({model_id})"
                if len(choice_text) > 50:
                    choice_text = choice_text[:47] + "..."
                openai_choices.append((choice_text, model_id))
            
            openai_model_question = [
                inquirer.Checkbox(
                    'models_openai',
                    message="Select OpenAI models",
                    choices=openai_choices,
                    default=['gpt-3.5-turbo'] if any(m[1] == 'gpt-3.5-turbo' for m in models["openai"]) else None
                )
            ]
            openai_model_answer = inquirer.prompt(openai_model_question)
            if not openai_model_answer:
                return None
            selected_openai_models = openai_model_answer["models_openai"]
            
            # If more than one OpenAI model selected, ask for additional API keys
            if len(selected_openai_models) > 1:
                add_keys_question = [
                    inquirer.Confirm(
                        'add_keys',
                        message=f"You selected {len(selected_openai_models)} OpenAI models. Add extra API keys for rate limits?",
                        default=True
                    )
                ]
                add_keys_answer = inquirer.prompt(add_keys_question)
                if add_keys_answer and add_keys_answer['add_keys']:
                    for i in range(1, min(len(selected_openai_models), 4)):  # Limit to 4 keys max
                        key_question = [
                            inquirer.Password(
                                f'api_key_{i}',
                                message=f"Additional OpenAI API key #{i} (optional):",
                            )
                        ]
                        key_answer = inquirer.prompt(key_question)
                        if key_answer and key_answer[f'api_key_{i}']:
                            openai_api_keys.append(key_answer[f'api_key_{i}'])
        
        if any("Gemini" in p for p in selected_providers):
            self.console.print("\n[bold cyan]Gemini Model Selection:[/]")
            # Create more compact choices for Gemini models
            gemini_choices = []
            for name, model_id in models["gemini"]:
                # Create compact display format
                choice_text = f"{name:<20} ({model_id})"
                if len(choice_text) > 50:
                    choice_text = choice_text[:47] + "..."
                gemini_choices.append((choice_text, model_id))
            
            gemini_model_question = [
                inquirer.Checkbox(
                    'models_gemini',
                    message="Select Gemini models",
                    choices=gemini_choices,
                    default=['gemini-1.5-pro'] if any(m[1] == 'gemini-1.5-pro' for m in models["gemini"]) else None
                )
            ]
            gemini_model_answer = inquirer.prompt(gemini_model_question)
            if not gemini_model_answer:
                return None
            selected_gemini_models = gemini_model_answer["models_gemini"]
            
            if len(selected_gemini_models) > 1:
                add_keys_question = [
                    inquirer.Confirm(
                        'add_keys',
                        message=f"You selected {len(selected_gemini_models)} Gemini models. Add extra API keys for rate limits?",
                        default=True
                    )
                ]
                add_keys_answer = inquirer.prompt(add_keys_question)
                if add_keys_answer and add_keys_answer['add_keys']:
                    for i in range(1, min(len(selected_gemini_models), 4)):  # Limit to 4 keys max
                        key_question = [
                            inquirer.Password(
                                f'api_key_{i}',
                                message=f"Additional Google API key #{i} (optional):",
                            )
                        ]
                        key_answer = inquirer.prompt(key_question)
                        if key_answer and key_answer[f'api_key_{i}']:
                            gemini_api_keys.append(key_answer[f'api_key_{i}'])
        
        if any("Custom" in p for p in selected_providers) and "custom" in models and models["custom"]:
            self.console.print("\n[bold cyan]Custom Model Selection:[/]")
            # Create more compact choices for custom models
            custom_choices = []
            for name, model_id in models["custom"]:
                # Create compact display format
                choice_text = f"{name:<20} ({model_id})"
                if len(choice_text) > 50:
                    choice_text = choice_text[:47] + "..."
                custom_choices.append((choice_text, model_id))
            
            custom_model_question = [
                inquirer.Checkbox(
                    'models_custom',
                    message="Select Custom models",
                    choices=custom_choices
                )
            ]
            custom_model_answer = inquirer.prompt(custom_model_question)
            if custom_model_answer:
                selected_custom_models = custom_model_answer["models_custom"]
                if selected_custom_models:
                    self.console.print(f"[green]Selected {len(selected_custom_models)} custom models[/]")
        
        # Create the list of selected models with additional information
        model_list = []
        
        # Add OpenAI models
        for i, model_id in enumerate(selected_openai_models):
            # Use the appropriate API key if available, otherwise use the default (empty string)
            api_key = openai_api_keys[i] if i < len(openai_api_keys) else ""
            
            model_list.append({
                "provider": "openai",
                "id": model_id,
                "api_key": api_key
            })
        
        # Add Gemini models
        for i, model_id in enumerate(selected_gemini_models):
            # Use the appropriate API key if available, otherwise use the default (empty string)
            api_key = gemini_api_keys[i] if i < len(gemini_api_keys) else ""
            
            model_list.append({
                "provider": "gemini",
                "id": model_id,
                "api_key": api_key
            })
            
        # Add Custom models and Guardrails
        for model_id in selected_custom_models:
            # Check if it's a guardrail or custom model
            if model_id.startswith("guardrail:"):
                # It's a guardrail
                guardrail_name = model_id.replace("guardrail:", "")
                model_list.append({
                    "provider": "guardrail",
                    "id": model_id,  # Keep the full guardrail:name format
                    "type": "guardrail",
                    "name": guardrail_name
                })
            elif model_id.startswith("custom:"):
                # It's a custom model
                actual_model_id = model_id.replace("custom:", "")
                try:
                    from benchmarks.models.model_loader import ModelLoader
                    model_loader = ModelLoader(verbose=False)
                    config = model_loader.get_custom_model_config(actual_model_id)
                    
                    # Check model type
                    model_type = config.get("type", "").lower() if config else ""
                    
                    model_list.append({
                        "provider": "custom",
                        "id": actual_model_id,
                        "type": model_type,
                        "config": config
                    })
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not load config for custom model {actual_model_id}: {str(e)}[/]")
                    # Add with minimal info
                    model_list.append({
                        "provider": "custom",
                        "id": actual_model_id,
                        "type": "unknown"
                    })
            else:
                # Legacy format - assume it's a custom model
                try:
                    from benchmarks.models.model_loader import ModelLoader
                    model_loader = ModelLoader(verbose=False)
                    config = model_loader.get_custom_model_config(model_id)
                    
                    # Check model type
                    model_type = config.get("type", "").lower() if config else ""
                    
                    model_list.append({
                        "provider": "custom",
                        "id": model_id,
                        "type": model_type,
                        "config": config
                    })
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not load config for custom model {model_id}: {str(e)}[/]")
                    # Add with minimal info
                    model_list.append({
                        "provider": "custom",
                        "id": model_id,
                        "type": "unknown"
                    })
        
        if not model_list:
            self.console.print("[yellow]No models selected.[/]")
            return None
        
        # Display summary of selected models
        self.console.print(f"\n[green]Selected {len(model_list)} models for benchmarking:[/]")
        for model in model_list:
            provider = model["provider"].capitalize()
            model_id = model["id"]
            self.console.print(f"  • [cyan]{provider}:[/] {model_id}")
        
        return model_list
    
    def _get_concurrency(self):
        """Get concurrency level from user."""
        concurrency_question = [
            inquirer.List(
                'concurrency',
                message="Concurrency level (parallel requests)",
                choices=[
                    ('Low (1) - Sequential processing', 1),
                    ('Medium (3) - Balanced', 3),
                    ('High (5) - Fast but may trigger rate limits', 5),
                    ('Very High (10) - Use with caution, rate limits likely', 10)
                ],
                default=3
            )
        ]
        
        concurrency_answer = inquirer.prompt(concurrency_question)
        if not concurrency_answer:
            return None
        
        return concurrency_answer['concurrency']

    def get_model_types_for_benchmark(self):
        """Get the types of models to benchmark from the user."""
        console = Console()
        console.print("\n[bold cyan]Select which types of models to benchmark:[/]\n")
        
        model_types = {
            "1": "Ollama",
            "2": "OpenAI",
            "3": "Gemini",
            "4": "Custom",
            "5": "All"
        }
        
        # Display options
        for key, value in model_types.items():
            console.print(f"{key}. {value}")
        
        # Get user selection
        while True:
            choice = Prompt.ask("\nEnter your choice (1-5)", default="5")
            if choice in model_types:
                break
            console.print("[red]Invalid choice. Please enter a number between 1 and 5.[/]")
        
        selected_type = model_types[choice]
        
        # Initialize lists for each model type
        selected_models = []
        
        if selected_type == "All" or selected_type == "Ollama":
            # Get available Ollama models
            try:
                from benchmarks.models.handlers.ollama_handler import OllamaHandler
                handler = OllamaHandler(verbose=False)
                ollama_models = asyncio.run(handler.list_models())
                if ollama_models:
                    console.print("\n[cyan]Available Ollama models:[/]")
                    # Use checkboxes for multi-selection
                    if len(ollama_models) > 0:
                        ollama_choices = [
                            (model["name"], model["name"]) for model in ollama_models
                        ]
                        ollama_question = [
                            inquirer.Checkbox(
                                'ollama_models',
                                message="Select Ollama models (space to select/deselect, enter to confirm)",
                                choices=ollama_choices,
                                default=[model["name"] for model in ollama_models]  # Default all selected
                            )
                        ]
                        
                        ollama_answer = inquirer.prompt(ollama_question)
                        if ollama_answer and ollama_answer['ollama_models']:
                            for model in ollama_answer['ollama_models']:
                                selected_models.append(f"ollama:{model}")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch Ollama models: {str(e)}[/]")
        
        if selected_type == "All" or selected_type == "OpenAI":
            # Fetch available OpenAI models from API
            try:
                from benchmarks.api.openai_handler import OpenAIHandler
                console.print("\n[cyan]Fetching OpenAI models...[/]")
                openai_models = asyncio.run(OpenAIHandler.list_available_models())
                if not openai_models:
                    # Fallback to defaults
                    openai_models = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
                    
                console.print("\n[cyan]Available OpenAI models:[/]")
                
                # Format display names for better readability
                openai_choices = []
                for model in openai_models:
                    display_name = model.replace("gpt-", "GPT-").replace("-turbo", " Turbo")
                    openai_choices.append((display_name, model))
                
                # Use checkboxes for multi-selection
                openai_question = [
                    inquirer.Checkbox(
                        'openai_models',
                        message="Select OpenAI models (space to select/deselect, enter to confirm)",
                        choices=openai_choices,
                        default=["gpt-3.5-turbo", "gpt-4"]  # Common defaults
                    )
                ]
                
                openai_answer = inquirer.prompt(openai_question)
                if openai_answer and openai_answer['openai_models']:
                    for model in openai_answer['openai_models']:
                        selected_models.append(model)  # Don't add prefix, use clean model name
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch OpenAI models: {str(e)}[/]")
                # Fallback to defaults
                openai_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
                console.print("\n[cyan]Available OpenAI models (fallback):[/]")
                
                # Use checkboxes for fallback models too
                openai_choices = [(model.replace("gpt-", "GPT-").replace("-turbo", " Turbo"), model) for model in openai_models]
                openai_question = [
                    inquirer.Checkbox(
                        'openai_models',
                        message="Select OpenAI models (space to select/deselect, enter to confirm)",
                        choices=openai_choices,
                        default=["gpt-3.5-turbo"]  # Default selection
                    )
                ]
                
                openai_answer = inquirer.prompt(openai_question)
                if openai_answer and openai_answer['openai_models']:
                    for model in openai_answer['openai_models']:
                        selected_models.append(model)
        
        if selected_type == "All" or selected_type == "Gemini":
            # Fetch available Gemini models from API
            try:
                from benchmarks.api.gemini_handler import GeminiHandler
                console.print("\n[cyan]Fetching Gemini models...[/]")
                gemini_models = GeminiHandler.list_available_models()
                if not gemini_models:
                    # Fallback to defaults
                    gemini_models = ["gemini-1.5-pro", "gemini-pro", "gemini-1.5-flash"]
                    
                console.print("\n[cyan]Available Gemini models:[/]")
                
                # Format display names for better readability
                gemini_choices = []
                for model in gemini_models:
                    display_name = model.replace("gemini-", "Gemini ").replace("-", " ").title()
                    gemini_choices.append((display_name, model))
                
                # Use checkboxes for multi-selection
                gemini_question = [
                    inquirer.Checkbox(
                        'gemini_models',
                        message="Select Gemini models (space to select/deselect, enter to confirm)",
                        choices=gemini_choices,
                        default=["gemini-pro"]  # Common default
                    )
                ]
                
                gemini_answer = inquirer.prompt(gemini_question)
                if gemini_answer and gemini_answer['gemini_models']:
                    for model in gemini_answer['gemini_models']:
                        selected_models.append(model)  # Don't add prefix, use clean model name
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch Gemini models: {str(e)}[/]")
                # Fallback to defaults
                gemini_models = ["gemini-pro", "gemini-1.5-pro"]
                console.print("\n[cyan]Available Gemini models (fallback):[/]")
                
                # Use checkboxes for fallback models too
                gemini_choices = [(model.replace("gemini-", "Gemini ").replace("-", " ").title(), model) for model in gemini_models]
                gemini_question = [
                    inquirer.Checkbox(
                        'gemini_models',
                        message="Select Gemini models (space to select/deselect, enter to confirm)",
                        choices=gemini_choices,
                        default=["gemini-pro"]  # Default selection
                    )
                ]
                
                gemini_answer = inquirer.prompt(gemini_question)
                if gemini_answer and gemini_answer['gemini_models']:
                    for model in gemini_answer['gemini_models']:
                        selected_models.append(model)
        
        if selected_type == "All" or selected_type == "Custom":
            # Get custom models from model loader
            try:
                from benchmarks.models.model_loader import ModelLoader
                from benchmarks.models.handlers.guardrail_handler import GuardrailHandler
                
                model_loader = ModelLoader(verbose=False)
                custom_models = model_loader.list_custom_models()
                
                # Get available guardrails
                available_guardrails = GuardrailHandler.list_available_guardrails()
                
                # Combine custom models and guardrails
                all_custom_choices = []
                
                # Add custom models
                if custom_models:
                    for model in custom_models:
                        try:
                            config = model_loader.get_custom_model_config(model)
                            model_type = config.get("type", "unknown")
                            display_name = f"{model} (custom-api)"
                            all_custom_choices.append((display_name, f"custom:{model}"))
                        except:
                            all_custom_choices.append((f"{model} (custom-api)", f"custom:{model}"))
                
                # Add guardrails
                if available_guardrails:
                    for guardrail in available_guardrails:
                        display_name = f"{guardrail} (guardrail)"
                        all_custom_choices.append((display_name, f"guardrail:{guardrail}"))
                
                if all_custom_choices:
                    console.print("\n[cyan]Available Custom models and Guardrails:[/]")
                    
                    # Use checkboxes for multi-selection
                    custom_question = [
                        inquirer.Checkbox(
                            'custom_models',
                            message="Select Custom models and Guardrails (space to select/deselect, enter to confirm)",
                            choices=all_custom_choices
                        )
                    ]
                    
                    custom_answer = inquirer.prompt(custom_question)
                    if custom_answer and custom_answer['custom_models']:
                        for model in custom_answer['custom_models']:
                            selected_models.append(model)
                else:
                    console.print("[yellow]No custom models or guardrails found.[/]")
            except Exception as e:
                console.print(f"[yellow]Error loading custom models and guardrails: {str(e)}[/]")
        
        # Show summary of selected models
        if selected_models:
            console.print(f"\n[green]Selected {len(selected_models)} models for benchmarking:[/]")
            for model in selected_models:
                console.print(f"  • [cyan]{model}[/]")
        else:
            console.print("[yellow]No models selected. Please run the command again and select at least one model.[/]")
        
        return selected_models

    def get_benchmark_config(self):
        """Get benchmark configuration including model selection."""
        # First get the model types and models to benchmark
        selected_models = self.get_model_types_for_benchmark()
        if not selected_models:
            return None
        
        # Get other benchmark parameters
        from rich.prompt import IntPrompt
        concurrency = IntPrompt.ask("Enter concurrency level (1-10)", default=3)
        max_tokens = IntPrompt.ask("Enter max tokens per response", default=1000)
        temperature = float(IntPrompt.ask("Enter temperature (0-100)", default=70)) / 100
        
        return {
            "models": selected_models,
            "concurrency": max(1, min(10, concurrency)),
            "max_tokens": max_tokens,
            "temperature": temperature
        }

    def select_option(self, message, options, default=0):
        """Select an option from a list of options.
        
        Args:
            message: The message to display to the user
            options: List of options to choose from
            default: Default option index
            
        Returns:
            The selected option
        """
        if not options:
            self.console.print("[yellow]No options available.[/]")
            return None
            
        # Create list for inquirer
        choices = [(option, option) for option in options]
        
        # Use inquirer to select an option
        question = [
            inquirer.List(
                'option',
                message=message,
                choices=choices,
                default=options[default] if default < len(options) else options[0]
            )
        ]
        
        answer = inquirer.prompt(question)
        return answer['option'] if answer else None
        
    def text_prompt(self, message, default=None, required=False, help_text=None):
        """Prompt the user for text input.
        
        Args:
            message: The message to display to the user
            default: Default value if user enters nothing
            required: Whether the input is required
            help_text: Help text to display to the user
            
        Returns:
            The user's input
        """
        # Show help text if provided
        if help_text:
            self.console.print(f"[dim]{help_text}[/]")
            
        # Create validation function if required
        validate = lambda answers, val: bool(val.strip()) if required else True
        
        # Use inquirer to prompt for text
        question = [
            inquirer.Text(
                'text',
                message=message,
                default=default,
                validate=validate
            )
        ]
        
        answer = inquirer.prompt(question)
        return answer['text'] if answer else default

    def _get_multiline_input(self, prompt_message: str, required: bool = True) -> str:
        """Get multi-line input from the user.
        
        Args:
            prompt_message: The prompt message to display
            required: Whether input is required
            
        Returns:
            The multi-line input as a string
        """
        self.console.print(f"\n[bold cyan]{prompt_message}[/]")
        self.console.print("[dim]Enter your text. Press Enter twice when done, or Ctrl+D to finish.[/dim]")
        self.console.print("[dim]For multi-line system prompts, paste your content and press Enter twice.[/dim]")
        
        lines = []
        empty_line_count = 0
        
        try:
            while True:
                try:
                    line = input()
                    if not line.strip():
                        empty_line_count += 1
                        if empty_line_count >= 2:  # Two empty lines = done
                            break
                        lines.append(line)  # Preserve empty lines within the text
                        continue
                    else:
                        empty_line_count = 0
                        lines.append(line)
                except EOFError:  # Ctrl+D pressed
                    break
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Input cancelled.[/]")
            return ""
        
        if not lines and required:
            self.console.print("[yellow]No input provided.[/]")
            return ""
            
        # Join lines and preserve formatting
        result = "\n".join(lines).strip()
        return result
