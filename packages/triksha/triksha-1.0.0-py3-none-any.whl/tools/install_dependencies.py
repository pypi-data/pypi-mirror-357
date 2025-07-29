#!/usr/bin/env python3
"""
Utility script to install model dependencies for Dravik CLI.

Usage:
  python install_dependencies.py --all
  python install_dependencies.py --model gemma
  python install_dependencies.py --sentencepiece
  python install_dependencies.py --tiktoken
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path
import importlib.util

def check_dependency(package_name: str) -> bool:
    """Check if a package is installed"""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except ModuleNotFoundError:
        return False

def install_package(package_name: str, version: str = None) -> bool:
    """Install a package with pip"""
    try:
        package_spec = package_name
        if version:
            package_spec = f"{package_name}>={version}"
            
        print(f"Installing {package_spec}...")
        cmd = [sys.executable, "-m", "pip", "install", package_spec]
        
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        print(f"Successfully installed {package_spec}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package_spec}: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error installing {package_spec}: {e}")
        return False

def install_sentencepiece():
    """Install SentencePiece and its requirements"""
    if check_dependency("sentencepiece"):
        print("✓ SentencePiece is already installed")
        return True
        
    print("Installing SentencePiece...")
    
    # Try to install directly
    success = install_package("sentencepiece", "0.1.97")
    if success:
        return True
    
    # If failed, try installing system dependencies first on Linux
    if sys.platform.startswith('linux'):
        try:
            print("Attempting to install system dependencies...")
            cmd = [
                "sudo", "apt-get", "update", "&&",
                "sudo", "apt-get", "install", "-y",
                "cmake", "build-essential", "pkg-config", "libgoogle-perftools-dev"
            ]
            subprocess.run(" ".join(cmd), shell=True, check=False)
            
            # Try again
            return install_package("sentencepiece", "0.1.97")
        except:
            print("Could not install system dependencies")
    
    print("Failed to install SentencePiece. Please install it manually:")
    print("  pip install sentencepiece>=0.1.97")
    return False

def install_tiktoken():
    """Install tiktoken for token counting"""
    if check_dependency("tiktoken"):
        print("✓ tiktoken is already installed")
        return True
        
    return install_package("tiktoken", "0.5.0")

def install_model_dependencies(model_name: str):
    """Install dependencies for a specific model"""
    model_name = model_name.lower()
    
    if "gemma" in model_name or "llama" in model_name or "mistral" in model_name or "phi" in model_name:
        if not install_sentencepiece():
            return False
    
    if "qwen" in model_name:
        if not install_tiktoken():
            return False
    
    print(f"Dependencies for {model_name} are now installed")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Install dependencies for Dravik CLI"
    )
    
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Install all dependencies"
    )
    
    parser.add_argument(
        "--model", 
        type=str,
        help="Install dependencies for a specific model"
    )
    
    parser.add_argument(
        "--sentencepiece", 
        action="store_true",
        help="Install SentencePiece library"
    )
    
    parser.add_argument(
        "--tiktoken", 
        action="store_true",
        help="Install tiktoken library"
    )
    
    args = parser.parse_args()
    
    # No args - show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Install all dependencies
    if args.all:
        print("Installing all dependencies...")
        install_sentencepiece()
        install_tiktoken()
        return
        
    # Install model-specific dependencies
    if args.model:
        install_model_dependencies(args.model)
        return
        
    # Install specific packages
    if args.sentencepiece:
        install_sentencepiece()
    
    if args.tiktoken:
        install_tiktoken()

if __name__ == "__main__":
    main()
