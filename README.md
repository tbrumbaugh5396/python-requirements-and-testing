# Requirements to Test Generator

A Python GUI application built with wxPython that converts natural language requirements into testable checklists and generates corresponding pytest code.

## Features

- **Natural Language Processing**: Extracts testable requirements from plain text using keyword detection
- **Requirements Categorization**: Automatically categorizes requirements (Validation, Input, Output, Security, Performance, Functional)
- **Interactive Checklist**: Displays requirements as checkable items with progress tracking
- **Test Code Generation**: Automatically generates pytest/unittest code templates
- **Export Functionality**: Save checklists and test code to files
- **File Management**: Open, save, and manage requirement documents

## Installation

1. **Install Python 3.7 or higher** (if not already installed)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install wxPython>=4.2.0 pytest>=7.0.0 typing-extensions>=4.0.0
   ```

## Usage

### Running the Application

```bash
# Using the launcher script (recommended)
python3 run_app.py

# Or run directly
python3 requirements_to_test_gui.py
```

### How to Use

1. **Enter Requirements**: In the left panel, enter your natural language requirements. The application recognizes requirement keywords like:
   - should, must, shall, will
   - needs to, required to, has to
   - validates, ensures, verifies, checks
   - prevents, allows, enables

2. **Generate**: Click "Generate Requirements & Tests" to process the text

3. **Review Checklist**: The "Requirements Checklist" tab shows:
   - Categorized requirements with checkboxes
   - Progress tracking
   - Export options

4. **View Test Code**: The "Generated Test Code" tab displays:
   - Pytest-compatible test methods
   - TODO comments for implementation
   - Save and copy options

### Example Input

```
The application should validate user input.
The system must authenticate users before allowing access.
Users should be able to save their work.
The interface needs to display error messages clearly.
Performance should be optimized for large datasets.
```

### Generated Output

The application will create:
- 5 categorized requirements (Security, Validation, Functional, Output, Performance)
- Corresponding test methods with descriptive names
- Ready-to-implement pytest code structure

## Features in Detail

### Requirements Parser
- Extracts sentences containing requirement keywords
- Cleans and formats requirement text
- Assigns unique IDs (REQ_001, REQ_002, etc.)
- Categorizes based on content analysis

### Test Code Generator
- Creates pytest-compatible test classes
- Generates method names from requirement text
- Includes setup/teardown methods
- Adds TODO comments for implementation guidance

### GUI Components
- **Split interface**: Input on left, results on right
- **Tabbed results**: Separate views for checklist and code
- **File operations**: Open, save, new, export
- **Interactive checklist**: Check/uncheck, bulk operations

## Menu Options

### File Menu
- **New (Ctrl+N)**: Clear all content
- **Open (Ctrl+O)**: Load requirements from file
- **Save (Ctrl+S)**: Save current requirements text
- **Exit (Ctrl+Q)**: Close application

### Help Menu
- **About**: Application information

## Export Options

1. **Requirements Checklist**: Export as formatted text file with:
   - Checkbox indicators (☐/☑)
   - Categories and IDs
   - Progress summary

2. **Test Code**: Save as Python file (.py) ready for:
   - pytest execution
   - Further development
   - Integration into test suites

## Technical Details

### Dependencies
- **wxPython**: Cross-platform GUI toolkit
- **pytest**: Testing framework
- **typing-extensions**: Type hints support

### File Structure
```
RequirementsToTest/
├── requirements_to_test_gui.py          # Main application
├── run_app.py                           # Launcher script
├── requirements.txt                     # Dependencies
├── README.md                           # Documentation
├── sample_generated_test.py            # Example generated test
└── sample_requirements_checklist.txt   # Example checklist export
```

### Classes Overview
- `RequirementsParser`: Natural language processing
- `TestCodeGenerator`: pytest code generation
- `RequirementsPanel`: Checklist UI component
- `MainFrame`: Main application window
- `RequirementsApp`: wxPython application class

## Troubleshooting

### Common Issues

1. **wxPython Installation Problems**:
   ```bash
   # On macOS with Apple Silicon
   pip install -U --force-reinstall wxPython
   
   # On Linux, may need system packages
   sudo apt-get install libgtk-3-dev libwebkitgtk-3.0-dev
   ```

2. **No Requirements Detected**:
   - Ensure text contains requirement keywords
   - Check sentence structure (complete sentences work best)
   - Try more explicit requirement language

3. **Application Won't Start**:
   - Verify Python version (3.7+)
   - Check all dependencies are installed
   - Run from command line to see error messages

## Future Enhancements

Potential improvements:
- Advanced NLP with machine learning
- Custom requirement templates
- Integration with test management tools
- Support for additional test frameworks
- Requirement traceability features
- Collaborative editing capabilities

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are correctly installed
3. Review the example usage patterns
4. Ensure input text follows natural language requirement patterns

---

**Note**: This tool generates test templates that require manual implementation. The generated pytest code provides structure and TODO comments but needs actual test logic to be added by developers. 