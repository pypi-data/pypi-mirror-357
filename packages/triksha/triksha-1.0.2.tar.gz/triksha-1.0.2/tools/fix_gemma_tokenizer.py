#!/usr/bin/env python3
"""
Utility to fix issues with Gemma tokenizer imports

Usage:
  python fix_gemma_tokenizer.py

This script attempts to fix issues with the Gemma tokenizer by reinstalling/updating
transformers to a version that properly supports Gemma, especially Gemma-3 models.
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Fix Gemma tokenizer import issues"
    )
    
    parser.add_argument(
        "--verbose", 
        action='store_true',
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Setup logging based on verbosity
    import logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Import our fix utility
    from utils.transformers_fix import fix_transformers_installation
    
    print("Fixing Gemma tokenizer import issues...")
    success = fix_transformers_installation()
    
    if success:
        print("[SUCCESS] Fixed Gemma tokenizer issues!")
        print("You should now be able to use Gemma models, including Gemma-3")
    else:
        print("[FAILURE] Could not automatically fix Gemma tokenizer issues")
        print("Please try the following manual steps:")
        print("")
        print("1. Update transformers to the latest version:")
        print("   pip install --upgrade transformers")
        print("")
        print("2. If that doesn't work, install directly from GitHub:")
        print("   pip install --upgrade git+https://github.com/huggingface/transformers.git")
        print("")
        print("3. Make sure you also have sentencepiece installed:")
        print("   pip install sentencepiece>=0.1.99")

if __name__ == "__main__":
    main()
