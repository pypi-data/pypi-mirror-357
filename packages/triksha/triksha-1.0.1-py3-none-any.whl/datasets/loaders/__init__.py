"""
Dataset Loaders for Dravik
"""

from .base_loader import BaseLoader
from .huggingface_loader import HuggingFaceLoader
from .file_loader import FileLoader
from .url_loader import UrlLoader

__all__ = [
    'BaseLoader',
    'HuggingFaceLoader',
    'FileLoader',
    'UrlLoader'
]
