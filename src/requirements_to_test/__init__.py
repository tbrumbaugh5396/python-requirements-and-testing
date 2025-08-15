"""
Requirements to Test Generator

A Python GUI application that converts natural language requirements 
into testable checklists and generates corresponding pytest code.
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"
__description__ = "Convert natural language requirements into testable checklists and pytest code"

# Export only lightweight, non-GUI components by default to avoid wx dependency on import
from .parser import RequirementsParser
from .generator import TestCodeGenerator
from .runner import TestRunner

__all__ = [
    'RequirementsParser',
    'TestCodeGenerator',
    'TestRunner'
] 