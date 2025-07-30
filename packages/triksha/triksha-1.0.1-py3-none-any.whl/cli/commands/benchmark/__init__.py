"""
Benchmark Commands Package

This package contains benchmark-related commands and utilities for the Triksha framework.
"""

__version__ = "1.0.0"

try:
    from .command import BenchmarkCommands, BenchmarkUI
except ImportError:
    BenchmarkCommands = None
    BenchmarkUI = None

try:
    from .runners import APIBenchmarkRunner, KubernetesBenchmarkManager
except ImportError:
    APIBenchmarkRunner = None
    KubernetesBenchmarkManager = None

try:
    from .results import ResultsViewer
except ImportError:
    ResultsViewer = None

__all__ = [
    'BenchmarkCommands',
    'BenchmarkUI',
    'APIBenchmarkRunner',
    'KubernetesBenchmarkManager',
    'ResultsViewer'
]
