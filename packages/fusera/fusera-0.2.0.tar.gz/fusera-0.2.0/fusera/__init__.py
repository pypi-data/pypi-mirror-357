# ABOUTME: Fusera SDK package initialization and public API exports
# ABOUTME: Exposes main compilation functions for PyTorch model compilation service

from .compile import compile

__version__ = "0.2.0"
__all__ = ["compile"]  # Remove status, get, wait_for