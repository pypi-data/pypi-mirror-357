#!/usr/bin/env python3
"""
Tool for formatting datasets for different model architectures.

Usage:
  python format_dataset.py --input input.json --output formatted.json --model llama3
  python format_dataset.py --input input.json --analyze
  python format_dataset.py --create-adversarial --count 100 --output adversarial.json
"""

import argparse
import json
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.dataset_processor import DatasetProcessor
from utils.dataset_formatter import DatasetFormatter

def main():
    """Main entry point for the script"""
    console = Console()
    
    parser = argparse.ArgumentParser(
        description="Format datasets for different model architectures"
    )
    
    # File input/output options
    parser.add_argument(
        "--input", 
        type=str, 
        help="Path to input dataset file"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        help="Path to save formatted dataset"
    )
    
    # Model options
    parser.add_argument(
        "--model", 
        type=str, 
        choices=["llama2", "llama3", "mistral", "mixtral", "vicuna", "gemma", "phi", "default", "custom"],
        default="default",
        help="Model architecture to format for"
    )
    
    # Prompt field
    parser.add_argument(
        "--prompt-field", 
        type=str, 
        help="Field containing prompts/instructions (auto-detect if not specified)"
    )
    
    # Response style
    parser.add_argument(
        "--response-style", 
        type=str, 
        choices=["varied", "consistent", "strict"],
        default="varied",
        help="Style of responses for adversarial prompts"
    )
    
    # Analysis mode
    parser.add_argument(
        "--analyze", 
        action="store_true",
        help="Analyze dataset without formatting"
    )
    
    # Create adversarial dataset
    parser.add_argument(
        "--create-adversarial", 
        action="store_true",
        help="Create synthetic adversarial dataset"
    )
    
    parser.add_argument(
        "--count", 
        type=int, 
        default=100,
        help="Number of synthetic examples to generate"
    )
    
    # Preview mode
    parser.add_argument(
        "--preview", 
        action="store_true",
        help="Preview examples from dataset"
    )
    
    parser.add_argument(
        "--samples", 
        type=int, 
        default=3,
        help="Number of samples to preview"
    )
    
    # Detect adversarial prompts
    parser.add_argument(
        "--detect-adversarial", 
        action="store_true",
        help="Detect adversarial prompts in dataset"
    )
    
    args = parser.parse_args()
    
    # Create adversarial dataset
    if args.create_adversarial:
        console.print(Panel(f"Creating synthetic adversarial dataset with {args.count} examples", 
                          style="green", title="ADVERSARIAL DATASET"))
        
        if not args.output:
            console.print("[yellow]No output path specified. Use --output to save dataset.[/]")
            return
            
        # Create dataset
        dataset = DatasetProcessor.create_adversarial_dataset(
            count=args.count,
            model_name=args.model,
            output_path=args.output
        )
        
        console.print(f"[green]Created adversarial dataset with {len(dataset['examples'])} examples[/]")
        console.print(f"Saved to: {args.output}")
        
        # Show sample
        if dataset['examples']:
            console.print("\n[bold]Sample example:[/]")
            example = dataset['examples'][0]
            console.print(f"[bold]Input:[/] {example['input'][:100]}...")
            console.print(f"[bold]Output:[/] {example['output'][:100]}...")
        
        return
    
    # Handle input validation
    if not args.input and not args.create_adversarial:
        parser.print_help()
        return
    
    # Analyze mode
    if args.analyze:
        console.print(Panel(f"Analyzing dataset: {args.input}", style="blue", title="DATASET ANALYSIS"))
        
        # Run analysis
        analysis = DatasetProcessor.analyze_dataset(args.input)
        
        if "error" in analysis:
            console.print(f"[red]Error: {analysis['error']}[/]")
            return
            
        # Print analysis results
        console.print(f"[bold]File:[/] {analysis.get('filename')}")
        console.print(f"[bold]Size:[/] {analysis.get('size_mb', 0):.2f} MB")
        
        if analysis.get('type') == 'list':
            console.print(f"[bold]Type:[/] List with {analysis.get('count', 0)} items")
            
            if 'fields' in analysis:
                console.print(f"[bold]Fields:[/] {', '.join(analysis.get('fields', []))}")
                
            if 'likely_prompt_field' in analysis:
                console.print(f"[bold]Detected prompt field:[/] {analysis.get('likely_prompt_field')}")
                
        elif analysis.get('type') == 'dictionary':
            console.print(f"[bold]Type:[/] Dictionary with keys: {', '.join(analysis.get('keys', []))}")
            
            if 'examples_count' in analysis:
                console.print(f"[bold]Examples:[/] {analysis.get('examples_count', 0)}")
                
            if 'example_fields' in analysis:
                console.print(f"[bold]Example fields:[/] {', '.join(analysis.get('example_fields', []))}")
                
            if 'likely_prompt_field' in analysis:
                console.print(f"[bold]Detected prompt field:[/] {analysis.get('likely_prompt_field')}")
                
        # Show adversarial content info if available
        if 'adversarial_count' in analysis:
            console.print(f"[bold]Adversarial content:[/] {analysis.get('adversarial_count', 0)} examples " +
                       f"({analysis.get('adversarial_percentage', 0):.1f}%)")
        
        return
    
    # Preview mode
    if args.preview:
        console.print(Panel(f"Previewing dataset: {args.input}", style="cyan", title="DATASET PREVIEW"))
        
        # Get samples
        samples = DatasetProcessor.preview_dataset(args.input, args.samples)
        
        if not samples or "error" in samples[0]:
            console.print(f"[red]Error: {samples[0].get('error', 'Unknown error')}[/]")
            return
            
        # Print samples
        for i, sample in enumerate(samples):
            console.print(f"\n[bold]Sample {i+1}:[/]")
            
            # Print each field
            for field, value in sample.items():
                if isinstance(value, str):
                    # Truncate long strings
                    if len(value) > 100:
                        value = value[:100] + "..."
                        
                console.print(f"[bold]{field}:[/] {value}")
                
        return
    
    # Detect adversarial prompts
    if args.detect_adversarial:
        console.print(Panel(f"Detecting adversarial prompts in: {args.input}", 
                          style="yellow", title="ADVERSARIAL DETECTION"))
        
        # Run detection
        result = DatasetProcessor.detect_adversarial_prompts(args.input, args.prompt_field)
        
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/]")
            return
            
        # Print results
        console.print(f"[bold]Total examples:[/] {result.get('total_examples', 0)}")
        console.print(f"[bold]Adversarial examples:[/] {result.get('adversarial_count', 0)} " +
                    f"({result.get('adversarial_percentage', 0):.1f}%)")
        console.print(f"[bold]Benign examples:[/] {result.get('benign_count', 0)}")
        console.print(f"[bold]Using prompt field:[/] {result.get('prompt_field')}")
        
        # Show some adversarial examples
        if result.get('sample_adversarial'):
            console.print("\n[bold]Sample adversarial prompts:[/]")
            
            for i, example in enumerate(result.get('sample_adversarial', [])):
                prompt = example.get(result.get('prompt_field', ''))
                if prompt:
                    if len(prompt) > 100:
                        prompt = prompt[:100] + "..."
                    console.print(f"{i+1}. {prompt}")
        
        return
    
    # Normal formatting mode
    console.print(Panel(f"Formatting dataset: {args.input}", style="green", title="DATASET FORMATTING"))
    
    # Figure out prompt field if not specified
    prompt_field = args.prompt_field
    if not prompt_field:
        # Run analysis to auto-detect
        analysis = DatasetProcessor.analyze_dataset(args.input)
        if "error" not in analysis and "likely_prompt_field" in analysis:
            prompt_field = analysis.get("likely_prompt_field")
            console.print(f"[green]Auto-detected prompt field: {prompt_field}[/]")
        
        if not prompt_field:
            console.print("[red]Could not auto-detect prompt field. Please specify with --prompt-field.[/]")
            return
    
    # Format dataset
    console.print(f"Formatting dataset for {args.model} model architecture...")
    console.print(f"Using prompt field: {prompt_field}")
    console.print(f"Response style: {args.response_style}")
    
    formatted_dataset = DatasetProcessor.format_dataset(
        input_path=args.input,
        prompt_field=prompt_field,
        model_name=args.model,
        response_style=args.response_style,
        output_path=args.output
    )
    
    if "error" in formatted_dataset:
        console.print(f"[red]Error: {formatted_dataset['error']}[/]")
        return
        
    # Show results
    example_count = len(formatted_dataset["examples"])
    console.print(f"[green]Successfully formatted {example_count} examples![/]")
    
    if args.output:
        console.print(f"[green]Formatted dataset saved to {args.output}[/]")
    else:
        # Print a sample formatted example
        if formatted_dataset["examples"]:
            example = formatted_dataset["examples"][0]
            console.print("\n[bold]Sample formatted example:[/]")
            console.print(f"[bold]Input:[/]\n{example['input'][:200]}..." if len(example['input']) > 200 else example['input'])
            console.print(f"[bold]Output:[/]\n{example['output'][:200]}..." if len(example['output']) > 200 else example['output'])

if __name__ == "__main__":
    main()
