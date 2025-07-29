#!/usr/bin/env python3
"""
Setup script for Triksha - Advanced LLM Security Testing Framework

This script allows you to install Triksha as a Python package and creates
convenient command-line entry points.

Usage:
  pip install triksha
  pip install -e .  # For development
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Read README file
def get_long_description():
    """Get the long description from README file."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def get_requirements():
    """Get requirements from requirements.txt."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="triksha",
    version="1.0.0",
    author="Triksha Team",
    author_email="team@triksha.ai",
    description="Advanced LLM Security Testing Framework",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/triksha-ai/triksha",
    packages=[
        'cli',
        'cli.commands',
        'cli.commands.benchmark',
        'cli.templates',
        'benchmarks',
        'benchmarks.templates',
        'tools',
        'utils',
        'datasets',
        'tests',
        'training'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0"
        ],
        "kubernetes": [
            "kubernetes>=24.0.0",
            "pyyaml>=6.0"
        ],
        "web": [
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
            "jinja2>=3.1.0"
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "kubernetes>=24.0.0",
            "pyyaml>=6.0",
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
            "jinja2>=3.1.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "triksha=cli.core:main_cli",
            "triksha-cli=cli.dravik_cli:main",
            "triksha-dataset=tools.format_dataset:main",
            "triksha-train=tools.train_model:main",
            "triksha-deps=cli.dependency_cli:main",
            "triksha-verify=verify_env:main",
        ],
    },
    package_data={
        "cli": ["templates/*"],
        "benchmarks": ["templates/*"],
        "": ["*.json", "*.txt", "*.md", "*.yml", "*.yaml"],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Homepage": "https://github.com/triksha-ai/triksha",
        "Documentation": "https://triksha.readthedocs.io/",
        "Repository": "https://github.com/triksha-ai/triksha",
        "Bug Tracker": "https://github.com/triksha-ai/triksha/issues",
    },
    keywords=["llm", "security", "testing", "jailbreak", "red-team", "ai-safety"],
    license="MIT",
) 