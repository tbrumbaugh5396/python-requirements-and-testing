#!/usr/bin/env python3
"""
Example script to test the TestRunner functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from requirements_to_test_gui import TestRunner, RequirementsParser, TestCodeGenerator

def test_runner_functionality():
    """Test the TestRunner with sample requirements"""
    
    # Sample requirements text
    sample_text = """
    The application should validate user input.
    The system must authenticate users before allowing access.
    Users should be able to save their work.
    The interface needs to display error messages clearly.
    Performance should be optimized for large datasets.
    """
    
    # Parse requirements
    parser = RequirementsParser()
    requirements = parser.extract_requirements(sample_text)
    
    print(f"Parsed {len(requirements)} requirements:")
    for req in requirements:
        print(f"  {req['id']}: [{req['category']}] {req['text']}")
    
    # Generate test code
    generator = TestCodeGenerator()
    test_code = generator.generate_pytest_code(requirements)
    
    print("\nGenerated test code:")
    print("=" * 50)
    print(test_code)
    print("=" * 50)
    
    # Run tests
    runner = TestRunner()
    print("\nRunning tests...")
    
    def progress_callback(message):
        print(f"Progress: {message}")
    
    results = runner.run_tests(test_code, requirements, progress_callback)
    
    print("\nTest Results:")
    print("-" * 30)
    for req_id, result in results.items():
        status = result['status']
        message = result['message']
        duration = result.get('duration', 0)
        
        status_symbol = {
            'passed': '✓',
            'failed': '✗',
            'error': '!',
            'skipped': '~',
            'unknown': '?'
        }.get(status, '?')
        
        print(f"{status_symbol} {req_id}: {status} ({duration:.3f}s)")
        if message:
            print(f"    {message}")
    
    # Summary
    passed = sum(1 for r in results.values() if r['status'] == 'passed')
    failed = sum(1 for r in results.values() if r['status'] == 'failed')
    total = len(results)
    
    print(f"\nSummary: {passed}/{total} tests passed, {failed} failed")
    
    return results

if __name__ == '__main__':
    test_runner_functionality() 