# Dynamic Adversarial Prompt Generation

This document explains the enhanced adversarial prompt generation capabilities using Markov chains and dynamic template recombination.

## Overview

The new `markov_jailbreak_generator.py` module introduces a more sophisticated approach to generating diverse, effective jailbreak prompts. Instead of relying solely on fixed templates, it dynamically creates novel templates by:

1. **Markov Chain Text Generation**: Learning patterns from existing templates and generating new text with similar stylistic characteristics
2. **Template Fragment Extraction**: Breaking down existing templates into reusable components
3. **Dynamic Recombination**: Intelligently combining fragments to create coherent, novel templates
4. **Semantic Awareness**: Ensuring that key phrases essential to each technique's effectiveness are preserved

## Key Features

### Markov Chain Text Generation

The `MarkovGenerator` class creates statistically-informed templates based on the n-gram patterns in existing templates. This generates naturally flowing text that mimics the style of successful jailbreak prompts while introducing novelty.

### Template Component Analysis

Each existing template is analyzed and broken down into components:
- Intros
- Descriptions
- Requests
- Justifications
- Authority statements
- Closing statements

These components are then recombined in novel ways while ensuring coherence.

### Additional Diversity Components

The module contains expanded dictionaries of technique-specific components:

- **DAN**: More diverse persona names, liberation phrases, and capability descriptions
- **LIKERT**: Various scale types, evaluation requests, and justification phrasings
- **ENCODING**: Different game framing narratives and encoding type descriptions
- **CONTEXT_HACKING**: Extended system directives, authorization codes, and security contexts

### Advanced Cleaning and Output Processing

The `clean_output_prompt` function applies sophisticated text processing to:
- Remove redundancy and repetition
- Fix formatting issues
- Eliminate template artifacts
- Ensure proper capitalization and punctuation
- Remove semantically duplicate content
- Fix Markov-induced spelling and grammar errors

## Usage

```python
from benchmarks.templates import generate_diverse_adversarial_prompts

# Generate 5 diverse prompts
prompts = generate_diverse_adversarial_prompts(count=5)

# Generate prompts with specific techniques
from benchmarks.templates import get_template_categories
techniques = ["DAN", "ENCODING", "CONTEXT_HACKING"]
prompts = generate_diverse_adversarial_prompts(count=3, techniques=techniques)
```

## Command-line Testing

You can use the included test script to compare the classic and Markov-based generation:

```bash
python test_markov_generator.py --count 5 --compare
```

Or just generate with the new method:

```bash
python test_markov_generator.py --count 10
```

Specify techniques with:

```bash
python test_markov_generator.py --techniques DAN ENCODING LIKERT
```

## Benefits Over Classic Templates

1. **Increased Diversity**: Generates more varied prompts, reducing the chance of patterns being detected
2. **Reduced Repetition**: Eliminates common redundancies in generated prompts
3. **Natural Language Flow**: Produces more natural-sounding text that may bypass filters
4. **Evolving Content**: Since each generation is different, defenses can't simply block fixed patterns
5. **Adaptive Integration**: Still uses the proven transformation logic from the original module

## Algorithm Details

The generation process follows these steps:

1. Select a jailbreak technique (e.g., DAN, LIKERT, ENCODING)
2. Generate a diverse template using Markov chains and fragment recombination
3. Apply technique-specific transformations to the base prompt
4. Clean the output to remove artifacts and redundancies
5. Verify and fix the final prompt for coherence and effectiveness

By dynamically generating the template structure itself, this approach creates significantly more diverse adversarial prompts while maintaining their effectiveness. 