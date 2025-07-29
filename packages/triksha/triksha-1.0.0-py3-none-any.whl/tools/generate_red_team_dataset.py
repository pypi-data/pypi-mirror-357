#!/usr/bin/env python3
"""
Generate a synthetic dataset of red teaming prompts using Markov-based generators.
This tool creates diverse adversarial prompts for model evaluation and training.
"""

import os
import sys
import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path to allow imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import jailbreak template generators
try:
    from benchmarks.templates import (
        generate_adversarial_prompt, 
        generate_adversarial_prompts,
        get_template_categories,
        get_harmful_goals
    )
    
    # Import Markov-based generators
    try:
        from benchmarks.templates.markov_jailbreak_generator import (
            generate_diverse_adversarial_prompt,
            generate_diverse_adversarial_prompts
        )
        HAS_ADVANCED_TEMPLATES = True
    except ImportError:
        HAS_ADVANCED_TEMPLATES = False
        print("Warning: Markov-based generators not available. Using standard generators only.")
except ImportError:
    print("Error: Could not import template generators. Make sure you're running from the project root.")
    sys.exit(1)

def generate_red_team_dataset(
    output_path: str,
    num_samples: int = 1000,
    techniques: List[str] = None,
    harmful_goals: List[str] = None,
    format_type: str = "jsonl",
    use_markov: bool = True,
    add_metadata: bool = True,
    seed: int = None
) -> None:
    """
    Generate a synthetic dataset of red team prompts.
    
    Args:
        output_path: Path to save the dataset
        num_samples: Number of samples to generate
        techniques: List of techniques to use (None = all)
        harmful_goals: List of harmful goals to use (None = default list)
        format_type: Output format (jsonl, json, csv)
        use_markov: Whether to use Markov-based generation (if available)
        add_metadata: Whether to add metadata to each sample
        seed: Random seed for reproducibility
    """
    # Set random seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Get available techniques
    all_techniques = get_template_categories()
    
    # Filter techniques if specified
    if techniques:
        techniques = [t for t in techniques if t in all_techniques]
        if not techniques:
            print("Error: No valid techniques specified")
            return
    else:
        techniques = all_techniques
    
    # Get harmful goals
    if not harmful_goals:
        harmful_goals = get_harmful_goals()
    
    # Create the dataset
    dataset = []
    
    print(f"Generating {num_samples} red teaming prompts...")
    
    # Determine whether to use Markov or standard generators
    generator_fn = generate_diverse_adversarial_prompts if (use_markov and HAS_ADVANCED_TEMPLATES) else generate_adversarial_prompts
    
    # Generate in batches to show progress
    batch_size = min(100, num_samples)
    for i in range(0, num_samples, batch_size):
        current_batch_size = min(batch_size, num_samples - i)
        
        # Print progress
        print(f"Generating samples {i+1}-{i+current_batch_size} of {num_samples}...")
        
        # Generate a batch of prompts
        prompts_data = generator_fn(count=current_batch_size, techniques=techniques)
        
        # Organize into dataset entries
        if use_markov and HAS_ADVANCED_TEMPLATES and generator_fn == generate_diverse_adversarial_prompts:
            # New format with technique information
            for prompt_data in prompts_data:
                entry = {"prompt": prompt_data["prompt"]}
                
                # Add metadata if requested
                if add_metadata:
                    # Use the actual technique from the generator
                    technique = prompt_data.get("technique", random.choice(techniques))
                    
                    # Use the actual base goal from the generator
                    harmful_goal = prompt_data.get("base_goal", random.choice(harmful_goals))
                    
                    # Add metadata
                    entry["metadata"] = {
                        "technique": technique,
                        "harmful_goal": harmful_goal,
                        "generation_method": "markov",
                        "generator_version": "1.0",
                        "timestamp": datetime.now().isoformat()
                    }
                
                dataset.append(entry)
        else:
            # Standard format with just prompt strings
            for prompt in prompts_data:
                entry = {"prompt": prompt}
                
                # Add metadata if requested
                if add_metadata:
                    # Extract technique from prompt if possible (basic heuristic)
                    technique = None
                    for t in techniques:
                        if t.lower() in prompt.lower():
                            technique = t
                            break
                    
                    if not technique:
                        technique = random.choice(techniques)
                    
                    # Extract harmful goal if possible (basic heuristic)
                    harmful_goal = None
                    for goal in harmful_goals:
                        if goal.lower() in prompt.lower():
                            harmful_goal = goal
                            break
                    
                    if not harmful_goal:
                        harmful_goal = random.choice(harmful_goals)
                    
                    # Add metadata
                    entry["metadata"] = {
                        "technique": technique,
                        "harmful_goal": harmful_goal,
                        "generation_method": "standard",
                        "generator_version": "1.0",
                        "timestamp": datetime.now().isoformat()
                    }
                
                dataset.append(entry)
    
    # Save the dataset
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    if format_type == "jsonl":
        with open(output_path, "w") as f:
            for entry in dataset:
                f.write(json.dumps(entry) + "\n")
    elif format_type == "json":
        with open(output_path, "w") as f:
            json.dump({"data": dataset}, f, indent=2)
    elif format_type == "csv":
        import csv
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            fields = ["prompt"]
            if add_metadata:
                fields.extend(["technique", "harmful_goal", "generation_method"])
            writer.writerow(fields)
            
            # Write data
            for entry in dataset:
                row = [entry["prompt"]]
                if add_metadata:
                    row.extend([
                        entry["metadata"]["technique"],
                        entry["metadata"]["harmful_goal"],
                        entry["metadata"]["generation_method"]
                    ])
                writer.writerow(row)
    else:
        print(f"Error: Unsupported format type '{format_type}'")
        return
    
    print(f"Dataset saved to {output_path}")
    print(f"Generated {len(dataset)} samples using {'Markov-based' if (use_markov and HAS_ADVANCED_TEMPLATES) else 'standard'} generation")

def main():
    parser = argparse.ArgumentParser(description="Generate a synthetic red team prompt dataset")
    parser.add_argument("--output", "-o", type=str, default="datasets/red_team_synthetic.jsonl",
                        help="Path to save the dataset")
    parser.add_argument("--num-samples", "-n", type=int, default=1000,
                        help="Number of samples to generate")
    parser.add_argument("--techniques", "-t", type=str, nargs="*",
                        help="Techniques to use (space-separated)")
    parser.add_argument("--format", "-f", type=str, default="jsonl",
                        choices=["jsonl", "json", "csv"],
                        help="Output format")
    parser.add_argument("--no-markov", action="store_true",
                        help="Disable Markov-based generation (use standard only)")
    parser.add_argument("--no-metadata", action="store_true",
                        help="Exclude metadata from dataset")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--list-techniques", action="store_true",
                        help="List available techniques and exit")
    
    args = parser.parse_args()
    
    # List techniques if requested
    if args.list_techniques:
        print("Available techniques:")
        for technique in get_template_categories():
            print(f"  - {technique}")
        sys.exit(0)
    
    # Generate the dataset
    generate_red_team_dataset(
        output_path=args.output,
        num_samples=args.num_samples,
        techniques=args.techniques,
        format_type=args.format,
        use_markov=not args.no_markov,
        add_metadata=not args.no_metadata,
        seed=args.seed
    )

if __name__ == "__main__":
    main() 