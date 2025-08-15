"""
Command line entry point for Requirements to Test Generator.
Supports both:
- python -m requirements_to_test
- python src/requirements_to_test/__main__.py
"""

try:
    # When executed as a module: python -m requirements_to_test
    from .gui import main
except Exception:
    # When executed directly as a script
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from requirements_to_test.gui import main

if __name__ == '__main__':
    main()