"""Commands for adversarial prompt generation in the Dravik CLI"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
import inquirer

# Import the advanced jailbreak templates module with error handling
try:
    from ...benchmarks.templates.advanced_jailbreak_templates import (
        generate_adversarial_prompts,
        get_template_categories,
        get_technique_description,
        BASE_HARMFUL_GOALS,
        get_harmful_goals
    )
except ImportError:
    # Provide fallback implementations
    def generate_adversarial_prompts(count=10, techniques=None):
        return [f"Sample adversarial prompt {i+1}" for i in range(count)]
    
    def get_template_categories():
        return ["ROLEPLAY", "HYPOTHETICAL", "JAILBREAK"]
    
    def get_technique_description(technique):
        return f"Description for {technique} technique"
    
    BASE_HARMFUL_GOALS = ["test goal 1", "test goal 2"]
    
    def get_harmful_goals():
        return BASE_HARMFUL_GOALS

class AdversarialCommands:
    """Commands for working with adversarial prompts"""
    
    def __init__(self, console=None, config=None):
        """Initialize with console"""
        self.console = console or Console()
        self.config = config or {}
        
        # Setup default paths
        self.output_dir = Path(self.config.get('adversarial_output_dir', 
                                              Path.home() / "dravik" / "adversarial_prompts"))
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def quick_adversarial_prompts(self):
        """Generate adversarial prompts quickly and allow export"""
        self.console.print(Panel.fit(
            "[bold]Quick Adversarial Prompts[/]\n\n"
            "Generate adversarial prompts based on advanced jailbreak templates.\n"
            "These prompts can be used for testing model safeguards.",
            title="[red]ADVERSARIAL PROMPT GENERATOR[/]",
            border_style="red"
        ))
        
        try:
            # Ask for number of prompts to generate
            count_question = [
                inquirer.Text(
                    'count',
                    message="How many adversarial prompts do you want to generate?",
                    default="10",
                    validate=lambda _, x: x.isdigit() and int(x) > 0
                )
            ]
            
            count_answer = inquirer.prompt(count_question)
            if not count_answer:
                self.console.print("[yellow]Cancelled.[/]")
                return
            
            count = int(count_answer['count'])
            
            # Ask for specific techniques
            technique_categories = get_template_categories()
            
            # Automatically use all individual techniques (excluding ALL_TECHNIQUES itself)
            all_individual_techniques = [t for t in technique_categories if t != "ALL_TECHNIQUES"]
            techniques = all_individual_techniques
            
            self.console.print(f"[green]✓ Using all {len(all_individual_techniques)} individual techniques for comprehensive testing[/]")
            
            # Display which techniques will be used
            self.console.print("[cyan]Techniques to be used:[/]")
            for tech in all_individual_techniques:
                description = get_technique_description(tech)
                self.console.print(f"  • [cyan]{tech}[/]: {description}")
            self.console.print()
            
            # Generate the prompts
            self.console.print(f"\n[bold]Generating {count} adversarial prompts using advanced templates...[/]")
            
            prompts = generate_adversarial_prompts(count=count, techniques=techniques)
            
            # Convert prompts to required format for display and export
            formatted_prompts = []
            for i, prompt in enumerate(prompts):
                formatted_prompts.append({
                    "id": i + 1,
                    "prompt": prompt,
                    "technique": techniques[i % len(techniques)] if techniques else "mixed",
                    "topic": "generated"
                })
            
            # Display generated prompts
            self._display_prompts(formatted_prompts)
            
            # Ask if user wants to export
            export_question = [
                inquirer.Confirm(
                    'export',
                    message="Do you want to export these prompts?",
                    default=True
                )
            ]
            
            export_answer = inquirer.prompt(export_question)
            if export_answer and export_answer['export']:
                self._export_prompts(formatted_prompts)
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled.[/]")
        except Exception as e:
            self.console.print(f"[red]Error generating adversarial prompts: {e}[/]")

    def _display_prompts(self, prompts: List[Dict[str, Any]]):
        """Display the generated prompts"""
        self.console.print(f"\n[bold green]Successfully generated {len(prompts)} adversarial prompts:[/]")
        
        # Create table
        table = Table(title=f"Adversarial Prompts ({len(prompts)})")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Prompt", style="white", overflow="fold")
        table.add_column("Technique", style="yellow")
        
        # Add rows with truncated prompts
        for prompt in prompts:
            # Truncate prompt text if it's too long
            prompt_text = prompt['prompt']
            if len(prompt_text) > 100:
                prompt_text = prompt_text[:97] + "..."
                
            table.add_row(
                str(prompt['id']),
                prompt_text,
                prompt['technique']
            )
        
        self.console.print(table)
        
        # Show a few full prompts as examples
        self.console.print("\n[bold]Example prompts (full text):[/]")
        samples = min(3, len(prompts))
        for i in range(samples):
            self.console.print(f"\n[bold cyan]Prompt #{prompts[i]['id']}:[/]")
            self.console.print(prompts[i]['prompt'])

    def _export_prompts(self, prompts: List[Dict[str, Any]]):
        """Handle exporting prompts"""
        # Ask for export format
        format_question = [
            inquirer.List(
                'format',
                message="Select export format",
                choices=[
                    ('JSON', 'json'),
                    ('CSV', 'csv')
                ]
            )
        ]
        
        format_answer = inquirer.prompt(format_question)
        if not format_answer:
            self.console.print("[yellow]Export cancelled.[/]")
            return
        
        export_format = format_answer['format']
        
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"adversarial_prompts_{timestamp}.{export_format}"
        default_path = str(self.output_dir / default_filename)
        
        # Ask for filename
        filename_question = [
            inquirer.Text(
                'filename',
                message=f"Enter filename for {export_format.upper()} export",
                default=default_path
            )
        ]
        
        filename_answer = inquirer.prompt(filename_question)
        if not filename_answer:
            self.console.print("[yellow]Export cancelled.[/]")
            return
        
        output_path = filename_answer['filename']
        
        # Ensure extension is correct
        if not output_path.endswith(f".{export_format}"):
            output_path = f"{output_path}.{export_format}"
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Export based on format
        success = False
        try:
            if export_format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "prompts": prompts,
                        "count": len(prompts),
                        "type": "adversarial_prompts",
                        "generated_at": datetime.now().isoformat()
                    }, f, indent=2)
                success = True
            elif export_format == 'csv':
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['id', 'prompt', 'technique', 'topic'])
                    for prompt in prompts:
                        writer.writerow([
                            prompt.get('id', ''),
                            prompt.get('prompt', ''),
                            prompt.get('technique', ''),
                            prompt.get('topic', '')
                        ])
                success = True
        except Exception as e:
            self.console.print(f"[red]Error exporting prompts: {str(e)}[/]")
            return
        
        if success:
            self.console.print(f"[green]Successfully exported {len(prompts)} prompts to {output_path}[/]")
        else:
            self.console.print(f"[red]Failed to export prompts to {output_path}[/]")

    def list_jailbreak_techniques(self):
        """List available jailbreak techniques"""
        self.console.print(Panel.fit(
            "[bold]Jailbreak Techniques[/]\n\n"
            "List of available techniques for generating adversarial prompts.",
            title="[blue]TEMPLATE CATEGORIES[/]",
            border_style="blue"
        ))
        
        table = Table(title="Available Jailbreak Techniques")
        table.add_column("Technique", style="cyan")
        table.add_column("Description", style="white")
        
        for technique in get_template_categories():
            table.add_row(technique, get_technique_description(technique))
        
        self.console.print(table)
