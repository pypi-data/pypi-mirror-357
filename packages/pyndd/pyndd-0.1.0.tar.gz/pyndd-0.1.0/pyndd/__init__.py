"""
PynDD - Python Dynamic DSL for data access and manipulation.

A lightweight library for dynamic data structure parsing and manipulation
using a custom DSL syntax.
"""

from .parser import parse, translate

__version__ = "0.1.0"
__all__ = ["parse", "translate"]