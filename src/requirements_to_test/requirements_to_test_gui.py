import wx
import re
import os
import sys
import subprocess
import tempfile
import json
import threading
from typing import List, Dict, Tuple, Optional
from datetime import datetime

try:
    from .runner import TestRunner
except Exception:
    # Allow running this module directly
    from requirements_to_test.runner import TestRunner

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
                        'checked': False,
                        'sub_requirements': []  # New field for sub-goals
                    })
        
        return requirements
    
    def add_sub_requirement(self, parent_req: Dict[str, str], sub_text: str) -> Dict[str, str]:
        """Add a sub-requirement to a parent requirement"""
        if 'sub_requirements' not in parent_req:
            parent_req['sub_requirements'] = []
        
        sub_id = f"{parent_req['id']}.{len(parent_req['sub_requirements']) + 1}"
        sub_req = {
            'id': sub_id,
            'text': self._clean_requirement(sub_text),
            'category': self._categorize_requirement(sub_text),
            'checked': False,
            'parent_id': parent_req['id'],
            'sub_requirements': []  # Allow nested sub-requirements
        }
        
        parent_req['sub_requirements'].append(sub_req)
        return sub_req
    
    def remove_sub_requirement(self, parent_req: Dict[str, str], sub_index: int) -> bool:
        """Remove a sub-requirement by index"""
        if 'sub_requirements' not in parent_req:
            return False
        
        if 0 <= sub_index < len(parent_req['sub_requirements']):
            parent_req['sub_requirements'].pop(sub_index)
            # Renumber remaining sub-requirements and their nested sub-requirements
            self._renumber_sub_requirements(parent_req)
            return True
        
        return False
    
    def _renumber_sub_requirements(self, parent_req: Dict[str, str]):
        """Renumber sub-requirements and recursively renumber their nested sub-requirements"""
        if 'sub_requirements' not in parent_req:
            return
        
        for i, sub_req in enumerate(parent_req['sub_requirements']):
            old_id = sub_req['id']
            new_id = f"{parent_req['id']}.{i + 1}"
            sub_req['id'] = new_id
            
            # Update parent_id reference
            sub_req['parent_id'] = parent_req['id']
            
            # Recursively renumber nested sub-requirements
            if 'sub_requirements' in sub_req and sub_req['sub_requirements']:
                self._renumber_sub_requirements(sub_req)
    
    def get_all_requirements_flat(self, requirements: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Get a flat list of all requirements including nested sub-requirements"""
        flat_list = []
        
        def flatten_recursive(req_list):
            for req in req_list:
                flat_list.append(req)
                if 'sub_requirements' in req and req['sub_requirements']:
                    flatten_recursive(req['sub_requirements'])
        
        flatten_recursive(requirements)
        return flat_list
    
    def get_requirement_depth(self, req: Dict[str, str]) -> int:
        """Get the depth level of a requirement based on its ID"""
        return req['id'].count('.')
    
    def find_requirement_by_id(self, requirements: List[Dict[str, str]], req_id: str) -> Optional[Dict[str, str]]:
        """Find a requirement by its ID, searching recursively through nested requirements"""
        def search_recursive(req_list):
            for req in req_list:
                if req['id'] == req_id:
                    return req
                if 'sub_requirements' in req and req['sub_requirements']:
                    found = search_recursive(req['sub_requirements'])
                    if found:
                        return found
            return None
        
        return search_recursive(requirements)
    
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
            "import sys",
            "import os",
            "",
            f"class {class_name}:",
            '    """Test class for requirements validation"""',
            "",
            "    def setup_method(self):",
            '        """Setup method called before each test"""',
            "        # Initialize test data and mock objects",
            "        self.mock_system = Mock()",
            "        self.test_data = {'users': [], 'data': []}", 
            "        pass",
            "",
        ]
        
        for req in requirements:
            test_method = self._generate_test_method(req)
            code_lines.extend(test_method)
            code_lines.append("")
        
        # Add helper methods
        code_lines.extend([
            "    def teardown_method(self):",
            '        """Teardown method called after each test"""',
            "        # Clean up after each test",
            "        pass",
            "",
            "    def _validate_input(self, input_data):",
            '        """Helper method for input validation tests"""',
            "        if not input_data or not isinstance(input_data, (str, dict, list)):",
            "            return False",
            "        return True",
            "",
            "    def _authenticate_user(self, username, password):",
            '        """Helper method for authentication tests"""',
            "        # Mock authentication logic",
            "        if username and password and len(password) >= 8:",
            "            return True",
            "        return False",
            "",
            "    def _save_data(self, data):",
            '        """Helper method for save functionality tests"""',
            "        # Mock save operation",
            "        if data:",
            "            self.test_data['data'].append(data)",
            "            return True",
            "        return False",
            "",
            "    def _display_message(self, message):",
            '        """Helper method for display tests"""',
            "        # Mock display operation",
            "        if message and isinstance(message, str) and len(message) > 0:",
            "            return message",
            "        return None",
            "",
            "    def _check_performance(self, operation_time):",
            '        """Helper method for performance tests"""',
            "        # Mock performance check (operation should complete in < 1 second)",
            "        return operation_time < 1.0",
            "",
            "if __name__ == '__main__':",
            "    pytest.main([__file__])"
        ])
        
        return "\n".join(code_lines)
    
    def _generate_test_method(self, requirement: Dict[str, str]) -> List[str]:
        """Generate a test method for a single requirement"""
        method_name = self._create_method_name(requirement['text'])
        category = requirement['category'].lower()
        
        lines = [
            f"    def test_{method_name}(self):",
            f'        """Test: {requirement["text"]}"""',
            f"        # Test for requirement {requirement['id']} - {requirement['category']}",
            "        # Generated test implementation",
        ]
        
        # Generate category-specific test implementation
        if category == 'validation':
            lines.extend([
                "        # Test input validation",
                "        valid_input = 'valid test data'",
                "        invalid_input = ''",
                "        ",
                "        assert self._validate_input(valid_input) == True",
                "        assert self._validate_input(invalid_input) == False",
                "        assert self._validate_input(None) == False"
            ])
        elif category == 'security':
            lines.extend([
                "        # Test authentication/authorization",
                "        valid_user = 'testuser'",
                "        valid_password = 'password123'",
                "        invalid_password = '123'",
                "        ",
                "        assert self._authenticate_user(valid_user, valid_password) == True",
                "        assert self._authenticate_user(valid_user, invalid_password) == False",
                "        assert self._authenticate_user('', valid_password) == False"
            ])
        elif category == 'functional':
            lines.extend([
                "        # Test functional requirement",
                "        test_data = {'id': 1, 'name': 'test'}",
                "        empty_data = None",
                "        ",
                "        assert self._save_data(test_data) == True",
                "        assert self._save_data(empty_data) == False",
                "        assert len(self.test_data['data']) >= 1"
            ])
        elif category == 'output':
            lines.extend([
                "        # Test output/display functionality",
                "        test_message = 'Error: Invalid input'",
                "        empty_message = ''",
                "        ",
                "        result = self._display_message(test_message)",
                "        assert result is not None",
                "        assert result == test_message",
                "        assert self._display_message(empty_message) is None"
            ])
        elif category == 'performance':
            lines.extend([
                "        # Test performance requirement",
                "        import time",
                "        ",
                "        start_time = time.time()",
                "        # Simulate fast operation",
                "        time.sleep(0.1)  # 100ms - should pass",
                "        operation_time = time.time() - start_time",
                "        ",
                "        assert self._check_performance(operation_time) == True",
                "        # Test that slow operations fail",
                "        assert self._check_performance(2.0) == False"
            ])
        elif category == 'input':
            lines.extend([
                "        # Test input handling",
                "        valid_inputs = ['test', {'key': 'value'}, [1, 2, 3]]",
                "        invalid_inputs = [None, '', []]",
                "        ",
                "        for valid_input in valid_inputs:",
                "            assert self._validate_input(valid_input) == True",
                "        ",
                "        for invalid_input in invalid_inputs:",
                "            assert self._validate_input(invalid_input) == False"
            ])
        else:
            # Generic test for unknown categories
            lines.extend([
                "        # Generic requirement test",
                "        # TODO: Implement specific test logic for this requirement",
                "        test_passed = True  # Replace with actual test logic",
                "        assert test_passed == True"
            ])
        
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
        self.test_results = {}
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
        
        # Test status summary
        self.status_text = wx.StaticText(self, label="No tests run yet")
        self.status_text.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(self.status_text, 0, wx.ALL | wx.CENTER, 5)
        
        # Scrolled panel for requirements
        self.scroll_panel = wx.ScrolledWindow(self)
        self.scroll_panel.SetScrollRate(5, 5)
        self.requirements_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_panel.SetSizer(self.requirements_sizer)
        
        sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.run_tests_btn = wx.Button(self, label="Run Tests")
        self.check_all_btn = wx.Button(self, label="Check All")
        self.uncheck_all_btn = wx.Button(self, label="Uncheck All")
        self.export_btn = wx.Button(self, label="Export Checklist")
        
        self.run_tests_btn.Bind(wx.EVT_BUTTON, self.on_run_tests)
        self.check_all_btn.Bind(wx.EVT_BUTTON, self.on_check_all)
        self.uncheck_all_btn.Bind(wx.EVT_BUTTON, self.on_uncheck_all)
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export_checklist)
        
        button_sizer.Add(self.run_tests_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.check_all_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.uncheck_all_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.export_btn, 0, wx.ALL, 5)
        
        sizer.Add(button_sizer, 0, wx.CENTER)
        
        self.SetSizer(sizer)
        
        # Initially disable run tests button
        self.run_tests_btn.Enable(False)
    
    def update_requirements(self, requirements: List[Dict[str, str]]):
        """Update the requirements display"""
        self.requirements = requirements
        self.test_results = {}  # Clear test results when requirements change
        
        # Clear existing controls
        self.requirements_sizer.Clear(True)
        
        # Add requirements recursively
        for req in requirements:
            self._add_requirements_recursive(req, depth=0)
        
        self.scroll_panel.FitInside()
        self.Layout()
        
        # Enable run tests button if we have requirements
        self.run_tests_btn.Enable(len(requirements) > 0)
        self.update_status_text()
    
    def _add_requirements_recursive(self, req: Dict[str, str], depth: int = 0, parent_req: Dict[str, str] = None):
        """Recursively add requirement panels for nested sub-requirements"""
        # Add the current requirement
        self._add_requirement_panel(req, depth=depth, parent_req=parent_req)
        
        # Add its sub-requirements recursively
        if 'sub_requirements' in req and req['sub_requirements']:
            for sub_req in req['sub_requirements']:
                self._add_requirements_recursive(sub_req, depth=depth + 1, parent_req=req)
    
    def _add_requirement_panel(self, req: Dict[str, str], depth: int = 0, parent_req: Dict[str, str] = None):
        """Add a single requirement panel with proper indentation based on depth"""
        req_panel = wx.Panel(self.scroll_panel)
        req_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Calculate indentation based on depth
        indent_width = 30 * depth
        if depth > 0:
            spacer = wx.StaticText(req_panel, label="", size=(indent_width, -1))
            req_sizer.Add(spacer, 0, wx.ALL | wx.CENTER, 0)
        
        # Test status indicator
        status_label = wx.StaticText(req_panel, label="○", size=(20, -1))
        status_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        status_label.SetForegroundColour(wx.Colour(200, 200, 200))
        req['status_label'] = status_label
        
        # Checkbox
        checkbox = wx.CheckBox(req_panel, label="")
        checkbox.SetValue(req['checked'])
        checkbox.Bind(wx.EVT_CHECKBOX, lambda evt, r=req: self.on_requirement_check(evt, r))
        
        # Requirement text with proper tree symbols
        text_label = self._format_requirement_text(req, depth)
        text = wx.StaticText(req_panel, label=text_label)
        text.Wrap(250 - (depth * 20))  # Adjust wrap width based on depth
        
        # Buttons - every requirement can have sub-requirements
        add_sub_btn = wx.Button(req_panel, label="+ Sub", size=(50, 25))
        add_sub_btn.Bind(wx.EVT_BUTTON, lambda evt, r=req: self.on_add_sub_requirement(evt, r))
        req['add_sub_btn'] = add_sub_btn
        
        # Delete button for sub-requirements (not top-level)
        if depth > 0:
            del_sub_btn = wx.Button(req_panel, label="✗", size=(25, 25))
            del_sub_btn.SetForegroundColour(wx.Colour(200, 0, 0))
            del_sub_btn.Bind(wx.EVT_BUTTON, lambda evt, sr=req, pr=parent_req: self.on_delete_sub_requirement(evt, sr, pr))
            req['del_sub_btn'] = del_sub_btn
        
        # Layout the panel
        req_sizer.Add(status_label, 0, wx.ALL | wx.CENTER, 5)
        req_sizer.Add(checkbox, 0, wx.ALL | wx.CENTER, 5)
        req_sizer.Add(text, 1, wx.ALL | wx.EXPAND, 5)
        req_sizer.Add(add_sub_btn, 0, wx.ALL | wx.CENTER, 2)
        
        if depth > 0:
            req_sizer.Add(del_sub_btn, 0, wx.ALL | wx.CENTER, 2)
        
        req_panel.SetSizer(req_sizer)
        self.requirements_sizer.Add(req_panel, 0, wx.EXPAND | wx.ALL, 2)
    
    def _format_requirement_text(self, req: Dict[str, str], depth: int) -> str:
        """Format requirement text with appropriate tree symbols based on depth"""
        if depth == 0:
            return f"[{req['category']}] {req['id']}: {req['text']}"
        else:
            # Create tree structure visualization
            tree_symbol = "  " + "  " * (depth - 1) + "└─ "
            return f"{tree_symbol}[{req['category']}] {req['id']}: {req['text']}"
    
    def on_add_sub_requirement(self, event, parent_req: Dict[str, str]):
        """Handle adding a sub-requirement"""
        # Create dialog to get sub-requirement text
        dlg = wx.TextEntryDialog(
            self, 
            f"Enter sub-requirement for:\n{parent_req['text']}\n\nSub-requirement text:",
            "Add Sub-Requirement"
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            sub_text = dlg.GetValue().strip()
            if sub_text:
                # Get the main frame to access the parser
                main_frame = self.GetTopLevelParent()
                if hasattr(main_frame, 'parser'):
                    # Add the sub-requirement
                    main_frame.parser.add_sub_requirement(parent_req, sub_text)
                    # Refresh the display
                    self.update_requirements(self.requirements)
                    # Regenerate test code
                    self._regenerate_tests()
        
        dlg.Destroy()
    
    def on_delete_sub_requirement(self, event, sub_req: Dict[str, str], parent_req: Dict[str, str]):
        """Handle deleting a sub-requirement"""
        # Confirm deletion
        dlg = wx.MessageDialog(
            self,
            f"Delete sub-requirement:\n\n{sub_req['text']}\n\nThis will also delete any nested sub-requirements.\nThis action cannot be undone.",
            "Confirm Deletion",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            # Find the index of the sub-requirement
            sub_index = -1
            if 'sub_requirements' in parent_req:
                for i, sr in enumerate(parent_req['sub_requirements']):
                    if sr['id'] == sub_req['id']:
                        sub_index = i
                        break
            
            if sub_index >= 0:
                # Get the main frame to access the parser
                main_frame = self.GetTopLevelParent()
                if hasattr(main_frame, 'parser'):
                    # Remove the sub-requirement (this will also remove nested sub-requirements)
                    main_frame.parser.remove_sub_requirement(parent_req, sub_index)
                    # Refresh the display
                    self.update_requirements(self.requirements)
                    # Regenerate test code
                    self._regenerate_tests()
        
        dlg.Destroy()
    
    def _regenerate_tests(self):
        """Regenerate test code after sub-requirements change"""
        main_frame = self.GetTopLevelParent()
        if hasattr(main_frame, 'test_generator') and hasattr(main_frame, 'test_code_text'):
            # Get all requirements including sub-requirements
            all_reqs = main_frame.parser.get_all_requirements_flat(self.requirements)
            # Generate new test code
            test_code = main_frame.test_generator.generate_pytest_code(all_reqs)
            main_frame.test_code_text.SetValue(test_code)

    def update_test_results(self, test_results: Dict[str, Dict]):
        """Update test results and visual indicators"""
        self.test_results = test_results
        
        # Update all requirements recursively
        self._update_requirements_recursive(self.requirements, test_results)
        
        self.update_status_text()
        self.Layout()
    
    def _update_requirement_status(self, req: Dict[str, str], test_results: Dict[str, Dict]):
        """Update status for a single requirement (main or sub)"""
        req_id = req['id']
        status_label = req.get('status_label')
        
        if status_label and req_id in test_results:
            result = test_results[req_id]
            status = result['status']
            
            if status == 'passed':
                status_label.SetLabel("✓")
                status_label.SetForegroundColour(wx.Colour(0, 150, 0))
                status_label.SetToolTip(f"Test passed - {result.get('message', '')}")
            elif status == 'failed':
                status_label.SetLabel("✗")
                status_label.SetForegroundColour(wx.Colour(200, 0, 0))
                status_label.SetToolTip(f"Test failed - {result.get('message', '')}")
            elif status == 'error':
                status_label.SetLabel("!")
                status_label.SetForegroundColour(wx.Colour(255, 165, 0))
                status_label.SetToolTip(f"Test error - {result.get('message', '')}")
            elif status == 'skipped':
                status_label.SetLabel("~")
                status_label.SetForegroundColour(wx.Colour(100, 100, 100))
                status_label.SetToolTip(f"Test skipped - {result.get('message', '')}")
            else:
                status_label.SetLabel("?")
                status_label.SetForegroundColour(wx.Colour(100, 100, 100))
                status_label.SetToolTip(f"Unknown status - {result.get('message', '')}")

    def update_status_text(self):
        """Update the status summary text"""
        if not self.test_results:
            self.status_text.SetLabel("No tests run yet")
            self.status_text.SetForegroundColour(wx.Colour(100, 100, 100))
            return
        
        passed = sum(1 for r in self.test_results.values() if r['status'] == 'passed')
        failed = sum(1 for r in self.test_results.values() if r['status'] == 'failed')
        error = sum(1 for r in self.test_results.values() if r['status'] == 'error')
        skipped = sum(1 for r in self.test_results.values() if r['status'] == 'skipped')
        total = len(self.test_results)
        
        # Count requirements at different levels
        main_reqs = len(self.requirements)
        total_reqs = self._count_all_requirements_recursive(self.requirements)
        sub_reqs = total_reqs - main_reqs
        
        status_text = f"Tests: {passed} passed, {failed} failed, {error} errors, {skipped} skipped"
        status_text += f" | Total: {total_reqs} requirements ({main_reqs} main + {sub_reqs} sub)"
        self.status_text.SetLabel(status_text)
        
        # Set color based on overall results
        if error > 0 or failed > 0:
            self.status_text.SetForegroundColour(wx.Colour(200, 0, 0))
        elif passed == total and total > 0:
            self.status_text.SetForegroundColour(wx.Colour(0, 150, 0))
        else:
            self.status_text.SetForegroundColour(wx.Colour(100, 100, 100))
    
    def _count_all_requirements_recursive(self, requirements: List[Dict[str, str]]) -> int:
        """Recursively count all requirements including nested sub-requirements"""
        count = 0
        for req in requirements:
            count += 1  # Count this requirement
            if 'sub_requirements' in req and req['sub_requirements']:
                count += self._count_all_requirements_recursive(req['sub_requirements'])
        return count
    
    def clear_test_results(self):
        """Clear all test result indicators"""
        self.test_results = {}
        
        # Clear all requirements recursively
        self._clear_requirements_recursive(self.requirements)
        
        self.update_status_text()
        self.Layout()
    
    def _clear_requirements_recursive(self, requirements: List[Dict[str, str]]):
        """Recursively clear test results for all requirements"""
        for req in requirements:
            status_label = req.get('status_label')
            if status_label:
                status_label.SetLabel("○")
                status_label.SetForegroundColour(wx.Colour(200, 200, 200))
                status_label.SetToolTip("Test not run yet")
            
            # Recursively clear sub-requirements
            if 'sub_requirements' in req and req['sub_requirements']:
                self._clear_requirements_recursive(req['sub_requirements'])
    
    def update_test_results(self, test_results: Dict[str, Dict]):
        """Update test results and visual indicators"""
        self.test_results = test_results
        
        # Update all requirements recursively
        self._update_requirements_recursive(self.requirements, test_results)
        
        self.update_status_text()
        self.Layout()
    
    def _update_requirements_recursive(self, requirements: List[Dict[str, str]], test_results: Dict[str, Dict]):
        """Recursively update test results for all requirements"""
        for req in requirements:
            self._update_requirement_status(req, test_results)
            
            # Recursively update sub-requirements
            if 'sub_requirements' in req and req['sub_requirements']:
                self._update_requirements_recursive(req['sub_requirements'], test_results)
    
    def on_run_tests(self, event):
        """Handle run tests button click"""
        # Clear previous test results and show running state
        self.clear_test_results()
        self.status_text.SetLabel("Tests are running...")
        self.status_text.SetForegroundColour(wx.Colour(100, 100, 200))
        
        # Get the main frame to access test code and runner
        main_frame = self.GetTopLevelParent()
        if hasattr(main_frame, 'run_tests'):
            main_frame.run_tests()
    
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
        self.test_runner = TestRunner()
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
        
        # Generate test code for all requirements (including any existing sub-requirements)
        all_reqs = self.parser.get_all_requirements_flat(self.current_requirements)
        test_code = self.test_generator.generate_pytest_code(all_reqs)
        self.test_code_text.SetValue(test_code)
        
        # Switch to requirements tab
        self.notebook.SetSelection(0)
        
        wx.MessageBox(f"Generated {len(self.current_requirements)} main requirements!", 
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
    
    def run_tests(self):
        """Run pytest tests and update the checklist with results"""
        if not self.current_requirements:
            wx.MessageBox("No requirements available to test!", "No Requirements", 
                         wx.OK | wx.ICON_WARNING)
            return
        
        test_code = self.test_code_text.GetValue()
        if not test_code:
            wx.MessageBox("No test code available to run!", "No Test Code", 
                         wx.OK | wx.ICON_WARNING)
            return
        
        # Get all requirements including sub-requirements for testing
        all_reqs = self.parser.get_all_requirements_flat(self.current_requirements)
        
        # Disable the run tests button during execution
        self.requirements_panel.run_tests_btn.Enable(False)
        self.requirements_panel.run_tests_btn.SetLabel("Running Tests...")
        
        # Create a non-modal progress dialog
        self.progress_dlg = wx.ProgressDialog(
            "Running Tests",
            "Preparing to run tests...",
            maximum=100,
            parent=self,
            style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME
        )
        
        def progress_callback(message):
            wx.CallAfter(self._update_progress, message)
        
        def run_tests_thread():
            try:
                # Run tests in background thread with all requirements
                results = self.test_runner.run_tests(
                    test_code, 
                    all_reqs,  # Use flat list including sub-requirements
                    progress_callback
                )
                
                # Update UI in main thread
                wx.CallAfter(self._update_test_results, results)
                
            except Exception as e:
                wx.CallAfter(self._handle_test_error, str(e))
        
        # Start test execution in background thread
        test_thread = threading.Thread(target=run_tests_thread)
        test_thread.daemon = True
        test_thread.start()
    
    def _update_progress(self, message):
        """Update progress dialog (called from main thread)"""
        if hasattr(self, 'progress_dlg') and self.progress_dlg:
            keep_going, skip = self.progress_dlg.Update(50, message)
            if not keep_going:  # User clicked cancel
                # Note: We can't actually cancel the test execution cleanly
                # but we can hide the dialog
                self._cleanup_progress_dialog()
    
    def _cleanup_progress_dialog(self):
        """Clean up the progress dialog"""
        if hasattr(self, 'progress_dlg') and self.progress_dlg:
            self.progress_dlg.Destroy()
            self.progress_dlg = None
        
        # Re-enable the run tests button
        self.requirements_panel.run_tests_btn.Enable(True)
        self.requirements_panel.run_tests_btn.SetLabel("Run Tests")
    
    def _update_test_results(self, results):
        """Update UI with test results (called from main thread)"""
        try:
            # Clean up progress dialog first
            self._cleanup_progress_dialog()
            
            # Update requirements panel with results
            self.requirements_panel.update_test_results(results)
            
            # Show results summary dialog with OK button
            passed = sum(1 for r in results.values() if r['status'] == 'passed')
            failed = sum(1 for r in results.values() if r['status'] == 'failed')
            errors = sum(1 for r in results.values() if r['status'] == 'error')
            total = len(results)
            
            if failed > 0 or errors > 0:
                icon = wx.ICON_WARNING
                title = "Test Results - Some Issues Found"
                if errors > 0:
                    summary = f"Test execution completed with issues!\n\n"
                    summary += f"✓ Passed: {passed}\n"
                    summary += f"✗ Failed: {failed}\n"
                    summary += f"⚠ Errors: {errors}\n"
                    summary += f"Total: {total}\n\n"
                    summary += "Check the checklist for detailed results."
                else:
                    summary = f"Test execution completed!\n\n"
                    summary += f"✓ Passed: {passed}\n"
                    summary += f"✗ Failed: {failed}\n"
                    summary += f"Total: {total}\n\n"
                    summary += "Check the checklist for detailed results."
            else:
                icon = wx.ICON_INFORMATION
                title = "Test Results - All Passed!"
                summary = f"🎉 All tests passed successfully!\n\n"
                summary += f"✓ Passed: {passed}/{total}\n\n"
                summary += "Great job! All requirements are being met."
            
            # Create a custom dialog with better formatting
            dlg = wx.MessageDialog(self, summary, title, wx.OK | icon)
            dlg.ShowModal()
            dlg.Destroy()
            
        except Exception as e:
            self._cleanup_progress_dialog()
            wx.MessageBox(f"Error updating results: {str(e)}", "Update Error", 
                         wx.OK | wx.ICON_ERROR)
    
    def _handle_test_error(self, error_msg):
        """Handle test execution errors (called from main thread)"""
        try:
            self._cleanup_progress_dialog()
            wx.MessageBox(f"Error running tests:\n\n{error_msg}\n\nPlease check that your test code is valid and try again.", 
                         "Test Execution Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            # Fallback error handling
            print(f"Error in error handler: {e}")
            self._cleanup_progress_dialog()

class RequirementsApp(wx.App):
    """Main application class"""
    
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = RequirementsApp()
    app.MainLoop() 