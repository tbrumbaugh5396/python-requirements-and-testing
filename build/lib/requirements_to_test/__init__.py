"""
Requirements to Test Generator

A Python GUI application that converts natural language requirements 
into testable checklists and generates corresponding pytest code.
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"
__description__ = "Convert natural language requirements into testable checklists and pytest code"

from .gui import RequirementsApp, MainFrame
from .parser import RequirementsParser
from .generator import TestCodeGenerator

__all__ = [
    'RequirementsApp',
    'MainFrame', 
    'RequirementsParser',
    'TestCodeGenerator'
] 