"""
Triksha CLI Commands Package

This package contains all command-line interface modules for the Triksha framework.
"""

__version__ = "1.0.0"

# Import command modules with error handling
try:
    from .adversarial_commands import AdversarialCommands
except ImportError:
    AdversarialCommands = None

try:
    from .dataset import DatasetCommands
except ImportError:
    DatasetCommands = None

try:
    from .training_commands import TrainingCommands
except ImportError:
    TrainingCommands = None

try:
    from .benchmark.command import BenchmarkCommands
except ImportError:
    BenchmarkCommands = None

__all__ = [
    'AdversarialCommands',
    'DatasetCommands', 
    'TrainingCommands',
    'BenchmarkCommands'
]
