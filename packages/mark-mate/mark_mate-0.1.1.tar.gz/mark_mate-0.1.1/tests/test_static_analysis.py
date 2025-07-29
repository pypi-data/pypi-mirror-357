"""
Comprehensive tests for Static Analysis Module

These tests verify the functionality and type safety of the StaticAnalyzer class,
ensuring it properly analyzes Python code quality using multiple tools.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from pathlib import Path

# Import the module under test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mark_mate.analyzers.static_analysis import StaticAnalyzer


class TestStaticAnalyzer:
    """Test StaticAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StaticAnalyzer()

    def test_analyzer_initialization(self):
        """Test analyzer initializes with correct structure."""
        assert hasattr(self.analyzer, 'config')
        assert hasattr(self.analyzer, 'tools_available')
        assert isinstance(self.analyzer.config, dict)
        assert isinstance(self.analyzer.tools_available, dict)

    def test_analyzer_with_config(self):
        """Test analyzer accepts configuration."""
        config = {"max_line_length": 120, "ignore_patterns": ["E501"]}
        analyzer = StaticAnalyzer(config)
        assert analyzer.config == config

    def test_tool_availability_check(self):
        """Test tool availability checking."""
        tools = self.analyzer.tools_available
        assert isinstance(tools, dict)
        # Tools may or may not be available, but structure should be correct
        for tool_name, available in tools.items():
            assert isinstance(tool_name, str)
            assert isinstance(available, bool)

    def test_analyze_valid_python_file(self):
        """Test analysis of a valid Python file."""
        # Create a temporary Python file
        test_code = '''
def hello_world():
    """A simple hello world function."""
    message = "Hello, World!"
    print(message)
    return message

if __name__ == "__main__":
    hello_world()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "file_path" in result
            assert "analysis_timestamp" in result
            assert "tools_used" in result
            assert "flake8_analysis" in result
            assert "pylint_analysis" in result
            assert "mypy_analysis" in result
            assert "ast_analysis" in result
            assert "summary" in result
            
            # Verify basic data types
            assert isinstance(result["tools_used"], list)
            assert isinstance(result["flake8_analysis"], dict)
            assert isinstance(result["pylint_analysis"], dict)
            assert isinstance(result["mypy_analysis"], dict)
            assert isinstance(result["ast_analysis"], dict)
            assert isinstance(result["summary"], dict)
            
            # Verify no errors in basic structure
            assert "error" not in result or result.get("error") is None
            
        finally:
            os.unlink(temp_file)

    def test_analyze_invalid_file_path(self):
        """Test analysis of non-existent file."""
        result = self.analyzer.analyze_python_file("/non/existent/file.py")
        assert "error" in result
        assert result["error"] == "Invalid Python file path"

    def test_analyze_non_python_file(self):
        """Test analysis of non-Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not Python code")
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            assert "error" in result
            assert result["error"] == "Invalid Python file path"
        finally:
            os.unlink(temp_file)

    def test_ast_analysis_basic_functionality(self):
        """Test AST analysis with known code patterns."""
        test_code = '''
class TestClass:
    def __init__(self):
        self.value = 42
    
    def method_one(self):
        for i in range(10):
            if i % 2 == 0:
                print(i)
    
    def method_two(self):
        return self.value * 2

def function_one():
    pass

