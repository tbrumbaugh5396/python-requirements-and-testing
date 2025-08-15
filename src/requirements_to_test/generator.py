"""
Test code generator module for creating pytest/unittest code from requirements.
"""

import re
from typing import List, Dict


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