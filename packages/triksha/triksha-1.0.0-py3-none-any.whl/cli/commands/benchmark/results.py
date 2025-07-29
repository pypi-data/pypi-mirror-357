"""Result viewing and export functionality for benchmarks"""
import json
import os
import csv
import copy  # Added for deep copying objects
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box
from pathlib import Path
import inquirer
from typing import Dict, Any, List, Optional
import uuid  # For generating IDs if needed

class ResultsViewer:
    """Viewer for benchmark results"""
    
    def __init__(self, db, console: Console, verbose: bool = False):
        """Initialize the results viewer"""
        self.db = db
        self.console = console
        self.exports_dir = Path.home() / "dravik" / "benchmark_exports"
        self.verbose = verbose
        
        # Create export directory if it doesn't exist
        self.exports_dir.mkdir(exist_ok=True, parents=True)
    
    def list_all_results(self, limit: int = None, include_large_benchmarks: bool = True) -> List[Dict]:
        """List all available benchmark results from the database
        
        Args:
            limit: Maximum number of results to display (None for all)
            include_large_benchmarks: Whether to ensure large benchmarks are included
            
        Returns:
            List of result data dictionaries
        """
        # Get processed results data
        results_data = self._get_results_data()
        
        if not results_data:
            self.console.print(Panel(
                "[yellow]No benchmark results found in database.[/]\n\n"
                "To run a benchmark:\n"
                "1. Use the 'benchmark' command\n"
                "2. Select the type of benchmark to run\n"
                "3. Configure the benchmark settings\n"
                "4. Results will be saved automatically",
                title="[red]No Results Found[/]",
                border_style="red"
            ))
            return []
        
        # Create a table to display results
        table = Table(title="Available Benchmark Results", box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Timestamp", style="green")
        table.add_column("Model Tested", style="yellow")
        table.add_column("Total Prompts", style="magenta")
        table.add_column("Success Rate", style="blue")
        table.add_column("Status", style="cyan")
        
        # Add the rest of the results, respecting the limit
        displayed_count = 0
        for result in results_data:
            if limit and displayed_count >= limit:
                break
                
            # Highlight large benchmarks
            if result['total_prompts'] >= 100:
                table.add_row(
                    str(result['id']),
                    f"[bold]{result['formatted_timestamp']}[/]", 
                    result['model_tested'], 
                    f"[bold bright_magenta]{result['total_prompts']}[/]",
                    result['success_rate'],
                    result['status']
                )
            else:
                table.add_row(
                    str(result['id']),
                    result['formatted_timestamp'], 
                    result['model_tested'], 
                    str(result['total_prompts']),
                    result['success_rate'],
                    result['status']
                )
            displayed_count += 1
        
        self.console.print(table)
        
        return results_data

    def find_large_benchmark(self, min_prompts: int = 500) -> Optional[Dict[str, Any]]:
        """Find and display a specific large benchmark from the database
        
        Args:
            min_prompts: Minimum number of prompts to qualify as "large"
            
        Returns:
            The benchmark data dictionary or None if not found
        """
        self.console.print(f"[blue]Searching for benchmarks with {min_prompts}+ prompts...[/]")
        
        # Get all benchmark results from the database
        db_results = self.db.get_benchmark_results()
        if not db_results:
            self.console.print("[yellow]No benchmark results found in database.[/]")
            return None
        
        # Locate large benchmarks
        large_benchmarks = []
        for data in db_results:
            try:
                total_prompts = data.get('total_prompts', 0)
                if total_prompts >= min_prompts:
                    timestamp = data.get('timestamp', 'Unknown')
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_timestamp = timestamp
                    
                    large_benchmarks.append({
                        'benchmark_id': data.get('benchmark_id', 'unknown'),
                        'timestamp': timestamp,
                        'formatted_timestamp': formatted_timestamp,
                        'total_prompts': total_prompts,
                        'data': data
                    })
            except Exception as e:
                self.console.print(f"[yellow]Error processing benchmark: {e}[/]")
        
        if not large_benchmarks:
            self.console.print(f"[yellow]No benchmarks with {min_prompts}+ prompts found.[/]")
            return None
        
        # Sort by size, then by recency
        large_benchmarks.sort(key=lambda x: (x['total_prompts'], x['timestamp']), reverse=True)
        
        # Display all large benchmarks
        table = Table(title=f"Large Benchmarks ({min_prompts}+ prompts)", box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Timestamp", style="green")
        table.add_column("Prompts", style="magenta")
        table.add_column("Success Rate", style="blue")
        table.add_column("Benchmark ID", style="dim")
        
        for i, benchmark in enumerate(large_benchmarks):
            # Calculate success rate
            bypass_success = benchmark['data'].get('bypass_success', {})
            providers = ['openai', 'gemini', 'custom']
            success_values = [bypass_success.get(provider, 0) for provider in providers if provider in bypass_success]
            avg_success = sum(success_values) / len(success_values) if success_values else 0
            total_prompts = benchmark['total_prompts']
            success_rate = f"{avg_success / total_prompts * 100:.1f}%" if total_prompts > 0 else "N/A"
            
            # Add to table
            table.add_row(
                str(i+1),
                benchmark['formatted_timestamp'],
                str(benchmark['total_prompts']),
                success_rate,
                str(benchmark['benchmark_id'])
            )
        
        self.console.print(table)
        
        # Let user select which one to view
        if len(large_benchmarks) > 1:
            choice = inquirer.prompt([
                inquirer.List(
                    'benchmark',
                    message="Select which benchmark to view",
                    choices=[(f"{b['formatted_timestamp']} ({b['total_prompts']} prompts)", i) 
                             for i, b in enumerate(large_benchmarks)]
                )
            ])
            
            if not choice:
                return None
            
            selected = large_benchmarks[choice['benchmark']]
        else:
            selected = large_benchmarks[0]
        
        self.console.print(f"[green]Selected benchmark from {selected['formatted_timestamp']} with {selected['total_prompts']} prompts[/]")
        return selected['data']
    
    def view_results(self):
        """View and analyze benchmark results from the database with interactive selection"""
        # Get all available benchmark results from the database
        results_data = self._get_results_data()
        
        if not results_data:
            self.console.print("[yellow]No benchmark results found in database to display[/]")
            return
        
        # Create and display the table
        table = Table(title="Available Benchmark Results", box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Timestamp", style="green")
        table.add_column("Model Tested", style="yellow")
        table.add_column("Total Prompts", style="magenta")
        table.add_column("Success Rate", style="blue")
        table.add_column("Status", style="cyan")
        
        # Add rows to table and create choices for selection
        choices = []
        for result in results_data:
            # Add row to table
            table.add_row(
                str(result['id']),
                result['formatted_timestamp'], 
                result['model_tested'], 
                str(result['total_prompts']),
                result['success_rate'],
                result['status']
            )
            
            # Create choice for selection
            choice_text = f"{result['formatted_timestamp']} - {result['model_tested']} ({result['total_prompts']} prompts)"
            choices.append((choice_text, result))
        
        choices.append(("Return to main menu", None))
        
        # Display the table
        self.console.print(table)
        
        # Now make the table selectable
        questions = [
            inquirer.List(
                'result',
                message="Select a benchmark result to view",
                choices=choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or answers['result'] is None:
            return
        
        selected = answers['result']
        
        # Now we have the selected result, let's display it
        self.console.print(f"\n[bold green]Viewing benchmark from {selected['formatted_timestamp']}[/]")
        self.console.print(f"[cyan]Model: {selected['model_tested']} | Total prompts: {selected['total_prompts']}[/]")
        
        # Check if the data has a models_tested structure
        selected_data = selected['data']
        
        # Check and fix the examples data if needed
        if 'models_tested' in selected_data and not selected_data.get('examples', []):
            # Try to find the BenchmarkCommands instance if available
            try:
                from cli.commands.benchmark.command import BenchmarkCommands
                # Create instance and extract prompts
                try:
                    benchmark_commands = BenchmarkCommands()
                except Exception as init_error:
                    # Try alternative initialization with minimum required parameters
                    try:
                        from rich.console import Console
                        benchmark_commands = BenchmarkCommands(console=self.console)
                    except Exception:
                        # Last resort, create a minimal object with just the function we need
                        class MinimalCommands:
                            def __init__(self, console):
                                self.console = console
                                
                            def _extract_prompts_from_api_benchmark(self, results):
                                self.console.print("[blue]Extracting prompts manually...[/]")
                                prompts = []
                                models = results.get('models_tested', [])
                                
                                for model in models:
                                    model_name = model.get('model', 'Unknown')
                                    examples = model.get('examples', [])
                                    
                                    for example in examples:
                                        prompt_text = example.get('prompt', '')
                                        if isinstance(prompt_text, dict) and 'text' in prompt_text:
                                            prompt_text = prompt_text['text']
                                            
                                        if prompt_text:
                                            prompts.append({
                                                'prompt': prompt_text,
                                                'responses': [{
                                                    'model': model_name,
                                                    'success': example.get('success', False),
                                                    'response': example.get('response', 'No response')
                                                }]
                                            })
                                
                                results['examples'] = prompts
                                self.console.print(f"[green]Extracted {len(prompts)} prompts[/]")
                                return prompts
                        
                        benchmark_commands = MinimalCommands(self.console)
                
                benchmark_commands.console = self.console  # Share console
                benchmark_commands._extract_prompts_from_api_benchmark(selected_data)
                self.console.print("[green]Successfully extracted prompts from models_tested structure[/]")
            except Exception as e:
                self.console.print(f"[yellow]Error extracting prompts: {str(e)}[/]")
                
                # Alternative approach if the import fails
                if 'models_tested' in selected_data:
                    # Manual extraction (simplified version)
                    prompts = []
                    models = selected_data.get('models_tested', [])
                    
                    for model in models:
                        model_name = model.get('model', 'Unknown')
                        examples = model.get('examples', [])
                        
                        for example in examples:
                            prompt_text = example.get('prompt', '')
                            if isinstance(prompt_text, dict) and 'text' in prompt_text:
                                prompt_text = prompt_text['text']
                                
                            if prompt_text:
                                # Simple approach: create a standalone example for each model/prompt combo
                                prompts.append({
                                    'prompt': prompt_text,
                                    'responses': [{
                                        'model': model_name,
                                        'success': example.get('success', False),
                                        'response': example.get('response', 'No response'),
                                        'response_time': example.get('response_time', 0)
                                    }]
                                })
                    
                    if prompts:
                        selected_data['examples'] = prompts
                        self.console.print(f"[green]Manually extracted {len(prompts)} examples[/]")
        
        # Use our existing method to display the API results
        self.display_api_results(selected_data)
        
        # After displaying, provide additional options
        while True:
            options = [
                ('View details of specific prompts', 'details'),
                ('Export this benchmark', 'export'),
                ('Return to results list', 'list'),
                ('Return to main menu', 'exit')
            ]
            
            action = inquirer.prompt([
                inquirer.List(
                    'action',
                    message="What would you like to do next?",
                    choices=options
                )
            ])
            
            if not action or action['action'] == 'exit':
                break
            elif action['action'] == 'list':
                # Show the list again and restart the selection process
                return self.view_results()
            elif action['action'] == 'details':
                # Show detailed information for specific examples/prompts
                self._display_api_example_details(selected_data)
            elif action['action'] == 'export':
                # Export the current benchmark data
                self._export_current_benchmark(selected_data)
        
        return

    def _get_results_data(self) -> List[Dict]:
        """Get processed results data without displaying the table"""
        # Get results from the database
        db_results = self.db.get_benchmark_results()
        
        if not db_results:
            return []
        
        # Sort by timestamp (newest first)
        db_results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Process results for display
        results_data = []
        large_benchmarks = []
        failed_entries = []
        
        for i, data in enumerate(db_results):
            try:
                # Extract key information (same logic as before)
                timestamp = data.get('timestamp', 'Unknown')
                
                # Get model_tested from different possible sources
                model_tested = data.get('model_tested', None)
                if model_tested is None:
                    # Try to extract from models_tested field
                    models_tested = data.get('models_tested', [])
                    if models_tested:
                        if isinstance(models_tested, str):
                            try:
                                models_tested = json.loads(models_tested)
                            except:
                                model_tested = models_tested
                        
                        if isinstance(models_tested, list):
                            model_names = []
                            for model in models_tested:
                                if isinstance(model, str):
                                    model_names.append(model)
                                elif isinstance(model, dict):
                                    if 'name' in model:
                                        model_names.append(model['name'])
                                    elif 'model' in model:
                                        model_names.append(model['model'])
                                    elif 'id' in model:
                                        model_names.append(model['id'])
                                    elif 'provider' in model and 'model' in model:
                                        model_names.append(f"{model['provider']}-{model['model']}")
                                    elif 'type' in model and 'id' in model:
                                        model_names.append(f"{model['type']}-{model['id']}")
                                    else:
                                        model_names.append(str(model))
                                else:
                                    model_names.append(str(model))
                            model_tested = ", ".join(model_names) if model_names else 'Unknown'
                        elif isinstance(models_tested, str):
                            model_tested = models_tested
                        else:
                            model_tested = str(models_tested)
                    elif 'metadata' in data and isinstance(data['metadata'], dict):
                        model_tested = data['metadata'].get('model_tested', 'Unknown')
                    elif 'openai_model' in data and 'gemini_model' in data:
                        models = []
                        if data.get('openai_model') and data.get('openai_model') != 'Unknown':
                            models.append(data.get('openai_model'))
                        if data.get('gemini_model') and data.get('gemini_model') != 'Unknown':
                            models.append(data.get('gemini_model'))
                        model_tested = ", ".join(models) if models else 'Unknown'
                    elif 'examples' in data and isinstance(data['examples'], list) and data['examples']:
                        first_example = data['examples'][0]
                        if 'responses' in first_example and isinstance(first_example['responses'], list):
                            models = set()
                            for response in first_example['responses']:
                                if 'model' in response:
                                    models.add(response['model'])
                            model_tested = ", ".join(sorted(models)) if models else 'Unknown'
                        else:
                            model_tested = 'Unknown'
                    elif 'id' in data and isinstance(data.get('id'), str) and data.get('type') == 'benchmark':
                        model_tested = data.get('name', 'Unknown').replace('API Benchmark', '').strip() or 'API Benchmark'
                    else:
                        model_tested = 'Unknown'
                
                # Get benchmark_id from right place
                benchmark_id = data.get('benchmark_id', None)
                if benchmark_id is None and 'id' in data:
                    benchmark_id = data.get('id')
                if benchmark_id is None:
                    benchmark_id = f'unknown-{i}'
                
                # Get total prompts from different possible sources
                total_prompts = data.get('total_prompts', 0)
                if total_prompts == 0:
                    total_prompts = data.get('examples_tested', 0)
                if total_prompts == 0:
                    examples = data.get('examples', [])
                    if isinstance(examples, list):
                        total_prompts = len(examples)
                if total_prompts == 0 and 'metadata' in data and isinstance(data['metadata'], dict):
                    total_prompts = data['metadata'].get('examples_count', 0)
                    if total_prompts == 0:
                        total_prompts = data['metadata'].get('total_prompts', 0)
                
                # Calculate success rate from different possible sources
                success_rate = "N/A"
                
                if 'success_rate' in data and data['success_rate'] is not None:
                    success_rate_val = data['success_rate']
                    if isinstance(success_rate_val, (int, float)):
                        success_rate = f"{success_rate_val:.1f}%"
                    elif isinstance(success_rate_val, str):
                        success_rate = success_rate_val
                elif data.get('bypass_success') and total_prompts > 0:
                    bypass_success = data.get('bypass_success', {})
                    providers = ['openai', 'gemini', 'custom'] 
                    success_values = [bypass_success.get(provider, 0) for provider in providers if provider in bypass_success]
                    avg_success = sum(success_values) / len(success_values) if success_values else 0
                    success_rate = f"{avg_success / total_prompts * 100:.1f}%" if total_prompts > 0 else "N/A"
                elif 'openai_bypass_rate' in data or 'gemini_bypass_rate' in data:
                    rates = []
                    if 'openai_bypass_rate' in data:
                        rates.append(data['openai_bypass_rate'])
                    if 'gemini_bypass_rate' in data:
                        rates.append(data['gemini_bypass_rate'])
                    if rates:
                        avg_rate = sum(rates) / len(rates)
                        success_rate = f"{avg_rate:.1f}%"
                elif 'examples' in data and isinstance(data['examples'], list) and total_prompts > 0:
                    successful_responses = 0
                    total_responses = 0
                    for example in data['examples']:
                        if 'responses' in example and isinstance(example['responses'], list):
                            for response in example['responses']:
                                total_responses += 1
                                if response.get('success', False):
                                    successful_responses += 1
                    if total_responses > 0:
                        success_rate = f"{(successful_responses / total_responses) * 100:.1f}%"
                elif 'metadata' in data and isinstance(data['metadata'], dict) and 'bypass_rate' in data['metadata']:
                    success_rate = data['metadata']['bypass_rate']
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_timestamp = timestamp
                
                # Determine status
                status = "Complete"
                if data.get('status') == 'failed':
                    status = "[red]Failed[/]"
                elif data.get('status') == 'in_progress':
                    status = "[yellow]In Progress[/]"
                elif data.get('errors', []):
                    status = "[yellow]Partial[/]"
                
                # Create result data
                result_data = {
                    'id': i+1,
                    'benchmark_id': benchmark_id,
                    'timestamp': timestamp,
                    'formatted_timestamp': formatted_timestamp,
                    'model_tested': model_tested,
                    'total_prompts': total_prompts,
                    'success_rate': success_rate,
                    'status': status,
                    'data': data
                }
                
                # Categorize based on size
                if total_prompts >= 100:
                    large_benchmarks.append(result_data)
                else:
                    results_data.append(result_data)
                    
            except Exception as e:
                failed_entries.append((f"Entry {i+1}", str(e)))
        
        # Ensure large benchmarks are included at the top
        if large_benchmarks:
            for large_bench in large_benchmarks:
                results_data.insert(0, large_bench)
        
        # Show information about any failed entries
        if failed_entries:
            self.console.print(Panel(
                f"[yellow]Warning: {len(failed_entries)} result entries had issues:[/]\n\n" +
                "\n".join(f"• {entry}: {error}" for entry, error in failed_entries) +
                "\n\nThese entries were skipped. There might be corrupted data in the database.",
                title="[yellow]Entry Issues[/]",
                border_style="yellow"
            ))
        
        return results_data

    def _export_current_benchmark(self, data: Dict[str, Any]):
        """Export the currently viewed benchmark data"""
        # Debug - log the data keys and structure
        self.console.print(f"[bold blue]Preparing to export benchmark data with keys: {', '.join(data.keys())}[/]")
        
        # Debug - check if data contains examples
        if 'examples' in data:
            self.console.print(f"[bold green]Found {len(data['examples'])} examples to export[/]")
        elif 'detailed_results' in data:
            self.console.print(f"[bold green]Found {len(data['detailed_results'])} detailed_results to export[/]")
        elif 'models_tested' in data:
            # self.console.print(f"[bold green]Found models_tested with {len(data['models_tested'])} models[/]")
            for i, model in enumerate(data['models_tested']):
                if 'examples' in model:
                    self.console.print(f"[bold green]Model {i} has {len(model['examples'])} examples[/]")
        
        # Ask for export format
        format_questions = [
            inquirer.List(
                'format',
                message="Select export format",
                choices=[
                    ('CSV - Prompts and Responses', 'csv_full'),
                    ('CSV - Responses Only', 'csv_responses'),
                    ('JSON - Complete Data', 'json'),
                    ('Plain Text Report', 'txt')
                ]
            )
        ]
        
        # Preprocess data to ensure we have examples or detailed_results
        # This is critical for CSV exports
        if not data.get('examples', []) and not data.get('detailed_results', []):
            self.console.print("[bold yellow]No examples or detailed_results found - attempting to extract from available data...[/]")
            
            # Try to convert from models_tested format
            if 'models_tested' in data:
                self.console.print("[bold blue]Extracting examples from models_tested structure...[/]")
                
                try:
                    # Create examples list
                    examples = []
                    
                    # Process each model
                    for model in data.get('models_tested', []):
                        model_name = model.get('model', 'Unknown')
                        provider = model.get('provider', 'Unknown')
                        
                        # Process each example in the model
                        for example in model.get('examples', []):
                            # Extract prompt
                            prompt_text = ""
                            if isinstance(example.get('prompt'), dict) and 'text' in example['prompt']:
                                prompt_text = example['prompt']['text']
                            else:
                                prompt_text = str(example.get('prompt', example.get('input', 'No prompt available')))
                            
                            # Look for existing example with this prompt
                            existing_example = None
                            for ex in examples:
                                if ex.get('prompt') == prompt_text:
                                    existing_example = ex
                                    break
                            
                            # Create or update example
                            if existing_example:
                                # Add this model's response to existing example
                                if 'responses' not in existing_example:
                                    existing_example['responses'] = []
                                
                                existing_example['responses'].append({
                                    'model': model_name,
                                    'provider': provider,
                                    'success': example.get('success', False),
                                    'response': example.get('response', example.get('output', 'No response')),
                                    'response_time': example.get('response_time', 0)
                                })
                            else:
                                # Create new example
                                new_example = {
                                    'prompt': prompt_text,
                                    'responses': [{
                                        'model': model_name,
                                        'provider': provider,
                                        'success': example.get('success', False),
                                        'response': example.get('response', example.get('output', 'No response')),
                                        'response_time': example.get('response_time', 0)
                                    }]
                                }
                                examples.append(new_example)
                    
                    # Update data with extracted examples
                    if examples:
                        data['examples'] = examples
                        self.console.print(f"[bold green]Successfully extracted {len(examples)} examples with responses[/]")
                
                except Exception as e:
                    self.console.print(f"[bold red]Error converting models_tested: {str(e)}[/]")
            
            # Try alternative data structures if still no examples
            if not data.get('examples', []):
                # Check for bypass_success structure
                if 'bypass_success' in data and 'prompts' in data:
                    self.console.print("[bold blue]Attempting to reconstruct from bypass_success and prompts...[/]")
                    
                    try:
                        examples = []
                        prompts = data.get('prompts', [])
                        
                        for i, prompt in enumerate(prompts):
                            responses = []
                            
                            # Add response for each provider
                            for provider in ['openai', 'gemini', 'custom']:
                                if provider in data.get('model_results', {}):
                                    provider_results = data['model_results'][provider]
                                    if i < len(provider_results):
                                        result = provider_results[i]
                                        responses.append({
                                            'model': data.get(f'{provider}_model', provider),
                                            'provider': provider,
                                            'success': result.get('success', False),
                                            'response': result.get('response', 'No response'),
                                            'response_time': result.get('response_time', 0)
                                        })
                            
                            if responses:
                                examples.append({
                                    'prompt': prompt,
                                    'responses': responses
                                })
                        
                        if examples:
                            data['examples'] = examples
                            self.console.print(f"[bold green]Reconstructed {len(examples)} examples from prompt data[/]")
                    
                    except Exception as e:
                        self.console.print(f"[bold red]Error reconstructing from prompts: {str(e)}[/]")
        
        # Check if we have detailed_results but no examples
        if not data.get('examples', []) and data.get('detailed_results', []):
            self.console.print("[bold blue]Converting detailed_results to examples format...[/]")
            
            try:
                examples = []
                for result in data.get('detailed_results', []):
                    prompt = result.get('prompt', 'No prompt available')
                    apis = result.get('apis', {})
                    
                    responses = []
                    for provider, provider_data in apis.items():
                        responses.append({
                            'model': provider,
                            'provider': provider,
                            'success': provider_data.get('success', False),
                            'response': provider_data.get('response', provider_data.get('error', 'No response')),
                            'response_time': provider_data.get('response_time', 0)
                        })
                    
                    if responses:
                        examples.append({
                            'prompt': prompt,
                            'responses': responses
                        })
                
                if examples:
                    data['examples'] = examples
                    self.console.print(f"[bold green]Converted {len(examples)} detailed_results to examples format[/]")
            
            except Exception as e:
                self.console.print(f"[bold red]Error converting detailed_results: {str(e)}[/]")
        
        format_answers = inquirer.prompt(format_questions)
        if not format_answers:
            return
        
        export_format = format_answers['format']
        
        # Export based on selected format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.console.print(f"[blue]Exporting benchmark data...[/]")
        
        # Ensure export directory exists
        self.exports_dir.mkdir(exist_ok=True, parents=True)
        
        if export_format == 'csv_full':
            # Enhanced CSV export with prompts and responses
            filepath = self.exports_dir / f"full_results_export_{timestamp}.csv"
            self._export_to_csv_full(data, filepath)
            self.console.print(f"[green]Full results exported to {filepath}[/]")
            self.console.print(f"[dim]To view the file: cat {filepath}[/]")
            
        elif export_format == 'csv_responses':
            # Basic CSV export with just responses
            filepath = self.exports_dir / f"responses_export_{timestamp}.csv"
            self._export_to_csv_responses(data, filepath)
            self.console.print(f"[green]Responses exported to {filepath}[/]")
            self.console.print(f"[dim]To view the file: cat {filepath}[/]")
            
        elif export_format == 'json':
            # Complete JSON export
            filepath = self.exports_dir / f"results_export_{timestamp}.json"
            try:
                # Define a JSON encoder class that can handle complex types
                class ExtendedJSONEncoder(json.JSONEncoder):
                    def default(self, obj):
                        # Handle datetime objects
                        if hasattr(obj, 'isoformat'):
                            return obj.isoformat()
                        # Handle binary data
                        if isinstance(obj, bytes):
                            return obj.decode('utf-8', errors='ignore')
                        # Handle numpy arrays
                        if hasattr(obj, 'tolist'):
                            return obj.tolist()
                        # Handle sets
                        if isinstance(obj, set):
                            return list(obj)
                        # Let the base class handle it or raise TypeError
                        try:
                            return json.JSONEncoder.default(self, obj)
                        except:
                            return str(obj)  # Last resort: convert to string

                # Make a clean copy of the data to avoid modifying the original
                export_data = {}
                try:
                    # Try to use a proper deep copy
                    export_data = copy.deepcopy(data)
                except:
                    # Fallback: manual copy of top-level keys
                    for key, value in data.items():
                        export_data[key] = value

                # Add export metadata
                export_data['_export_metadata'] = {
                    'exported_at': datetime.now().isoformat(),
                    'exported_by': 'Dravik Benchmark System',
                    'original_keys': list(data.keys())
                }

                # Check before writing to ensure we have good data
                json_data = json.dumps(export_data, indent=2, cls=ExtendedJSONEncoder)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_data)
                
                self.console.print(f"[green]Complete data exported to {filepath}[/]")
                self.console.print(f"[dim]To view the file: cat {filepath}[/]")
                # Debug - check file size after writing
                self.console.print(f"[bold blue]Exported file size: {filepath.stat().st_size} bytes[/]")
                
                # Verify the export worked by attempting to read it back
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        json.load(f)
                    self.console.print(f"[green]✓ Export verification successful - JSON is valid[/]")
                except Exception as verify_error:
                    self.console.print(f"[yellow]Warning: Export verification failed - {str(verify_error)}[/]")
                    
            except Exception as e:
                self.console.print(f"[red]Error exporting to JSON: {e}[/]")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/]")
            
        elif export_format == 'txt':
            # Plain text report
            filepath = self.exports_dir / f"report_export_{timestamp}.txt"
            self._export_to_text_report(data, filepath)
            self.console.print(f"[green]Text report exported to {filepath}[/]")
            self.console.print(f"[dim]To view the file: cat {filepath}[/]")
    
    def _export_to_csv_full(self, data: Dict[str, Any], filepath: Path):
        """Export both prompts and responses to a comprehensive CSV file"""
        try:
            # Ensure export directory exists
            filepath.parent.mkdir(exist_ok=True, parents=True)
            
            # Use binary mode and write UTF-8 without BOM
            with open(filepath, 'wb') as file:
                # Convert to string first to handle BOM correctly
                csv_content = "prompt_id,prompt,provider,model,success,response,response_time\n"
                
                # We need to handle multiple data formats (detailed_results, examples, models_tested)
                # First, check for examples (this is our preferred converted format)
                examples = data.get('examples', [])
                if examples:
                    self.console.print(f"[green]Exporting {len(examples)} examples to CSV[/]")
                    for i, example in enumerate(examples):
                        prompt = example.get('prompt', 'No prompt available')
                        responses = example.get('responses', [])
                        
                        for response in responses:
                            # Get model name with appropriate fallbacks
                            provider = response.get('provider', 'Unknown')
                            model = response.get('model', 'Unknown')
                            
                            # For custom models, check if we can get the actual model name
                            if (provider == 'custom' or provider == 'custom-api') and model == 'Unknown':
                                # Try to get model name from data
                                model = data.get('model_tested', data.get('name', model))
                            
                            success = str(response.get('success', False))
                            response_text = response.get('response', 'No response')
                            response_time = response.get('response_time', 0)
                            
                            # Make sure we have data to write
                            if not prompt or prompt == 'No prompt available':
                                self.console.print(f"[yellow]Warning: Missing prompt for example {i+1}[/]")
                            
                            csv_content += f'{i+1},"{self._csv_escape(prompt)}","{provider}","{model}","{success}","{self._csv_escape(response_text)}","{response_time}"\n'
                    
                    self.console.print(f"[green]Exported {len(examples)} prompts with {sum(len(example.get('responses', [])) for example in examples)} responses.[/]")
                
                # Next, check for detailed_results
                elif 'detailed_results' in data:
                    detailed_results = data.get('detailed_results', [])
                    self.console.print(f"[green]Exporting {len(detailed_results)} detailed results to CSV[/]")
                    
                    for i, result in enumerate(detailed_results):
                        prompt = result.get('prompt', 'No prompt available')
                        apis = result.get('apis', {})
                        
                        if not apis:
                            # If no API data, write a placeholder row
                            csv_content += f'{i+1},"{self._csv_escape(prompt)}","n/a","n/a","n/a","No API responses found","0"\n'
                            continue
                        
                        # Write a row for each provider's response
                        for provider, provider_data in apis.items():
                            # Get model name - for custom provider, use the model_tested field
                            model = provider
                            if provider == 'custom' or provider == 'custom-api':
                                model = data.get('model_tested', data.get('name', provider))
                                
                            success = str(provider_data.get('success', False))
                            response = provider_data.get('response', provider_data.get('error', 'No response'))
                            response_time = provider_data.get('response_time', 0)
                            csv_content += f'{i+1},"{self._csv_escape(prompt)}","{provider}","{model}","{success}","{self._csv_escape(response)}","{response_time}"\n'
                    
                    self.console.print(f"[green]Exported {len(detailed_results)} benchmark results with responses.[/]")
                
                # Finally, check for models_tested format
                elif 'models_tested' in data:
                    models = data.get('models_tested', [])
                    self.console.print(f"[green]Exporting from {len(models)} models_tested to CSV[/]")
                    
                    # We need to create a prompt mapping to avoid duplicates
                    prompt_mapping = {}
                    prompt_counter = 0
                    
                    for model in models:
                        # Get proper model name - for custom provider, ensure we have the correct name
                        model_name = model.get('model', 'Unknown')
                        provider = model.get('provider', 'Unknown')
                        
                        # If this is a custom model, try to get the real name
                        if (provider == 'custom' or provider == 'custom-api') and model_name == 'Unknown':
                            model_name = data.get('model_tested', data.get('name', model_name))
                        
                        examples = model.get('examples', [])
                        
                        for example in examples:
                            # Get the prompt text
                            prompt_text = None
                            if isinstance(example.get('prompt'), dict) and 'text' in example['prompt']:
                                prompt_text = example['prompt']['text']
                            else:
                                prompt_text = example.get('prompt', example.get('input', 'No prompt available'))
                            
                            # Get a unique ID for this prompt
                            prompt_id = None
                            if prompt_text in prompt_mapping:
                                prompt_id = prompt_mapping[prompt_text]
                            else:
                                prompt_counter += 1
                                prompt_id = prompt_counter
                                prompt_mapping[prompt_text] = prompt_id
                            
                            # Get response data
                            success = str(example.get('success', False))
                            response = example.get('response', example.get('output', 'No response'))
                            response_time = example.get('response_time', 0)
                            
                            # Add to CSV
                            csv_content += f'{prompt_id},"{self._csv_escape(prompt_text)}","{provider}","{model_name}","{success}","{self._csv_escape(response)}","{response_time}"\n'
                    
                    self.console.print(f"[green]Exported {prompt_counter} unique prompts with {sum(len(model.get('examples', [])) for model in models)} responses.[/]")
                
                # Handle the case when we have raw prompts and responses
                elif 'prompts' in data and ('model_results' in data or any(key.endswith('_results') for key in data.keys())):
                    prompts = data.get('prompts', [])
                    self.console.print(f"[green]Exporting from {len(prompts)} raw prompts to CSV[/]")
                    
                    # Find the results fields
                    result_fields = [k for k in data.keys() if k.endswith('_results') or k == 'model_results']
                    
                    for i, prompt in enumerate(prompts):
                        # For each result field, extract the corresponding response
                        for field in result_fields:
                            provider = field.replace('_results', '')
                            if provider == 'model':
                                # This is a special case where we have multiple providers in one field
                                model_results = data.get(field, {})
                                for model_name, results in model_results.items():
                                    if i < len(results):
                                        result = results[i]
                                        success = str(result.get('success', False))
                                        response = result.get('response', 'No response')
                                        response_time = result.get('response_time', 0)
                                        
                                        # Fix custom model names
                                        if model_name == 'custom' or model_name == 'custom-api':
                                            model_name = data.get('model_tested', data.get('name', model_name))
                                        
                                        csv_content += f'{i+1},"{self._csv_escape(prompt)}","{model_name}","{model_name}","{success}","{self._csv_escape(response)}","{response_time}"\n'
                            else:
                                # Standard case with a single provider
                                results = data.get(field, [])
                                if i < len(results):
                                    result = results[i]
                                    model_name = data.get(f'{provider}_model', provider)
                                    
                                    # Fix custom model names
                                    if provider == 'custom' or provider == 'custom-api':
                                        model_name = data.get('model_tested', data.get('name', model_name))
                                    
                                    success = str(result.get('success', False))
                                    response = result.get('response', 'No response')
                                    response_time = result.get('response_time', 0)
                                    
                                    csv_content += f'{i+1},"{self._csv_escape(prompt)}","{provider}","{model_name}","{success}","{self._csv_escape(response)}","{response_time}"\n'
                    
                    self.console.print(f"[green]Exported {len(prompts)} prompts with responses from {len(result_fields)} models/providers.[/]")
                
                else:
                    self.console.print("[yellow]Warning: No recognizable data format found. Creating a minimal CSV.[/]")
                    self.console.print("[yellow]The CSV file will only contain the header row and minimal data.[/]")
                    
                    # Add diagnostic info to the exported file
                    csv_content += '0,"No prompt data found in a recognized format","n/a","n/a","n/a","This benchmark has no prompt data in a recognized format.","0"\n'
                    
                    # Log the keys available in the data for debugging
                    self.console.print(f"[dim]Available data keys: {', '.join(data.keys())}[/]")
                
                # Write the content as UTF-8
                file.write(csv_content.encode('utf-8'))
                self.console.print(f"[bold green]CSV file saved: {filepath}[/]")
                self.console.print(f"[bold blue]Exported file size: {filepath.stat().st_size} bytes[/]")
                
        except Exception as e:
            self.console.print(f"[red]Error exporting to CSV: {e}[/]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/]")
    
    def _csv_escape(self, text):
        """Escape text for CSV by doubling quotes and handling newlines"""
        if not text:
            return ""
        return str(text).replace('"', '""').replace('\n', ' ').replace('\r', '')
    
    def _export_to_csv_responses(self, data: Dict[str, Any], filepath: Path):
        """Export just the responses to a CSV file"""
        try:
            # Ensure export directory exists
            filepath.parent.mkdir(exist_ok=True, parents=True)
            
            # Use binary mode and write UTF-8 without BOM
            with open(filepath, 'wb') as file:
                # Convert to string first to handle BOM correctly
                csv_content = "id,prompt_id,model,provider,response,success\n"
                
                # Count of exported responses
                response_count = 0
                
                # Check for examples first (our preferred format)
                examples = data.get('examples', [])
                if examples:
                    self.console.print(f"[green]Exporting responses from {len(examples)} examples[/]")
                    
                    for i, example in enumerate(examples):
                        prompt = example.get('prompt', 'No prompt available')
                        responses = example.get('responses', [])
                        
                        for j, response in enumerate(responses):
                            provider = response.get('provider', 'Unknown')
                            model = response.get('model', 'Unknown')
                            
                            # For custom models, check if we can get the actual model name
                            if (provider == 'custom' or provider == 'custom-api') and model == 'Unknown':
                                # Try to get model name from data
                                model = data.get('model_tested', data.get('name', model))
                                
                            success = str(response.get('success', False))
                            response_text = response.get('response', 'No response')
                            
                            response_count += 1
                            csv_content += f'{response_count},{i+1},"{model}","{provider}","{self._csv_escape(response_text)}",{success}\n'
                    
                    self.console.print(f"[green]Exported {response_count} responses from examples[/]")
                
                # Check for detailed_results
                elif data.get('detailed_results', []):
                    detailed_results = data.get('detailed_results', [])
                    self.console.print(f"[green]Exporting responses from {len(detailed_results)} detailed results[/]")
                    
                    for i, result in enumerate(detailed_results):
                        apis = result.get('apis', {})
                        
                        for provider, provider_data in apis.items():
                            # Get model name - for custom provider, use the model_tested field
                            model = provider
                            if provider == 'custom' or provider == 'custom-api':
                                model = data.get('model_tested', data.get('name', provider))
                                
                            response = provider_data.get('response', provider_data.get('error', 'No response'))
                            success = str(provider_data.get('success', False))
                            
                            response_count += 1
                            csv_content += f'{response_count},{i+1},"{model}","{provider}","{self._csv_escape(response)}",{success}\n'
                    
                    self.console.print(f"[green]Exported {response_count} responses from detailed results[/]")
                
                # Check for models_tested format
                elif 'models_tested' in data:
                    models = data.get('models_tested', [])
                    self.console.print(f"[green]Exporting responses from {len(models)} models[/]")
                    
                    # Create a mapping for prompts to avoid duplicates
                    prompt_mapping = {}
                    prompt_counter = 0
                    
                    for model in models:
                        model_name = model.get('model', 'Unknown')
                        provider = model.get('provider', 'Unknown')
                        
                        # If this is a custom model, try to get the real name
                        if (provider == 'custom' or provider == 'custom-api') and model_name == 'Unknown':
                            model_name = data.get('model_tested', data.get('name', model_name))
                            
                        examples = model.get('examples', [])
                        
                        for example in examples:
                            # Get the prompt
                            prompt_text = None
                            if isinstance(example.get('prompt'), dict) and 'text' in example['prompt']:
                                prompt_text = example['prompt']['text']
                            else:
                                prompt_text = example.get('prompt', example.get('input', 'No prompt available'))
                            
                            # Get prompt ID
                            prompt_id = None
                            if prompt_text in prompt_mapping:
                                prompt_id = prompt_mapping[prompt_text]
                            else:
                                prompt_counter += 1
                                prompt_id = prompt_counter
                                prompt_mapping[prompt_text] = prompt_id
                            
                            # Get response data
                            response = example.get('response', example.get('output', 'No response'))
                            success = str(example.get('success', False))
                            
                            response_count += 1
                            csv_content += f'{response_count},{prompt_id},"{model_name}","{provider}","{self._csv_escape(response)}",{success}\n'
                    
                    self.console.print(f"[green]Exported {response_count} responses from {prompt_counter} unique prompts[/]")
                
                # Check for raw prompts and model_results
                elif 'prompts' in data and ('model_results' in data or any(key.endswith('_results') for key in data.keys())):
                    prompts = data.get('prompts', [])
                    self.console.print(f"[green]Exporting responses from {len(prompts)} raw prompts[/]")
                    
                    # Find the results fields
                    result_fields = [k for k in data.keys() if k.endswith('_results') or k == 'model_results']
                    
                    for i, prompt in enumerate(prompts):
                        # For each result field, extract the corresponding response
                        for field in result_fields:
                            provider = field.replace('_results', '')
                            if provider == 'model':
                                # This is a special case for model_results
                                model_results = data.get(field, {})
                                for model_name, results in model_results.items():
                                    if i < len(results):
                                        result = results[i]
                                        
                                        # Fix custom model names
                                        if model_name == 'custom' or model_name == 'custom-api':
                                            model_name = data.get('model_tested', data.get('name', model_name))
                                            
                                        response = result.get('response', 'No response')
                                        success = str(result.get('success', False))
                                        
                                        response_count += 1
                                        csv_content += f'{response_count},{i+1},"{model_name}","{model_name}","{self._csv_escape(response)}",{success}\n'
                            else:
                                # Standard case with a single provider
                                results = data.get(field, [])
                                if i < len(results):
                                    result = results[i]
                                    model_name = data.get(f'{provider}_model', provider)
                                    
                                    # Fix custom model names
                                    if provider == 'custom' or provider == 'custom-api':
                                        model_name = data.get('model_tested', data.get('name', model_name))
                                        
                                    response = result.get('response', 'No response')
                                    success = str(result.get('success', False))
                                    
                                    response_count += 1
                                    csv_content += f'{response_count},{i+1},"{model_name}","{provider}","{self._csv_escape(response)}",{success}\n'
                    
                    self.console.print(f"[green]Exported {response_count} responses from {len(prompts)} prompts[/]")
                
                else:
                    # No recognized data format - create minimal output
                    self.console.print("[yellow]Warning: No recognizable data format found for responses[/]")
                    self.console.print("[yellow]The CSV file will only contain diagnostic information[/]")
                    
                    # Add diagnostic info
                    csv_content += f'1,0,"Unknown","N/A","No response data found in a recognized format",false\n'
                    
                    # Log the keys available
                    self.console.print(f"[dim]Available data keys: {', '.join(data.keys())}[/]")
                
                # Write the content as UTF-8
                file.write(csv_content.encode('utf-8'))
                self.console.print(f"[bold green]CSV file with {response_count} responses saved: {filepath}[/]")
                
        except Exception as e:
            self.console.print(f"[red]Error exporting responses to CSV: {e}[/]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/]")
    
    def _export_to_text_report(self, data: Dict[str, Any], filepath: Path):
        """Export results to a plain text report"""
        try:
            # Ensure export directory exists
            filepath.parent.mkdir(exist_ok=True, parents=True)
            
            # Use binary mode and write UTF-8 without BOM
            with open(filepath, 'wb') as file:
                # Build the content as a string first
                content = "DRAVIK BENCHMARK RESULTS REPORT\n"
                content += "==============================\n\n"
                
                # Write summary information
                content += f"Timestamp: {data.get('timestamp', 'Unknown')}\n"
                content += f"Benchmark ID: {data.get('benchmark_id', 'Unknown')}\n"
                
                # Handle different data formats
                if 'models_tested' in data:
                    # API benchmark format
                    models = data.get('models_tested', [])
                    content += f"Format: API Benchmark with {len(models)} models\n"
                    content += f"Total Examples Tested: {data.get('examples_tested', 0)}\n"
                    content += f"Overall Success Rate: {data.get('success_rate', 0):.2f}%\n\n"
                    
                    # List models
                    content += "MODELS TESTED\n"
                    content += "-------------\n"
                    for model in models:
                        model_name = model.get('model', 'Unknown')
                        provider = model.get('provider', 'Unknown')
                        
                        # Fix custom model names
                        if (provider == 'custom' or provider == 'custom-api') and model_name == 'Unknown':
                            model_name = data.get('model_tested', data.get('name', model_name))
                            
                        success_rate = model.get('success_rate', 0)
                        avg_time = model.get('average_response_time', 0)
                        examples_count = len(model.get('examples', []))
                        
                        content += f"- {model_name} ({provider})\n"
                        content += f"  Success Rate: {success_rate:.2f}%\n"
                        content += f"  Avg Response Time: {avg_time:.2f}s\n"
                        content += f"  Examples Processed: {examples_count}\n\n"
                    
                    # Check if we have converted examples to write
                    examples = data.get('examples', [])
                    if examples:
                        content += "PROMPT EXAMPLES\n"
                        content += "--------------\n\n"
                        for i, example in enumerate(examples[:10]):  # Limit to first 10 for readability
                            content += f"Example #{i+1}:\n"
                            content += f"Prompt: {example.get('prompt', 'No prompt available')}\n"
                            
                            for response in example.get('responses', []):
                                provider = response.get('provider', 'Unknown')
                                model = response.get('model', 'Unknown')
                                
                                # Fix custom model names
                                if (provider == 'custom' or provider == 'custom-api') and model == 'Unknown':
                                    model = data.get('model_tested', data.get('name', model))
                                    
                                success = "✓" if response.get('success', False) else "✗"
                                response_text = response.get('response', 'No response available')
                                content += f"  {model} [{success}]: {response_text[:100]}{'...' if len(response_text) > 100 else ''}\n"
                            
                            content += "\n"
                        
                        if len(examples) > 10:
                            content += f"... and {len(examples) - 10} more entries (truncated for readability)\n\n"
                    # If we don't have converted examples, try to look at raw model examples
                    else:
                        content += "EXAMPLE PROMPTS\n"
                        content += "--------------\n\n"
                        total_examples = 0
                        for model in models:
                            model_name = model.get('model', 'Unknown')
                            provider = model.get('provider', 'Unknown')
                            
                            # Fix custom model names
                            if (provider == 'custom' or provider == 'custom-api') and model_name == 'Unknown':
                                model_name = data.get('model_tested', data.get('name', model_name))
                                
                            examples = model.get('examples', [])
                            # Only show a few examples per model
                            for i, example in enumerate(examples[:3]):
                                prompt = example.get('prompt', '')
                                if isinstance(prompt, dict) and 'text' in prompt:
                                    prompt = prompt['text']
                                
                                success = "✓" if example.get('success', False) else "✗"
                                response = example.get('response', example.get('output', 'No response'))
                                
                                content += f"Example #{total_examples+i+1} ({model_name}):\n"
                                content += f"Prompt: {prompt}\n"
                                content += f"Result [{success}]: {response[:100]}{'...' if len(response) > 100 else ''}\n\n"
                            
                            total_examples += len(examples[:3])
                            
                            if len(examples) > 3:
                                content += f"... and {len(examples) - 3} more examples for {model_name}\n\n"
                
                else:
                    # Standard benchmark format
                    model_tested = data.get('model_tested', 'Unknown')
                    content += f"Model Tested: {model_tested}\n"
                    content += f"Total Prompts: {data.get('total_prompts', 0)}\n\n"
                    
                    # Write model-specific scores
                    content += "PERFORMANCE BY MODEL\n"
                    content += "-------------------\n"
                    scores = data.get('scores', {})
                    for model, score in scores.items():
                        content += f"{model}: {score:.1f}%\n"
                    content += "\n"
                    
                    # Check for examples
                    examples = data.get('examples', [])
                    if examples:
                        content += "EXAMPLES\n"
                        content += "--------\n\n"
                        for i, example in enumerate(examples[:10]):  # Limit to first 10
                            content += f"Example #{i+1}:\n"
                            content += f"Prompt: {example.get('prompt', 'No prompt available')}\n"
                            
                            for response in example.get('responses', []):
                                provider = response.get('provider', 'Unknown')
                                model = response.get('model', 'Unknown')
                                
                                # Fix custom model names
                                if (provider == 'custom' or provider == 'custom-api') and model == 'Unknown':
                                    model = data.get('model_tested', data.get('name', model))
                                    
                                success = "✓" if response.get('success', False) else "✗"
                                response_text = response.get('response', 'No response')
                                content += f"  {model} [{success}]: {response_text[:100]}{'...' if len(response_text) > 100 else ''}\n"
                            
                            content += "\n"
                        
                        if len(examples) > 10:
                            content += f"... and {len(examples) - 10} more entries (truncated for readability)\n\n"
                    
                    # Write detailed results
                    detailed_results = data.get('detailed_results', [])
                    if detailed_results:
                        content += "DETAILED RESULTS\n"
                        content += "---------------\n\n"
                        
                        for i, result in enumerate(detailed_results[:10]):  # Limit to first 10 for readability
                            content += f"Prompt #{i+1}: {result.get('prompt', 'N/A')}\n"
                            
                            apis = result.get('apis', {})
                            for provider, provider_data in apis.items():
                                # Get proper model name
                                model = provider
                                if provider == 'custom' or provider == 'custom-api':
                                    model = data.get('model_tested', data.get('name', provider))
                                    
                                success = "✓" if provider_data.get('success', False) else "✗"
                                response = provider_data.get('response', provider_data.get('error', 'No response'))
                                content += f"  {model} [{success}]: {response[:100]}{'...' if len(response) > 100 else ''}\n"
                            
                            content += "\n"
                        
                        if len(detailed_results) > 10:
                            content += f"... and {len(detailed_results) - 10} more entries (truncated for readability)\n"
                    
                    if not examples and not detailed_results:
                        content += "No detailed results available for this benchmark.\n"
                        content += "This may be due to the benchmark being in progress or an issue with the data.\n\n"
                        
                        # Include available keys for debugging
                        content += "Available data fields:\n"
                        for key in data.keys():
                            content += f"- {key}\n"
                
                # Write the content as UTF-8
                file.write(content.encode('utf-8'))
                self.console.print(f"[bold green]Text report saved: {filepath}[/]")
                self.console.print(f"[bold blue]Exported file size: {filepath.stat().st_size} bytes[/]")
                
        except Exception as e:
            self.console.print(f"[red]Error exporting to text report: {e}[/]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/]")
    
    def display_api_results(self, data: Dict[str, Any]):
        """Display API benchmark results"""
        # Show basic information
        self.console.print(Panel(f"[bold blue]Benchmark Results[/]"))
        
        # Add diagnostic logging 
        if self.verbose:
            # self.console.print("[bold magenta]DEBUG: Benchmark data keys:[/]")
            # self.console.print(", ".join(data.keys()))
            pass
        
        # Determine the data format (examples vs detailed_results)
        examples_count = len(data.get("examples", []))
        detailed_results_count = len(data.get("detailed_results", []))
        
        # Create a summary table
        summary_table = Table(title="Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        # Add basic metrics
        timestamp = data.get('timestamp', 'Unknown')
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_timestamp = timestamp
            
        summary_table.add_row("Timestamp", formatted_timestamp)
        summary_table.add_row("Benchmark ID", data.get('benchmark_id', 'Unknown'))
        
        # Based on available data, determine the prompt/example count
        if examples_count > 0:
            summary_table.add_row("Total Prompts", str(examples_count))
        elif detailed_results_count > 0:
            summary_table.add_row("Total Prompts", str(detailed_results_count))
        else:
            summary_table.add_row("Total Prompts", str(data.get('total_prompts', 0)))
        
        # Check for API benchmark specific format
        if 'models_tested' in data:
            # API benchmark format
            examples_tested = data.get('examples_tested', 0)
            overall_success = data.get('success_rate', 0)
            models_tested = data.get('models_tested', [])
            
            summary_table.add_row("Overall Success Rate", f"{overall_success:.2f}%")
            summary_table.add_row("Models Tested", str(len(models_tested)))
            
            # Display the summary
            self.console.print(summary_table)
            
            # Display model specific results
            if models_tested:
                model_table = Table(title="Model Performance", box=box.ROUNDED)
                model_table.add_column("Model", style="cyan")
                model_table.add_column("Provider", style="magenta")
                model_table.add_column("Success Rate", style="green")
                model_table.add_column("Avg Response Time", style="blue")
                model_table.add_column("Examples Processed", style="yellow")
                
                for model in models_tested:
                    model_name = model.get('model', 'Unknown')
                    provider = model.get('provider', 'Unknown')
                    success_rate = model.get('success_rate', 0)
                    avg_time = model.get('average_response_time', 0)
                    examples = len(model.get('examples', []))
                    
                    model_table.add_row(
                        model_name,
                        provider,
                        f"{success_rate:.2f}%",
                        f"{avg_time:.2f}s",
                        str(examples)
                    )
                
                self.console.print(model_table)
                
                # Ask if user wants to see individual examples
                if inquirer.confirm("View example details?", default=False):
                    self._display_api_example_details(data)
            
        else:
            # Standard benchmark format
            model_tested = data.get('model_tested', 'Unknown')
            total_prompts = data.get('total_prompts', 0)
            
            summary_table.add_row("Model Tested", model_tested)
            
            # Add model-specific metrics
            scores = data.get('scores', {})
            if not scores and 'metrics' in data:
                # Try to use metrics if scores not available
                scores = data.get('metrics', {})
                
            models_used = data.get('models_used', {})
            
            if scores:
                for model_key, score in scores.items():
                    # Handle different score formats
                    if isinstance(score, (int, float)):
                        score_value = score
                    elif isinstance(score, str) and score.endswith('%'):
                        try:
                            score_value = float(score.rstrip('%'))
                        except:
                            score_value = 0
                    else:
                        score_value = 0
                        
                    model_name = model_key.replace('_bypass_rate', '')
                    model_display = f"{model_name.capitalize()}"
                    
                    if model_name in models_used:
                        model_display = f"{model_name.capitalize()} ({models_used[model_name]})"
                        
                    summary_table.add_row(f"{model_display} Success Rate", f"{score_value:.1f}%")
            
            # Display the summary
            self.console.print(summary_table)
            
            # If we have examples or detailed results, offer to view them
            if examples_count > 0 or detailed_results_count > 0:
                if inquirer.confirm(f"View {'example' if examples_count > 0 else 'prompt'} details?", default=True):
                    self._display_api_example_details(data)
            else:
                # If no examples found, show a message
                self.console.print("[yellow]No examples or detailed results found in this benchmark data.[/]")
                # Try to display any available detailed results
                self._display_detailed_results(data)
    
    def _display_api_example_details(self, data: Dict[str, Any]):
        """Display detailed information for specific examples/prompts with improved error handling"""
        try:
            # Debug info
            # self.console.print("[bold magenta]DEBUG: Trying to find prompts...[/]")
            
            # Debugging: Dump the raw structure for models_tested
            if 'models_tested' in data:
                models = data.get('models_tested', [])
                
                for i, model in enumerate(models):
                    # Check if the model has an examples list
                    model_examples = model.get('examples', [])
                    if model_examples:
                        # Examine the first example
                        if model_examples:
                            example = model_examples[0]
                            # Check for prompt in different locations
                            for key in ['prompt', 'input', 'text']:
                                if key in example:
                                    self.console.print(f"Found prompt in '{key}': {str(example[key])[:50]}...")
            
            # Check for examples using multiple possible keys
            examples = data.get("examples", [])
            
            # If no examples found, try models_tested structure
            if not examples and 'models_tested' in data:
                combined_examples = []
                for model in data.get('models_tested', []):
                    model_examples = model.get('examples', [])
                    if model_examples:
                        # Convert model examples to the format we expect
                        for ex in model_examples:
                            # Extract the prompt text
                            prompt = None
                            if 'prompt' in ex:
                                prompt = ex['prompt']
                            elif 'input' in ex:
                                prompt = ex['input']
                            
                            # Create a response entry
                            response = {
                                'model': model.get('model', 'Unknown'),
                                'success': ex.get('success', False),
                                'bypassed': ex.get('bypassed', False),
                                'response': ex.get('response', ex.get('output', 'No response')),
                                'response_time': ex.get('response_time', 0)
                            }
                            
                            # Check if this example already exists in our list
                            found = False
                            for existing in combined_examples:
                                if existing.get('prompt') == prompt:
                                    # Add this response to the existing example
                                    if 'responses' not in existing:
                                        existing['responses'] = []
                                    existing['responses'].append(response)
                                    found = True
                                    break
                            
                            # If not found, add a new example
                            if not found and prompt:
                                combined_examples.append({
                                    'prompt': prompt,
                                    'responses': [response]
                                })
                
                if combined_examples:
                    examples = combined_examples
                    self.console.print(f"[green]Constructed {len(examples)} examples from models_tested data[/]")
            
            # If still no examples, try detailed_results as an alternative
            if not examples and "detailed_results" in data:
                examples = data.get("detailed_results", [])
                if self.verbose:
                    self.console.print("[yellow]Using 'detailed_results' as source of examples[/]")
            
            if not examples:
                self.console.print("[yellow]No examples or detailed results found in the benchmark data[/]")
                # Dump all data keys for debugging
                self.console.print(f"Available keys: {', '.join(data.keys())}")
                return
                
            # Create a list of prompts for the user to choose from
            prompt_choices = []
            for i, example in enumerate(examples):
                # Try to extract the prompt text from different formats
                prompt = None
                
                # Check different possible locations of the prompt text
                if "prompt" in example:
                    prompt = example["prompt"]
                elif "text" in example:
                    prompt = example["text"]
                
                # Handle dictionary format
                if isinstance(prompt, dict) and "text" in prompt:
                    prompt = prompt["text"]
                
                # If we still don't have a prompt, look for it in 'apis' entry structure
                if not prompt and "apis" in example:
                    # Try to get first prompt from any API response
                    for api_name, api_response in example.get("apis", {}).items():
                        if "prompt" in api_response:
                            prompt = api_response["prompt"]
                            break
                
                # If still no prompt found, create a placeholder
                if not prompt:
                    prompt = f"Example #{i+1} (No prompt text available)"
                    
                # Truncate long prompts for display
                display_text = prompt[:60] + "..." if len(prompt) > 60 else prompt
                prompt_choices.append((f"{i+1}. {display_text}", i))
                
            # Add option to go back
            prompt_choices.append(("Back to results", None))
            
            # Let user select a prompt
            prompt_question = [
                inquirer.List(
                    'prompt_index',
                    message="Select a prompt to view details",
                    choices=prompt_choices
                )
            ]
            
            prompt_answer = inquirer.prompt(prompt_question)
            if not prompt_answer or prompt_answer['prompt_index'] is None:
                return
                
            selected_index = prompt_answer['prompt_index']
            example = examples[selected_index]
            
            # Display the prompt - try different places it might be stored
            prompt = None
            if "prompt" in example:
                prompt = example["prompt"]
            elif "text" in example:
                prompt = example["text"]
                
            # Handle dictionary format
            if isinstance(prompt, dict) and "text" in prompt:
                prompt = prompt["text"]
                
            # If still no prompt, try looking in API responses
            if not prompt and "apis" in example:
                for api_name, api_response in example.get("apis", {}).items():
                    if "prompt" in api_response:
                        prompt = api_response["prompt"]
                        break
            
            # Use a fallback if no prompt found
            if not prompt:
                prompt = f"Example #{selected_index+1} (No prompt text available)"
                
            self.console.print(Panel(
                prompt,
                title=f"[bold blue]Prompt #{selected_index+1}[/]",
                border_style="blue"
            ))
            
            # Display responses - look in different possible locations
            responses = []
            
            # Try different response structures
            if "responses" in example:
                responses = example["responses"]
            elif "apis" in example:
                # Convert apis format to responses format
                for api_name, api_response in example.get("apis", {}).items():
                    formatted_response = {
                        "model": api_name,
                        "success": api_response.get("success", False),
                        "bypassed": api_response.get("bypassed", api_response.get("success", False)),
                        "response": api_response.get("response", "No response text"),
                        "response_time": api_response.get("response_time", "N/A")
                    }
                    responses.append(formatted_response)
            
            if not responses:
                self.console.print("[yellow]No responses found for this prompt[/]")
            else:
                self.console.print(f"[bold cyan]Responses ({len(responses)})[/]")
                
                for i, response in enumerate(responses):
                    # Get model and status
                    model = response.get("model", "Unknown model")
                    success = response.get("success", False)
                    bypassed = response.get("bypassed", False)
                    
                    # Determine border color based on status
                    if bypassed:
                        border_style = "red"
                        status = "[bold red]BYPASSED[/]"
                    elif not success:
                        border_style = "yellow"
                        status = "[bold yellow]FAILED[/]"
                    else:
                        border_style = "green"
                        status = "[bold green]SUCCESS[/]"
                        
                    # Get response text
                    response_text = response.get("response", "No response text")
                    if isinstance(response_text, dict) and "text" in response_text:
                        response_text = response_text["text"]
                        
                    # Display in panel
                    self.console.print(Panel(
                        f"{response_text}\n\n[dim]Response time: {response.get('response_time', 'N/A')}s[/]",
                        title=f"[bold]{model}[/] - {status}",
                        border_style=border_style
                    ))
            
            # Ask if user wants to see another example
            continue_question = [
                inquirer.List(
                    'continue',
                    message="What would you like to do next?",
                    choices=[
                        ("View another prompt", "another"),
                        ("Back to results", "back")
                    ],
                    default="another"
                )
            ]
            
            continue_answer = inquirer.prompt(continue_question)
            if not continue_answer or continue_answer['continue'] == "back":
                return
                
            # Show the prompt selection again
            return self._display_api_example_details(data)
            
        except Exception as e:
            self.console.print(f"[bold red]Error displaying example details: {e}[/]")
            import traceback
            self.console.print(traceback.format_exc())
            # Return gracefully to avoid crashing
            return
    
    def _display_detailed_results(self, data: Dict[str, Any]):
        """Display detailed benchmark results with categorization"""
        # Get the example results
        detailed_results = data.get('detailed_results', [])
        
        if not detailed_results:
            self.console.print("[yellow]No detailed results available.[/]")
            return
        
        # Analyze results by technique/category
        techniques = {}
        categories = {}
        
        for result in detailed_results:
            # Get the technique and evaluation
            technique = result.get('technique', 'unknown')
            category = result.get('category', 'unknown')
            evaluation = result.get('evaluation', 'UNKNOWN')
            
            # Track techniques
            if technique not in techniques:
                techniques[technique] = {'total': 0, 'success': 0}
            techniques[technique]['total'] += 1
            if evaluation == 'SUCCESS':
                techniques[technique]['success'] += 1
                
            # Track categories
            if category not in categories:
                categories[category] = {'total': 0, 'success': 0}
            categories[category]['total'] += 1
            if evaluation == 'SUCCESS':
                categories[category]['success'] += 1
        
        # Show technique results
        self.console.print("\n[bold cyan]Results by Technique[/]")
        technique_table = Table(title="Technique Analysis", box=box.ROUNDED)
        technique_table.add_column("Technique", style="cyan")
        technique_table.add_column("Total", style="blue")
        technique_table.add_column("Success", style="green")
        technique_table.add_column("Rate", style="magenta")
        
        for technique, stats in sorted(techniques.items(), key=lambda x: x[1]['total'], reverse=True):
            success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
            rate_style = "red" if success_rate > 50 else "green"
            technique_table.add_row(
                technique, 
                str(stats['total']), 
                str(stats['success']), 
                f"[{rate_style}]{success_rate:.1f}%[/]"
            )
            
        self.console.print(technique_table)
        
        # Show category results
        self.console.print("\n[bold cyan]Results by Category[/]")
        category_table = Table(title="Category Analysis", box=box.ROUNDED)
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Total", style="blue")
        category_table.add_column("Success", style="green")
        category_table.add_column("Rate", style="magenta")
        
        for category, stats in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
            success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
            rate_style = "red" if success_rate > 50 else "green"
            category_table.add_row(
                category, 
                str(stats['total']), 
                str(stats['success']), 
                f"[{rate_style}]{success_rate:.1f}%[/]"
            )
            
        self.console.print(category_table)
        
        # Ask if user wants to see individual examples
        if inquirer.confirm("View individual examples?", default=False):
            self._display_api_example_details(data)
    
    def show_statistics(self):
        """Show statistics across all benchmarks from the database"""
        # Load all benchmark results from database
        results_data = self.list_all_results()
        
        if not results_data:
            return
        
        # Prepare data structures to hold statistics
        models = {}  # Models that were tested against
        providers = {}  # API providers (openai, gemini, custom)
        success_by_provider = {}  # Success rates by provider
        success_by_technique = {}  # Success rates by jailbreak technique
        total_prompts = 0
        total_success = 0
        
        # Process all benchmark results
        for result in results_data:
            data = result['data']
            
            # Count total prompts
            result_prompts = data.get('total_prompts', 0)
            total_prompts += result_prompts
            
            # Track models tested
            model_tested = data.get('model_tested', 'Unknown')
            models[model_tested] = models.get(model_tested, 0) + result_prompts
            
            # Track providers and their success rates
            bypass_success = data.get('bypass_success', {})
            for provider, success_count in bypass_success.items():
                providers[provider] = providers.get(provider, 0) + result_prompts
                success_by_provider[provider] = success_by_provider.get(provider, 0) + success_count
                total_success += success_count
            
            # Track techniques (if available)
            detailed_results = data.get('detailed_results', [])
            for result_item in detailed_results:
                # Try to identify technique from prompt or metadata
                prompt = result_item.get('prompt', '')
                technique = self._identify_technique(prompt, result_item)
                
                if technique:
                    success_by_technique[technique] = success_by_technique.get(technique, {'total': 0, 'success': 0})
                    success_by_technique[technique]['total'] += 1
                    
                    # Check if any provider was successful
                    apis = result_item.get('apis', {})
                    if any(provider_data.get('success', False) for provider_data in apis.values()):
                        success_by_technique[technique]['success'] += 1
        
        # Display statistics
        self.console.print(Panel(f"[bold blue]Benchmark Statistics[/]"))
        
        # Overall statistics
        self.console.print(f"[bold cyan]Overall Statistics:[/]")
        overall_rate = (total_success / (total_prompts * len(providers))) * 100 if total_prompts and providers else 0
        self.console.print(f"Total prompts tested: {total_prompts}")
        self.console.print(f"Overall success rate: {overall_rate:.2f}%\n")
        
        # Provider statistics
        self.console.print(f"[bold cyan]Provider Success Rates:[/]")
        provider_table = Table(box=box.SIMPLE)
        provider_table.add_column("Provider", style="bright_blue")
        provider_table.add_column("Success Rate", style="green")
        provider_table.add_column("Successes", style="yellow")
        provider_table.add_column("Total Tests", style="magenta")
        
        for provider, total in providers.items():
            success = success_by_provider.get(provider, 0)
            rate = (success / total) * 100 if total else 0
            provider_table.add_row(
                provider.capitalize(),
                f"{rate:.2f}%",
                str(success),
                str(total)
            )
        
        self.console.print(provider_table)
        self.console.print()
        
        # Technique statistics (if available)
        if success_by_technique:
            self.console.print(f"[bold cyan]Technique Success Rates:[/]")
            technique_table = Table(box=box.SIMPLE)
            technique_table.add_column("Technique", style="bright_blue")
            technique_table.add_column("Success Rate", style="green")
            technique_table.add_column("Successes", style="yellow")
            technique_table.add_column("Total Tests", style="magenta")
            
            for technique, stats in success_by_technique.items():
                total = stats['total']
                success = stats['success']
                rate = (success / total) * 100 if total else 0
                technique_table.add_row(
                    technique,
                    f"{rate:.2f}%",
                    str(success),
                    str(total)
                )
            
            self.console.print(technique_table)
        
        # Models tested
        self.console.print(f"\n[bold cyan]Models Tested:[/]")
        for model, count in models.items():
            self.console.print(f"• {model} ({count} prompts)")
        
        # Offer to view or export detailed comparison
        if inquirer.confirm("Generate detailed statistical report?", default=False):
            self._generate_detailed_statistics(results_data)

    def _generate_detailed_statistics(self, results_data: List[Dict]):
        """Generate detailed statistics report with charts and export options"""
        self.console.print("[bold green]Generating detailed statistics...[/]")
        
        try:
            # Prepare timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.exports_dir / f"statistics_report_{timestamp}.txt"
            
            with open(report_path, 'w') as f:
                f.write("DRAVIK BENCHMARK STATISTICS REPORT\n")
                f.write("=================================\n\n")
                
                # Write benchmark details
                f.write("Benchmarks Included:\n")
                for i, result in enumerate(results_data):
                    f.write(f"{i+1}. {result['formatted_timestamp']} - {result['model_tested']}\n")
                f.write("\n")
                
                # Write provider stats
                f.write("Provider Performance:\n")
                f.write("--------------------\n")
                providers_data = {}
                for result in results_data:
                    data = result['data']
                    bypass_success = data.get('bypass_success', {})
                    total_prompts = data.get('total_prompts', 0)
                    
                    for provider, success in bypass_success.items():
                        if provider not in providers_data:
                            providers_data[provider] = []
                        
                        success_rate = (success / total_prompts) * 100 if total_prompts else 0
                        providers_data[provider].append({
                            'timestamp': result['formatted_timestamp'],
                            'success_rate': success_rate,
                            'success': success,
                            'total': total_prompts
                        })
                
                for provider, stats in providers_data.items():
                    f.write(f"\n{provider.upper()}:\n")
                    for stat in stats:
                        f.write(f"  {stat['timestamp']}: {stat['success_rate']:.2f}% " +
                                f"({stat['success']} of {stat['total']})\n")
                
                # Write technique stats if available
                f.write("\nTechnique Effectiveness:\n")
                f.write("----------------------\n")
                techniques_data = {}
                
                # Try to extract technique information from all results
                for result in results_data:
                    data = result['data']
                    detailed_results = data.get('detailed_results', [])
                    
                    for result_item in detailed_results:
                        # Try to identify technique from prompt or metadata
                        prompt = result_item.get('prompt', '')
                        technique = self._identify_technique(prompt, result_item)
                        
                        if technique:
                            if technique not in techniques_data:
                                techniques_data[technique] = {'total': 0, 'success': 0}
                            
                            techniques_data[technique]['total'] += 1
                            apis = result_item.get('apis', {})
                            if any(provider_data.get('success', False) for provider_data in apis.values()):
                                techniques_data[technique]['success'] += 1
                
                for technique, stats in techniques_data.items():
                    success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] else 0
                    f.write(f"{technique}: {success_rate:.2f}% ({stats['success']} of {stats['total']})\n")
                
                f.write("\n\nEnd of Report\n")
            
            self.console.print(f"[green]Detailed statistics exported to {report_path}[/]")
            
        except Exception as e:
            self.console.print(f"[red]Error generating statistics report: {e}[/]")

    def _identify_technique(self, prompt: str, result_item: Dict) -> str:
        """Try to identify the jailbreak technique used in a prompt"""
        # First check if technique is explicitly stored
        if "technique" in result_item:
            return result_item["technique"]
        
        # Look for technique indicators in the prompt
        techniques = {
            "DAN": ["DAN", "do anything now", "can do anything"],
            "Encoding": ["Base64", "leetspeak", "encoded", "decode"],
            "Likert": ["scale from 1-5", "rate this", "rate the following"],
            "Crescendo": ["let's start with", "now, let's make", "for the final part"],
            "Deception": ["for educational purposes", "for a novel", "fictional"],
            "Token Manipulation": ["h-o-w", "t-o", "redacted", "How_to"],
            "Context Hacking": ["SYSTEM OVERRIDE", "ACADEMIC EXCEPTION", "maintenance window"],
            "Role Playing": ["act as", "roleplay", "boundlessAI"],
            "Function Calling": ["/execute", "system.override", "FUNCTION CALL"],
            "Multilingual": ["translate", "foreign language"]
        }
        
        # Check for technique indicators
        for technique, indicators in techniques.items():
            for indicator in indicators:
                if indicator.lower() in prompt.lower():
                    return technique
        
        return "Unknown"

    def export_results(self):
        """Export benchmark results from the database to various formats"""
        results_data = self.list_all_results()
        
        if not results_data:
            return
        
        # Let user select a result to export
        choices = [(f"{r['id']}. {r['formatted_timestamp']} - {r['model_tested']}", r) for r in results_data]
        
        result_questions = [
            inquirer.List(
                'result',
                message="Select a benchmark result to export",
                choices=choices
            )
        ]
        
        result_answers = inquirer.prompt(result_questions)
        if not result_answers:
            return
        
        selected = result_answers['result']
        
        # First analyze and potentially fix the benchmark data 
        fixed_data = self.analyze_benchmark_data(selected['data'])
        
        # Use the helper method to handle the export using the fixed data
        self._export_current_benchmark(fixed_data)

    def analyze_benchmark_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze benchmark data and fix any obvious structural issues
        
        Args:
            data: The benchmark data to analyze
            
        Returns:
            Possibly fixed benchmark data
        """
        self.console.print("[blue]Analyzing benchmark data structure...[/]")
        
        # Check for essential fields
        missing_fields = []
        for field in ['timestamp', 'model_tested', 'total_prompts']:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            self.console.print(f"[yellow]Warning: Benchmark is missing essential fields: {', '.join(missing_fields)}[/]")
        
        # Check for detailed results
        if 'detailed_results' not in data or not data['detailed_results']:
            self.console.print("[yellow]Warning: No detailed results found in benchmark data.[/]")
            
            # Try to reconstruct detailed results from other fields if possible
            if 'prompts' in data and isinstance(data['prompts'], list):
                self.console.print("[green]Found 'prompts' field. Attempting to reconstruct detailed results...[/]")
                
                detailed_results = []
                providers = data.get('providers', ['unknown'])
                
                for i, prompt in enumerate(data['prompts']):
                    result = {'prompt': prompt, 'apis': {}}
                    
                    # Add placeholder responses for each provider
                    for provider in providers:
                        result['apis'][provider] = {
                            'success': False,
                            'response': 'Response data not available',
                            'reconstructed': True
                        }
                    
                    detailed_results.append(result)
                
                data['detailed_results'] = detailed_results
                self.console.print(f"[green]Successfully reconstructed {len(detailed_results)} detailed results.[/]")
        
        # Return the possibly fixed data
        return data

    def export_to_csv(self, result_id: int = None):
        """Export benchmark results to CSV with enhanced metadata"""
        # Get all results or ask user to select one
        results_data = self.list_all_results(include_large_benchmarks=True)
        
        if not results_data:
            self.console.print("[yellow]No benchmark results found to export.[/]")
            return
            
        # If no ID specified, ask user to select one
        selected_result = None
        if result_id is None:
            # Prepare choices
            choices = []
            for result in results_data:
                choice_label = f"ID {result['id']}: {result['formatted_timestamp']} ({result['model_tested']}, {result['total_prompts']} prompts)"
                choices.append((choice_label, result))
                
            choices.append(("Cancel", None))
            
            # Ask user to select
            questions = [
                inquirer.List(
                    'result',
                    message="Select a benchmark result to export",
                    choices=choices
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['result'] is None:
                return
                
            selected_result = answers['result']
        else:
            # Find result by ID
            for result in results_data:
                if result['id'] == result_id:
                    selected_result = result
                    break
                    
            if not selected_result:
                self.console.print(f"[yellow]No benchmark result found with ID {result_id}.[/]")
                return
        
        # Load the full data
        file_path = selected_result['path']
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.console.print(f"[red]Error loading benchmark data: {str(e)}[/]")
            return
            
        # Create export directory if it doesn't exist
        self.exports_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate export filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"benchmark_export_{selected_result['id']}_{timestamp}.csv"
        export_path = self.exports_dir / export_filename
        
        # Extract detailed results
        detailed_results = data.get('detailed_results', [])
        
        if not detailed_results:
            self.console.print("[yellow]No detailed results to export.[/]")
            return
            
        # Write CSV
        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Determine headers
                # Include category if present in any result
                has_category = any('category' in result for result in detailed_results)
                
                headers = ['id', 'prompt', 'model', 'technique']
                if has_category:
                    headers.append('category')
                headers.extend(['evaluation', 'response_time', 'timestamp'])
                
                writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                
                for result in detailed_results:
                    # Sanitize result for CSV
                    sanitized = {
                        'id': result.get('id', ''),
                        'prompt': result.get('prompt', ''),
                        'model': result.get('model', ''),
                        'technique': result.get('technique', 'unknown'),
                        'evaluation': result.get('evaluation', 'UNKNOWN'),
                        'response_time': result.get('response_time', 0),
                        'timestamp': result.get('timestamp', '')
                    }
                    
                    # Add category if we're including it
                    if has_category:
                        sanitized['category'] = result.get('category', 'unknown')
                    
                    writer.writerow(sanitized)
                
            self.console.print(f"[green]✓ Successfully exported to:[/] {export_path}")
            
            # Also create a summary CSV with aggregate metrics
            summary_export_path = self.exports_dir / f"summary_{export_filename}"
            
            # Analyze results by technique and category
            techniques = {}
            categories = {}
            
            for result in detailed_results:
                technique = result.get('technique', 'unknown')
                category = result.get('category', 'unknown')
                evaluation = result.get('evaluation', 'UNKNOWN')
                
                # Track techniques
                if technique not in techniques:
                    techniques[technique] = {'total': 0, 'success': 0}
                techniques[technique]['total'] += 1
                if evaluation == 'SUCCESS':
                    techniques[technique]['success'] += 1
                    
                # Track categories
                if category not in categories:
                    categories[category] = {'total': 0, 'success': 0}
                categories[category]['total'] += 1
                if evaluation == 'SUCCESS':
                    categories[category]['success'] += 1
            
            # Write technique summary
            with open(summary_export_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write benchmark metadata
                writer.writerow(['Benchmark Summary'])
                writer.writerow(['ID', selected_result['id']])
                writer.writerow(['Timestamp', selected_result['formatted_timestamp']])
                writer.writerow(['Model', selected_result['model_tested']])
                writer.writerow(['Total Prompts', selected_result['total_prompts']])
                writer.writerow([])
                
                # Write technique summary
                writer.writerow(['Technique Summary'])
                writer.writerow(['Technique', 'Total', 'Success', 'Rate (%)'])
                
                for technique, stats in sorted(techniques.items(), key=lambda x: x[1]['total'], reverse=True):
                    success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
                    writer.writerow([technique, stats['total'], stats['success'], f"{success_rate:.1f}"])
                
                writer.writerow([])
                
                # Write category summary
                writer.writerow(['Category Summary'])
                writer.writerow(['Category', 'Total', 'Success', 'Rate (%)'])
                
                for category, stats in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
                    success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
                    writer.writerow([category, stats['total'], stats['success'], f"{success_rate:.1f}"])
            
            self.console.print(f"[green]✓ Also exported summary metrics to:[/] {summary_export_path}")
            
        except Exception as e:
            self.console.print(f"[red]Error exporting benchmark data: {str(e)}[/]")
            import traceback
            traceback.print_exc()

    def delete_benchmark_results(self):
        """Delete benchmark results from the database"""
        # First, list available results
        results_data = self.list_all_results()
        
        if not results_data:
            return
        
        # Allow user to select which result to delete
        choices = [(f"{r['id']}. {r['formatted_timestamp']} - {r['model_tested']} ({r['total_prompts']} prompts)", r) for r in results_data]
        choices.append(("Cancel", None))
        
        questions = [
            inquirer.List(
                'result',
                message="Select a benchmark result to DELETE",
                choices=choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or answers['result'] is None:
            return
        
        selected = answers['result']
        
        # Ask for confirmation
        confirm_question = [
            inquirer.Confirm(
                'confirm',
                message=f"Are you sure you want to delete the benchmark from {selected['formatted_timestamp']}?",
                default=False
            )
        ]
        
        confirm_answer = inquirer.prompt(confirm_question)
        if not confirm_answer or not confirm_answer['confirm']:
            self.console.print("[yellow]Deletion cancelled.[/]")
            return
        
        # Delete the selected benchmark
        benchmark_id = selected.get('benchmark_id')
        if not benchmark_id:
            self.console.print("[red]Error: No benchmark ID found for the selected result.[/]")
            return
            
        success = self.db.delete_benchmark_result(benchmark_id)
        
        if success:
            self.console.print(f"[green]Successfully deleted job from {selected['formatted_timestamp']}[/]")
        else:
            self.console.print("[red]Error deleting benchmark result from database.[/]")

def test_db_results(db_handler, console=None):
    """Test function to verify database connection and benchmark results fetching
    
    Args:
        db_handler: Database handler instance
        console: Optional console for output
    """
    if console is None:
        console = Console()
    
    console.print("[bold blue]Testing database connection and benchmark results retrieval...[/]")
    
    viewer = ResultsViewer(db_handler, console, verbose=True)
    results = viewer.list_all_results()
    
    if results:
        console.print(f"[green]✓ Successfully retrieved {len(results)} benchmark results from database.[/]")
    else:
        console.print("[yellow]No benchmark results found in database.[/]")
    
    return results