def function_two():
    pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            ast_analysis = result["ast_analysis"]
            
            # Verify AST analysis structure
            assert isinstance(ast_analysis, dict)
            
            # Should have detected classes and functions
            if "classes" in ast_analysis:
                assert isinstance(ast_analysis["classes"], list)
            if "functions" in ast_analysis:
                assert isinstance(ast_analysis["functions"], list)
            if "complexity_metrics" in ast_analysis:
                assert isinstance(ast_analysis["complexity_metrics"], dict)
                
        finally:
            os.unlink(temp_file)

    def test_syntax_error_handling(self):
        """Test handling of Python files with syntax errors."""
        test_code = '''
def broken_function(:
    print("This has a syntax error"
    return None
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            
            # Should handle syntax errors gracefully
            assert isinstance(result, dict)
            # May have error in AST analysis but shouldn't crash
            if "ast_analysis" in result and isinstance(result["ast_analysis"], dict):
                # AST analysis might contain error info
                assert "error" in result["ast_analysis"] or "classes" in result["ast_analysis"]
                
        finally:
            os.unlink(temp_file)

    def test_empty_file_analysis(self):
        """Test analysis of empty Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")  # Empty file
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            
            assert isinstance(result, dict)
            assert "ast_analysis" in result
            assert isinstance(result["ast_analysis"], dict)
            
        finally:
            os.unlink(temp_file)

    def test_complex_python_code_analysis(self):
        """Test analysis of more complex Python code."""
        test_code = '''
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class DataProcessor:
    """A class for processing data with various methods."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data: List[Dict[str, Any]] = []
        self.processed_count = 0
    
    def load_data(self, file_path: str) -> bool:
        """Load data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                self.data = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            return False
    
    def process_data(self) -> Optional[List[Dict[str, Any]]]:
        """Process the loaded data."""
        if not self.data:
            return None
        
        processed = []
        for item in self.data:
            if self._validate_item(item):
                processed_item = self._transform_item(item)
                processed.append(processed_item)
                self.processed_count += 1
        
        return processed
    
    def _validate_item(self, item: Dict[str, Any]) -> bool:
        """Validate a single data item."""
        required_fields = ['id', 'name', 'value']
        return all(field in item for field in required_fields)
    
    def _transform_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single data item."""
        return {
            'id': item['id'],
            'name': item['name'].strip().title(),
            'value': float(item['value']),
            'processed_at': datetime.now().isoformat()
        }

def main():
    """Main function to demonstrate usage."""
    processor = DataProcessor({"debug": True})
    if processor.load_data("data.json"):
        results = processor.process_data()
        print(f"Processed {processor.processed_count} items")

if __name__ == "__main__":
    main()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            
            # Comprehensive verification
            assert isinstance(result, dict)
            assert result["file_path"] == temp_file
            assert "analysis_timestamp" in result
            assert isinstance(result["tools_used"], list)
            
            # AST analysis should work
            ast_analysis = result["ast_analysis"]
            assert isinstance(ast_analysis, dict)
            
            # Summary should be generated
            summary = result["summary"]
            assert isinstance(summary, dict)
            
        finally:
            os.unlink(temp_file)

    @patch('subprocess.run')
    def test_flake8_analysis_mocked(self, mock_subprocess):
        """Test flake8 analysis with mocked subprocess."""
        # Mock flake8 output
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="test.py:1:1: E302 expected 2 blank lines",
            stderr=""
        )
        
        # Create analyzer with flake8 available
        analyzer = StaticAnalyzer()
        analyzer.tools_available["flake8"] = True
        
        test_code = 'print("hello")'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = analyzer.analyze_python_file(temp_file)
            
            # Should have flake8 analysis
            assert "flake8_analysis" in result
            assert isinstance(result["flake8_analysis"], dict)
            assert "flake8" in result["tools_used"]
            
        finally:
            os.unlink(temp_file)

    def test_summary_generation(self):
        """Test that summary is properly generated."""
        test_code = '''
def simple_function():
    """A simple function."""
    return "Hello, World!"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            
            summary = result["summary"]
            assert isinstance(summary, dict)
            
            # Summary should contain useful information
            # Structure depends on implementation, but should be dict
            for key, value in summary.items():
                assert isinstance(key, str)
                # Values can be various types but should be JSON-serializable
                
        finally:
            os.unlink(temp_file)

    def test_data_structure_consistency(self):
        """Test that all analysis results maintain consistent data structures."""
        test_code = '''
class TestClass:
    def test_method(self):
        return True
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = self.analyzer.analyze_python_file(temp_file)
            
            # Verify all expected keys exist
            expected_keys = [
                "file_path", "analysis_timestamp", "tools_used",
                "flake8_analysis", "pylint_analysis", "mypy_analysis",
                "ast_analysis", "summary"
            ]
            
            for key in expected_keys:
                assert key in result, f"Missing key: {key}"
            
            # Verify types are consistent
            assert isinstance(result["file_path"], str)
            assert isinstance(result["analysis_timestamp"], str)
            assert isinstance(result["tools_used"], list)
            
            # All analysis sections should be dicts
            analysis_sections = [
                "flake8_analysis", "pylint_analysis", "mypy_analysis",
                "ast_analysis", "summary"
            ]
            
            for section in analysis_sections:
                assert isinstance(result[section], dict), f"{section} should be a dict"
            
            # Tools used should contain strings
            for tool in result["tools_used"]:
                assert isinstance(tool, str)
                
        finally:
            os.unlink(temp_file)


class TestStaticAnalyzerIntegration:
    """Integration tests for StaticAnalyzer with MarkMate workflow."""
    
    def test_integration_with_extraction_workflow(self):
        """Test that static analysis integrates properly with MarkMate extraction."""
        # This would test the interface between static analysis and the broader
        # extract → grade workflow
        
        analyzer = StaticAnalyzer()
        
        # Test with a typical student submission
        student_code = '''
def calculate_average(numbers):
    total = 0
    count = 0
    for num in numbers:
        total += num
        count += 1
    return total / count

# Test the function
nums = [1, 2, 3, 4, 5]
avg = calculate_average(nums)
print(f"Average: {avg}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(student_code)
            temp_file = f.name
        
        try:
            result = analyzer.analyze_python_file(temp_file)
            
            # Result should be suitable for grading workflow
            assert isinstance(result, dict)
            assert "summary" in result
            
            # Should be JSON serializable (important for MarkMate workflow)
            import json
            json_str = json.dumps(result, default=str)  # default=str for datetime
            assert isinstance(json_str, str)
            
            # Should be able to deserialize
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)
            
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Static Analysis Tests...")
    
    # Basic functionality test
    analyzer = StaticAnalyzer()
    print(f"Analyzer initialized with tools: {list(analyzer.tools_available.keys())}")
    
    # Test with simple code
    test_code = 'print("Hello, World!")'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        result = analyzer.analyze_python_file(temp_file)
        print(f"Analysis result type: {type(result)}")
        print(f"Analysis result keys: {list(result.keys())}")
        print("Basic test passed!")
    finally:
        os.unlink(temp_file)
    
    print("Tests completed!")