                "prompt_count": prompt_count,
                "techniques": techniques
            }
            
            # Create a dataset with diverse adversarial prompts using markov chains
            try:
                # Import the markov jailbreak generator
                from benchmarks.templates.markov_jailbreak_generator import generate_diverse_adversarial_prompts
                
                # Generate diverse prompts
                diverse_prompts = generate_diverse_adversarial_prompts(
                    count=prompt_count, 
                    techniques=techniques
                )
                
                # Create the dataset structure
                dataset = {
                    "name": "Advanced Adversarial Templates with Markov Generation",
                    "description": "Dynamic adversarial prompts generated using Markov chains and advanced jailbreak templates",
                    "examples": [],
                    "metadata": {
                        "generation_method": "markov",
                        "generation_time": datetime.now().isoformat(),
                        "count": len(diverse_prompts)
                    }
                }
                
                # Process the generated prompts
                for i, prompt in enumerate(diverse_prompts):
                    # Extract category based on content patterns
                    prompt_category = self._evaluate_prompt_quality(prompt, "general")
                    
                    # Add to dataset
                    dataset["examples"].append({
                        "id": f"advanced_prompt_{i+1}",
                        "prompt": prompt,
                        "technique": "markov_diverse",
                        "category": prompt_category,
                        "harmful_goal": prompt_category
                    })
            except Exception as e:
                self.console.print(f"[yellow]Error generating Markov-based prompts: {str(e)}. Using advanced templates instead.[/]")
                
                # Create a minimal dataset as fallback
                from benchmarks.templates.advanced_jailbreak_templates import generate_adversarial_prompts
                prompts = generate_adversarial_prompts(count=prompt_count)
                
                # Create the dataset structure
                dataset = {
                    "name": "Advanced Adversarial Templates",
                    "description": "Adversarial prompts from advanced templates",
                    "examples": [{"prompt": p, "technique": "advanced_template"} for p in prompts],
                    "metadata": {
                        "generation_method": "advanced_templates",
                        "generation_time": datetime.now().isoformat(),
                        "count": len(prompts)
                    }
                }
            
            # Run the benchmark 