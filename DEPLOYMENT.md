# Deployment Guide for Requirements to Test Generator

This guide walks you through packaging and deploying the Requirements to Test Generator to PyPI.

## Prerequisites

1. **Python 3.7+** installed
2. **PyPI account** (create at https://pypi.org/account/register/)
3. **TestPyPI account** (create at https://test.pypi.org/account/register/) - recommended for testing
4. **API tokens** for both PyPI and TestPyPI (recommended over passwords)

## Setup API Tokens (Recommended)

### For PyPI:
1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens" and click "Add API token"
3. Set scope to "Entire account" or specific project
4. Copy the token (starts with `pypi-`)

### For TestPyPI:
1. Go to https://test.pypi.org/manage/account/
2. Follow same steps as PyPI
3. Copy the token (starts with `pypi-`)

### Configure tokens in ~/.pypirc:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

## Pre-Deployment Checklist

- [ ] Version number updated in `pyproject.toml` and `requirements_to_test/__init__.py`
- [ ] README.md is complete and accurate
- [ ] All dependencies listed in `pyproject.toml`
- [ ] License file is present
- [ ] Package structure is correct
- [ ] All tests pass (if you have tests)
- [ ] Documentation is up to date

## Step-by-Step Deployment

### 1. Update Version (if needed)

Edit the version in two places:
- `pyproject.toml`: `version = "1.0.1"`
- `requirements_to_test/__init__.py`: `__version__ = "1.0.1"`

### 2. Build the Package

```bash
# Using the provided script
./build.sh

# Or manually
pip install --upgrade build twine
python -m build
```

This creates:
- `dist/requirements_to_test-1.0.0-py3-none-any.whl` (wheel)
- `dist/requirements-to-test-1.0.0.tar.gz` (source distribution)

### 3. Test Upload to TestPyPI (Recommended)

```bash
# Using the upload script
./upload.sh

# Or manually
python -m twine upload --repository testpypi dist/*
```

### 4. Test Installation from TestPyPI

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ requirements-to-test

# Test the installation
requirements-to-test
# or
python -m requirements_to_test
```

### 5. Upload to PyPI

If testing went well:

```bash
# Upload to production PyPI
python -m twine upload dist/*
```

### 6. Verify Deployment

1. Check your package page: https://pypi.org/project/requirements-to-test/
2. Test installation: `pip install requirements-to-test`
3. Test CLI: `requirements-to-test`

## Package Structure

```
RequirementsToTest/
├── requirements_to_test/           # Main package
│   ├── __init__.py                # Package metadata
│   ├── __main__.py                # CLI entry point
│   ├── gui.py                     # GUI components
│   ├── parser.py                  # Requirements parser
│   └── generator.py               # Test code generator
├── pyproject.toml                 # Modern packaging config
├── MANIFEST.in                    # Additional files to include
├── README.md                      # Package documentation
├── LICENSE                        # MIT license
├── requirements.txt               # Development dependencies
├── build.sh                       # Build script
├── upload.sh                      # Upload script
└── sample_*                       # Example files
```

## Entry Points

The package provides multiple ways to run:

1. **Command line**: `requirements-to-test`
2. **Module execution**: `python -m requirements_to_test`
3. **Direct import**: `from requirements_to_test import RequirementsApp`

## Troubleshooting

### Build Issues

**"No module named requirements_to_test"**
- Ensure you're in the project root directory
- Check that all `__init__.py` files exist

**"Package discovery failed"**
- Verify `pyproject.toml` package configuration
- Check that package directory structure is correct

### Upload Issues

**"403 Forbidden"**
- Check API token is correct
- Ensure you have permission to upload to package name
- Package name might already exist (choose different name)

**"400 Bad Request"**
- Version number might already exist
- Check package metadata in `pyproject.toml`

### Installation Issues

**"Could not find a version"**
- Wait a few minutes after upload (PyPI needs time to index)
- Check package name spelling
- Ensure version was uploaded successfully

**"No module named wx"**
- wxPython requires system libraries
- See README.md for platform-specific installation notes

## Updating the Package

1. Make your changes
2. Update version numbers
3. Update CHANGELOG (if you have one)
4. Build and test
5. Upload new version

```bash
# Quick update workflow
vim pyproject.toml  # Update version
vim requirements_to_test/__init__.py  # Update version
./build.sh
./upload.sh
```

## Best Practices

1. **Always test on TestPyPI first**
2. **Use semantic versioning** (MAJOR.MINOR.PATCH)
3. **Keep detailed changelogs**
4. **Test installations on different platforms**
5. **Use API tokens instead of passwords**
6. **Never commit tokens to version control**

## Alternative Package Names

If `requirements-to-test` is taken, consider:
- `req-to-test`
- `requirements-test-generator`
- `nlp-requirements-tester`
- `requirement-checker`

## Support

For issues with:
- **Package functionality**: Check the main README.md
- **Packaging/deployment**: Review this guide
- **PyPI upload**: Check PyPI documentation
- **wxPython installation**: See wxPython documentation

---

**Note**: Replace `yourusername` in URLs with your actual GitHub username if you create a repository for this project. 