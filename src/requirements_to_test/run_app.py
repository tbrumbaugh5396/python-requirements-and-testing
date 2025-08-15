#!/usr/bin/env python3
"""
Launcher script for Requirements to Test Generator
"""

if __name__ == '__main__':
    try:
        try:
            # Prefer relative import when running as part of the package
            from .requirements_to_test_gui import RequirementsApp
        except Exception:
            # Fallback for running this file directly
            from requirements_to_test.requirements_to_test_gui import RequirementsApp
        app = RequirementsApp()
        app.MainLoop()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install required dependencies:")
        print("pip3 install -r requirements.txt")
    except Exception as e:
        print(f"Error running application: {e}")
        print("Please check that all dependencies are properly installed.")