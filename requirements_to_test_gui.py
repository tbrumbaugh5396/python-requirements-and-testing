import wx
import re
import os
from typing import List, Dict, Tuple
from datetime import datetime

class RequirementsParser:
    """Parser to extract testable requirements from natural language text"""
    
    def __init__(self):
        # Keywords that typically indicate requirements
        self.requirement_keywords = [
            'should', 'must', 'shall', 'will', 'needs to', 'required to',
            'has to', 'ought to', 'is required', 'is expected', 'validates',
            'ensures', 'verifies', 'checks', 'prevents', 'allows', 'enables'
        ]
    
    def extract_requirements(self, text: str) -> List[Dict[str, str]]:
        """Extract requirements from natural language text"""
        requirements = []
        sentences = re.split(r'[.!?]+', text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if sentence contains requirement keywords
            if any(keyword in sentence.lower() for keyword in self.requirement_keywords):
                # Clean up the sentence
                clean_sentence = self._clean_requirement(sentence)
                if clean_sentence:
                    requirements.append({
                        'id': f'REQ_{i+1:03d}',
                        'text': clean_sentence,
                        'category': self._categorize_requirement(clean_sentence),
                        'checked': False
                    })
        
        return requirements
    
    def _clean_requirement(self, sentence: str) -> str:
        """Clean and format requirement sentence"""
        # Remove extra whitespace
        sentence = ' '.join(sentence.split())
        
        # Ensure sentence starts with capital letter
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
        
        # Ensure sentence ends with period
        if sentence and not sentence.endswith('.'):
            sentence += '.'
        
        return sentence
    
    def _categorize_requirement(self, sentence: str) -> str:
        """Categorize requirement based on content"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['validate', 'check', 'verify', 'ensure']):
            return 'Validation'
        elif any(word in sentence_lower for word in ['input', 'enter', 'provide']):
            return 'Input'
        elif any(word in sentence_lower for word in ['output', 'display', 'show', 'return']):
            return 'Output'
        elif any(word in sentence_lower for word in ['security', 'authenticate', 'authorize']):
            return 'Security'
        elif any(word in sentence_lower for word in ['performance', 'speed', 'fast', 'time']):
            return 'Performance'
        else:
            return 'Functional'

class TestCodeGenerator:
    """Generate pytest/unittest code from requirements"""
    
    def generate_pytest_code(self, requirements: List[Dict[str, str]], class_name: str = "TestRequirements") -> str:
        """Generate pytest code for the requirements"""
        code_lines = [
            "import pytest",
            "import unittest",
            "from unittest.mock import Mock, patch",
            "",
            f"class {class_name}:",
            '    """Test class for requirements validation"""',
            ""
        ]
        
        for req in requirements:
            test_method = self._generate_test_method(req)
            code_lines.extend(test_method)
            code_lines.append("")
        
        # Add helper methods
        code_lines.extend([
            "    def setup_method(self):",
            '        """Setup method called before each test"""',
            "        pass",
            "",
            "    def teardown_method(self):",
            '        """Teardown method called after each test"""',
            "        pass",
            "",
            "if __name__ == '__main__':",
            "    pytest.main([__file__])"
        ])
        
        return "\n".join(code_lines)
    
    def _generate_test_method(self, requirement: Dict[str, str]) -> List[str]:
        """Generate a test method for a single requirement"""
        method_name = self._create_method_name(requirement['text'])
        
        lines = [
            f"    def test_{method_name}(self):",
            f'        """Test: {requirement["text"]}"""',
            f"        # TODO: Implement test for requirement {requirement['id']}",
            f"        # Category: {requirement['category']}",
            f"        # Requirement: {requirement['text']}",
            "        ",
            "        # Example test structure:",
            "        # 1. Setup test data",
            "        # 2. Execute the functionality",
            "        # 3. Assert expected results",
            "        ",
            "        assert True  # Replace with actual test implementation"
        ]
        
        return lines
    
    def _create_method_name(self, requirement_text: str) -> str:
        """Create a valid Python method name from requirement text"""
        # Remove punctuation and convert to lowercase
        name = re.sub(r'[^\w\s]', '', requirement_text.lower())
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        # Limit length
        name = name[:50]
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = 'req_' + name
        
        return name or 'requirement_test'

class RequirementsPanel(wx.Panel):
    """Panel for displaying and managing requirements checklist"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.requirements = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the requirements panel UI"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(self, label="Generated Requirements Checklist")
        title_font = title.GetFont()
        title_font.SetPointSize(12)
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 5)
        
        # Scrolled panel for requirements
        self.scroll_panel = wx.ScrolledWindow(self)
        self.scroll_panel.SetScrollRate(5, 5)
        self.requirements_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_panel.SetSizer(self.requirements_sizer)
        
        sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.check_all_btn = wx.Button(self, label="Check All")
        self.uncheck_all_btn = wx.Button(self, label="Uncheck All")
        self.export_btn = wx.Button(self, label="Export Checklist")
        
        self.check_all_btn.Bind(wx.EVT_BUTTON, self.on_check_all)
        self.uncheck_all_btn.Bind(wx.EVT_BUTTON, self.on_uncheck_all)
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export_checklist)
        
        button_sizer.Add(self.check_all_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.uncheck_all_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.export_btn, 0, wx.ALL, 5)
        
        sizer.Add(button_sizer, 0, wx.CENTER)
        
        self.SetSizer(sizer)
    
    def update_requirements(self, requirements: List[Dict[str, str]]):
        """Update the requirements display"""
        self.requirements = requirements
        
        # Clear existing controls
        self.requirements_sizer.Clear(True)
        
        # Add new requirement checkboxes
        for req in requirements:
            req_panel = wx.Panel(self.scroll_panel)
            req_sizer = wx.BoxSizer(wx.HORIZONTAL)
            
            # Checkbox
            checkbox = wx.CheckBox(req_panel, label="")
            checkbox.SetValue(req['checked'])
            checkbox.Bind(wx.EVT_CHECKBOX, lambda evt, r=req: self.on_requirement_check(evt, r))
            
            # Requirement text
            text = wx.StaticText(req_panel, label=f"[{req['category']}] {req['text']}")
            text.Wrap(400)
            
            req_sizer.Add(checkbox, 0, wx.ALL | wx.CENTER, 5)
            req_sizer.Add(text, 1, wx.ALL | wx.EXPAND, 5)
            
            req_panel.SetSizer(req_sizer)
            self.requirements_sizer.Add(req_panel, 0, wx.EXPAND | wx.ALL, 2)
        
        self.scroll_panel.FitInside()
        self.Layout()
    
    def on_requirement_check(self, event, requirement):
        """Handle requirement checkbox change"""
        requirement['checked'] = event.IsChecked()
    
    def on_check_all(self, event):
        """Check all requirements"""
        for req in self.requirements:
            req['checked'] = True
        self.update_requirements(self.requirements)
    
    def on_uncheck_all(self, event):
        """Uncheck all requirements"""
        for req in self.requirements:
            req['checked'] = False
        self.update_requirements(self.requirements)
    
    def on_export_checklist(self, event):
        """Export requirements checklist to file"""
        if not self.requirements:
            wx.MessageBox("No requirements to export!", "Export Error", wx.OK | wx.ICON_WARNING)
            return
        
        wildcard = "Text files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save Requirements Checklist", 
                           defaultFile="requirements_checklist.txt",
                           wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self._export_to_file(path)
        
        dlg.Destroy()
    
    def _export_to_file(self, filepath: str):
        """Export requirements to text file"""
        try:
            with open(filepath, 'w') as f:
                f.write("Requirements Checklist\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for req in self.requirements:
                    status = "☑" if req['checked'] else "☐"
                    f.write(f"{status} [{req['category']}] {req['id']}: {req['text']}\n")
                
                f.write(f"\nTotal Requirements: {len(self.requirements)}\n")
                f.write(f"Completed: {sum(1 for r in self.requirements if r['checked'])}\n")
            
            wx.MessageBox(f"Checklist exported successfully to {filepath}", 
                         "Export Complete", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Error exporting checklist: {str(e)}", 
                         "Export Error", wx.OK | wx.ICON_ERROR)

class MainFrame(wx.Frame):
    """Main application frame"""
    
    def __init__(self):
        super().__init__(None, title="Requirements to Test Generator", size=(1000, 700))
        
        self.parser = RequirementsParser()
        self.test_generator = TestCodeGenerator()
        self.current_requirements = []
        
        self.setup_ui()
        self.setup_menu()
        self.Center()
    
    def setup_ui(self):
        """Setup the main UI"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Splitter window
        splitter = wx.SplitterWindow(panel, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        
        # Left panel - Input
        left_panel = wx.Panel(splitter)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Input section
        input_label = wx.StaticText(left_panel, label="Enter Natural Language Requirements:")
        input_font = input_label.GetFont()
        input_font.SetWeight(wx.FONTWEIGHT_BOLD)
        input_label.SetFont(input_font)
        left_sizer.Add(input_label, 0, wx.ALL, 5)
        
        self.input_text = wx.TextCtrl(left_panel, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)
        self.input_text.SetValue("The application should validate user input.\n"
                                "The system must authenticate users before allowing access.\n"
                                "Users should be able to save their work.\n"
                                "The interface needs to display error messages clearly.\n"
                                "Performance should be optimized for large datasets.")
        left_sizer.Add(self.input_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Generate button
        self.generate_btn = wx.Button(left_panel, label="Generate Requirements & Tests")
        self.generate_btn.Bind(wx.EVT_BUTTON, self.on_generate)
        left_sizer.Add(self.generate_btn, 0, wx.ALL | wx.CENTER, 5)
        
        left_panel.SetSizer(left_sizer)
        
        # Right panel - Notebook with requirements and test code
        right_panel = wx.Panel(splitter)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.notebook = wx.Notebook(right_panel)
        
        # Requirements tab
        self.requirements_panel = RequirementsPanel(self.notebook)
        self.notebook.AddPage(self.requirements_panel, "Requirements Checklist")
        
        # Test code tab
        test_panel = wx.Panel(self.notebook)
        test_sizer = wx.BoxSizer(wx.VERTICAL)
        
        test_label = wx.StaticText(test_panel, label="Generated Test Code:")
        test_label_font = test_label.GetFont()
        test_label_font.SetWeight(wx.FONTWEIGHT_BOLD)
        test_label.SetFont(test_label_font)
        test_sizer.Add(test_label, 0, wx.ALL, 5)
        
        self.test_code_text = wx.TextCtrl(test_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        test_sizer.Add(self.test_code_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Test code buttons
        test_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.save_test_btn = wx.Button(test_panel, label="Save Test Code")
        self.copy_test_btn = wx.Button(test_panel, label="Copy to Clipboard")
        
        self.save_test_btn.Bind(wx.EVT_BUTTON, self.on_save_test_code)
        self.copy_test_btn.Bind(wx.EVT_BUTTON, self.on_copy_test_code)
        
        test_btn_sizer.Add(self.save_test_btn, 0, wx.ALL, 5)
        test_btn_sizer.Add(self.copy_test_btn, 0, wx.ALL, 5)
        
        test_sizer.Add(test_btn_sizer, 0, wx.CENTER)
        
        test_panel.SetSizer(test_sizer)
        self.notebook.AddPage(test_panel, "Generated Test Code")
        
        right_sizer.Add(self.notebook, 1, wx.EXPAND)
        right_panel.SetSizer(right_sizer)
        
        # Split the window
        splitter.SplitVertically(left_panel, right_panel)
        splitter.SetSashGravity(0.4)
        splitter.SetMinimumPaneSize(300)
        
        main_sizer.Add(splitter, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)
    
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New\tCtrl+N", "Clear all content")
        file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open requirements file")
        file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save current requirements")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tCtrl+Q", "Exit application")
        
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About", "About this application")
        
        menubar.Append(file_menu, "&File")
        menubar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menubar)
        
        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_new, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
    
    def on_generate(self, event):
        """Generate requirements and test code from input text"""
        input_text = self.input_text.GetValue().strip()
        
        if not input_text:
            wx.MessageBox("Please enter some requirements text!", "No Input", 
                         wx.OK | wx.ICON_WARNING)
            return
        
        # Parse requirements
        self.current_requirements = self.parser.extract_requirements(input_text)
        
        if not self.current_requirements:
            wx.MessageBox("No requirements could be extracted from the text. "
                         "Try including words like 'should', 'must', 'shall', etc.", 
                         "No Requirements Found", wx.OK | wx.ICON_WARNING)
            return
        
        # Update requirements panel
        self.requirements_panel.update_requirements(self.current_requirements)
        
        # Generate test code
        test_code = self.test_generator.generate_pytest_code(self.current_requirements)
        self.test_code_text.SetValue(test_code)
        
        # Switch to requirements tab
        self.notebook.SetSelection(0)
        
        wx.MessageBox(f"Generated {len(self.current_requirements)} requirements!", 
                     "Generation Complete", wx.OK | wx.ICON_INFORMATION)
    
    def on_save_test_code(self, event):
        """Save generated test code to file"""
        if not self.test_code_text.GetValue():
            wx.MessageBox("No test code to save!", "Save Error", wx.OK | wx.ICON_WARNING)
            return
        
        wildcard = "Python files (*.py)|*.py|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save Test Code", 
                           defaultFile="test_requirements.py",
                           wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                with open(path, 'w') as f:
                    f.write(self.test_code_text.GetValue())
                wx.MessageBox(f"Test code saved to {path}", "Save Complete", 
                             wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Error saving file: {str(e)}", "Save Error", 
                             wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_copy_test_code(self, event):
        """Copy test code to clipboard"""
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.test_code_text.GetValue()))
            wx.TheClipboard.Close()
            wx.MessageBox("Test code copied to clipboard!", "Copy Complete", 
                         wx.OK | wx.ICON_INFORMATION)
    
    def on_new(self, event):
        """Clear all content"""
        self.input_text.SetValue("")
        self.test_code_text.SetValue("")
        self.current_requirements = []
        self.requirements_panel.update_requirements([])
    
    def on_open(self, event):
        """Open requirements file"""
        wildcard = "Text files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open Requirements File", wildcard=wildcard, 
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                with open(path, 'r') as f:
                    content = f.read()
                self.input_text.SetValue(content)
            except Exception as e:
                wx.MessageBox(f"Error opening file: {str(e)}", "Open Error", 
                             wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_save(self, event):
        """Save current requirements text"""
        content = self.input_text.GetValue()
        if not content:
            wx.MessageBox("No content to save!", "Save Error", wx.OK | wx.ICON_WARNING)
            return
        
        wildcard = "Text files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save Requirements Text", 
                           defaultFile="requirements.txt",
                           wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                with open(path, 'w') as f:
                    f.write(content)
                wx.MessageBox(f"Requirements saved to {path}", "Save Complete", 
                             wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Error saving file: {str(e)}", "Save Error", 
                             wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_exit(self, event):
        """Exit application"""
        self.Close()
    
    def on_about(self, event):
        """Show about dialog"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Requirements to Test Generator")
        info.SetVersion("1.0")
        info.SetDescription("A tool to convert natural language requirements "
                           "into testable checklists and generate pytest code.")
        info.SetCopyright("(C) 2024")
        info.AddDeveloper("AI Assistant")
        
        wx.adv.AboutBox(info)

class RequirementsApp(wx.App):
    """Main application class"""
    
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = RequirementsApp()
    app.MainLoop() 