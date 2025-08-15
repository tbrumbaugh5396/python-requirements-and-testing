"""
Lightweight pytest runner that does not depend on wxPython.
"""

import re
import os
import sys
import subprocess
import tempfile
from typing import List, Dict


class TestRunner:
    """Execute pytest tests and capture results"""

    def __init__(self):
        self.test_results = {}
        self.python_executable = self._find_python_with_pytest()

    def _find_python_with_pytest(self) -> str:
        """Find a Python executable that has pytest installed"""
        candidates = [
            sys.executable,
            '/usr/local/opt/python@3.10/bin/python3.10',
            '/usr/local/bin/python3',
            'python3',
            'python',
        ]

        for candidate in candidates:
            try:
                result = subprocess.run(
                    [candidate, '-c', 'import pytest; print("OK")'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and 'OK' in result.stdout:
                    return candidate
            except Exception:
                continue

        return sys.executable

    def run_tests(self, test_code: str, requirements: List[Dict[str, str]], progress_callback=None) -> Dict[str, Dict]:
        """Run pytest tests and return results mapped to requirement IDs"""
        results: Dict[str, Dict] = {}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(test_code)
            temp_file_path = temp_file.name

        try:
            cmd = [
                self.python_executable, '-m', 'pytest',
                temp_file_path,
                '-v',
                '--tb=short'
            ]

            if progress_callback:
                progress_callback("Starting test execution...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if progress_callback:
                progress_callback("Parsing test results...")

            results = self._parse_pytest_output(result.stdout, result.stderr, result.returncode, requirements)

            if progress_callback:
                progress_callback("Test execution completed")

        except subprocess.TimeoutExpired:
            if progress_callback:
                progress_callback("Test execution timed out")
            for req in requirements:
                results[req['id']] = {
                    'status': 'failed',
                    'message': 'Test execution timed out',
                    'duration': 0
                }
        except Exception as e:
            if progress_callback:
                progress_callback(f"Test execution error: {str(e)}")
            for req in requirements:
                results[req['id']] = {
                    'status': 'error',
                    'message': f'Execution error: {str(e)}',
                    'duration': 0
                }
        finally:
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

        return results

    def _parse_pytest_output(self, stdout: str, stderr: str, returncode: int, requirements: List[Dict[str, str]]) -> Dict[str, Dict]:
        """Parse pytest output to extract test results"""
        results: Dict[str, Dict] = {}

        method_to_req: Dict[str, str] = {}
        for req in requirements:
            method_name = f"test_{self._create_method_name(req['text'])}"
            method_to_req[method_name] = req['id']

        output = stdout + stderr
        lines = output.split('\n')

        test_session_started = False
        for line in lines:
            line = line.strip()
            if 'test session starts' in line.lower() or '=======' in line:
                test_session_started = True
                continue
            if not test_session_started:
                continue

            if '::test_' in line and ('PASSED' in line or 'FAILED' in line or 'ERROR' in line):
                parts = line.split('::')
                if len(parts) >= 3:
                    test_method_part = parts[-1]
                    test_method = test_method_part.split()[0]

                    req_id = method_to_req.get(test_method)
                    if req_id:
                        if 'PASSED' in line:
                            status = 'passed'
                            message = 'Test passed successfully'
                        elif 'FAILED' in line:
                            status = 'failed'
                            message = 'Test failed - check implementation'
                        elif 'ERROR' in line:
                            status = 'error'
                            message = 'Test error - check syntax'
                        else:
                            status = 'unknown'
                            message = 'Unknown test result'

                        duration = 0
                        if '[' in line and 's]' in line:
                            try:
                                duration_str = line.split('[')[1].split('s]')[0]
                                duration = float(duration_str)
                            except Exception:
                                pass

                        results[req_id] = {
                            'status': status,
                            'message': message,
                            'duration': duration
                        }

        if not results and returncode == 0:
            for req in requirements:
                results[req['id']] = {
                    'status': 'passed',
                    'message': 'Test passed (inferred from exit code)',
                    'duration': 0
                }
        elif not results and returncode != 0:
            for req in requirements:
                results[req['id']] = {
                    'status': 'failed',
                    'message': 'Test failed (inferred from exit code)',
                    'duration': 0
                }

        for req in requirements:
            if req['id'] not in results:
                results[req['id']] = {
                    'status': 'skipped',
                    'message': 'Test was not executed or could not be parsed',
                    'duration': 0
                }

        return results

    def _create_method_name(self, requirement_text: str) -> str:
        """Create a valid Python method name from requirement text"""
        name = re.sub(r'[^\w\s]', '', requirement_text.lower())
        name = re.sub(r'\s+', '_', name)
        name = name[:50]
        if name and name[0].isdigit():
            name = 'req_' + name
        return name or 'requirement_test'


