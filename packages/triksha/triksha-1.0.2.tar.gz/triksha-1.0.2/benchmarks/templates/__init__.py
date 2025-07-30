"""Prompt templates for generating adversarial examples"""

# Import from advanced_jailbreak_templates.py
from .advanced_jailbreak_templates import (
    generate_adversarial_prompt,
    generate_adversarial_prompts,
    get_template_categories,
    get_technique_description,
    get_harmful_goals
)

# Import from markov_jailbreak_generator.py
from .markov_jailbreak_generator import (
    generate_diverse_adversarial_prompt,
    generate_diverse_adversarial_prompts,
    clean_output_prompt,
    MarkovGenerator
)

# Export the functions
__all__ = [
    # From advanced_jailbreak_templates
    'generate_adversarial_prompt',
    'generate_adversarial_prompts',
    'get_template_categories',
    'get_technique_description',
    'get_harmful_goals',
    
    # From markov_jailbreak_generator
    'generate_diverse_adversarial_prompt',
    'generate_diverse_adversarial_prompts',
    'clean_output_prompt',
    'MarkovGenerator'
]
