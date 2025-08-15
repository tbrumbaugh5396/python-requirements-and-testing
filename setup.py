#!/usr/bin/env python3
"""
Setup script for requirements-to-test.
"""

import os
from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')


# Read requirements
def read_requirements(filename):
    """Read requirements from file."""

    requirements_file = this_directory / filename
    if requirements_file.exists():
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                # Skip empty lines, comments, and -r references
                if line and not line.startswith('#') and not line.startswith('-r'):
                    requirements.append(line)
            return requirements
    return []


# Read version from the package __init__.py in src layout
def get_version():
    """Extract version from src/requirements_to_test/__init__.py."""
    version_file = this_directory / "src" / "requirements_to_test" / "__init__.py"
    if version_file.exists():
        import re
        content = version_file.read_text(encoding='utf-8')
        version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", content)
        if version_match:
            return version_match.group(1)
    return "1.0.0"

setup(
    name="requirements-to-test",
    version=get_version(),
    author="AI Assistant",
    author_email="ai@example.com",
    description="Convert natural language requirements into testable checklists and generate pytest code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/requirements-to-test",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/requirements-to-test/issues",
        "Source": "https://github.com/yourusername/requirements-to-test",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=[],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Text Processing :: Linguistic",
    ],
    keywords="testing requirements pytest gui wxpython test-generation",
    python_requires=">=3.7",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "gui": ["wxPython>=4.2.0"],
    },
    entry_points={
        "console_scripts": [
            # Console launcher that starts the GUI
            "requirements-to-test=requirements_to_test.gui:main",
        ],
        "gui_scripts": [
            # Native GUI entry point (on Windows it hides the console)
            "requirements-to-test-gui=requirements_to_test.gui:main",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
) 