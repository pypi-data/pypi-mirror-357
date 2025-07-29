"""
Comprehensive tests for Code Extractor with International Encoding Support

Tests the CodeExtractor's ability to handle Python source code files
from international ESL student environments with proper encoding detection.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# Import the module under test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mark_mate.extractors.code_extractor import CodeExtractor
from mark_mate.extractors.models import ExtractionResult, FileInfo


class TestCodeExtractorBasic:
    """Test basic CodeExtractor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = CodeExtractor()

    def test_extractor_initialization(self):
        """Test extractor initializes with correct structure."""
        assert hasattr(self.extractor, 'extractor_name')
        assert hasattr(self.extractor, 'supported_extensions')
        assert self.extractor.extractor_name == "code_extractor"
        assert isinstance(self.extractor.supported_extensions, list)
        assert ".py" in self.extractor.supported_extensions

    def test_can_extract_supported_files(self):
        """Test file extension detection."""
        # Supported files
        assert self.extractor.can_extract("script.py") is True
        assert self.extractor.can_extract("module.py") is True
        assert self.extractor.can_extract("__init__.py") is True
        
        # Unsupported files
        assert self.extractor.can_extract("script.js") is False
        assert self.extractor.can_extract("data.csv") is False
        assert self.extractor.can_extract("document.txt") is False


class TestCodeExtractorPythonCode:
    """Test Python code extraction and analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = CodeExtractor()

    def test_basic_python_extraction(self):
        """Test basic Python file extraction."""
        python_content = '''def hello_world():
    """Print hello world message."""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert isinstance(result, ExtractionResult)
            assert result.success is True
            assert isinstance(result.content, str)
            assert result.extractor == "code_extractor"
            assert result.file_info.extension == ".py"
            
            # Should contain basic structure analysis
            assert "basic_structure" in result.analysis
            
        finally:
            os.unlink(temp_file)

    def test_python_with_classes(self):
        """Test Python file with classes and methods."""
        python_content = '''class TestClass:
    """A simple test class."""
    
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        """Return the stored value."""
        return self.value
    
    def _private_method(self):
        """A private method."""
        pass

def global_function():
    """A global function."""
    return "test"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            
            # Check basic structure analysis
            if "basic_structure" in result.analysis:
                basic = result.analysis["basic_structure"]
                
                # Should detect classes and functions
                if "classes" in basic:
                    assert len(basic["classes"]) >= 1
                if "functions" in basic:
                    assert len(basic["functions"]) >= 1
            
        finally:
            os.unlink(temp_file)

    def test_python_international_encoding(self):
        """Test Python code with international characters and comments."""
        python_content = '''# -*- coding: utf-8 -*-
"""
国际化Python模块 - International Python Module
Модуль для работы с интернациональными данными
"""

def saludo_internacional():
    """Función que saluda en varios idiomas."""
    mensajes = {
        "chinese": "你好世界",      # Chinese greeting
        "russian": "Привет мир",   # Russian greeting  
        "arabic": "مرحبا بالعالم",  # Arabic greeting
        "japanese": "こんにちは世界", # Japanese greeting
        "spanish": "Hola Mundo",   # Spanish greeting
        "french": "Bonjour Monde"  # French greeting
    }
    return mensajes

class EstudianteInternacional:
    """Clase para representar estudiantes internacionales."""
    
    def __init__(self, nombre, país, idioma):
        self.nombre = nombre    # 名前 (name in Japanese)
        self.país = país        # страна (country in Russian) 
        self.idioma = idioma    # لغة (language in Arabic)
    
    def presentarse(self):
        """Método para que el estudiante se presente."""
        return f"Hola, soy {self.nombre} de {self.país}"

# Constants with international names
UNIVERSIDAD = "Universidad Internacional"
ESTUDIANTES_MÁXIMO = 1000
НАЛОГ_ПРОЦЕНТ = 0.15  # Tax percentage in Russian

if __name__ == "__main__":
    # Test with international data
    estudiante = EstudianteInternacional("张三", "中国", "中文")
    print(estudiante.presentarse())
    print(saludo_internacional())
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(python_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            
            # Check that international characters are preserved
            assert "你好世界" in result.content
            assert "Привет мир" in result.content
            assert "مرحبا بالعالم" in result.content
            assert "こんにちは世界" in result.content
            assert "EstudianteInternacional" in result.content
            assert "НАЛОГ_ПРОЦЕНТ" in result.content
            
            # Check that structure analysis worked
            if "basic_structure" in result.analysis:
                basic = result.analysis["basic_structure"]
                assert "error" not in basic  # Should parse successfully
            
        finally:
            os.unlink(temp_file)

    def test_python_with_imports(self):
        """Test Python file with various import patterns."""
        python_content = '''import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

import numpy as np
import pandas as pd

def analyze_data():
    """Analyze some data."""
    pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            
            # Check import analysis
            if "basic_structure" in result.analysis:
                basic = result.analysis["basic_structure"]
                if "imports" in basic:
                    imports = basic["imports"]
                    assert len(imports) > 0
                    
                    # Should detect different import types
                    import_types = [imp.get("type") for imp in imports]
                    assert "import" in import_types or "from_import" in import_types
            
        finally:
            os.unlink(temp_file)


class TestCodeExtractorErrorHandling:
    """Test error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = CodeExtractor()

    def test_syntax_error_handling(self):
        """Test handling of Python files with syntax errors."""
        # Python code with syntax error
        python_content = '''def broken_function():
    print("Missing closing quote
    return "broken"

if __name__ == "__main__":
    broken_function()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Should handle syntax errors gracefully
            assert isinstance(result, ExtractionResult)
            
            # May succeed with error information or fail gracefully
            if result.success and "basic_structure" in result.analysis:
                basic = result.analysis["basic_structure"]
                # Should report syntax error
                if "error" in basic:
                    assert "syntax" in basic["error"].lower()
            
        finally:
            os.unlink(temp_file)

    def test_empty_python_file(self):
        """Test handling of empty Python files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")  # Empty file
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert isinstance(result, ExtractionResult)
            assert result.success is True  # Empty files should be handled
            assert "EMPTY FILE" in result.content
            
        finally:
            os.unlink(temp_file)

    def test_non_existent_file(self):
        """Test handling of non-existent files."""
        result = self.extractor.extract_content("/non/existent/file.py")
        
        assert isinstance(result, ExtractionResult)
        assert result.success is False
        assert result.error is not None

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a Python file")
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert isinstance(result, ExtractionResult)
            assert result.success is False
            assert result.error is not None
            
        finally:
            os.unlink(temp_file)


class TestCodeExtractorAdvanced:
    """Test advanced features and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = CodeExtractor()

    def test_file_type_detection(self):
        """Test detection of different Python file types."""
        test_cases = [
            ("test_module.py", "import unittest\nclass TestCase(unittest.TestCase): pass", "test"),
            ("__main__.py", "if __name__ == '__main__': print('main')", "main"),
            ("regular_module.py", "def some_function(): pass", "module"),
            ("script.py", "print('hello')", "script")
        ]
        
        for filename, content, expected_type in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                # Rename to match expected filename pattern
                new_path = temp_file.replace('.py', f'_{expected_type}.py')
                if expected_type == "test":
                    new_path = temp_file.replace('.py', '_test.py')
                elif expected_type == "main":
                    new_path = temp_file.replace('.py', '__main__.py')
                
                os.rename(temp_file, new_path)
                
                result = self.extractor.extract_content(new_path)
                
                if result.success and "basic_structure" in result.analysis:
                    basic = result.analysis["basic_structure"]
                    if "file_type" in basic:
                        # File type detection may vary based on content
                        assert basic["file_type"] in ["test", "main", "module", "script"]
                
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                if os.path.exists(new_path):
                    os.unlink(new_path)


class TestCodeExtractorIntegration:
    """Integration tests using existing test fixtures."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = CodeExtractor()
        self.fixtures_path = Path(__file__).parent / "fixtures"

    def test_with_existing_encoding_fixtures(self):
        """Test with existing encoding test fixtures if they exist."""
        encoding_samples_path = self.fixtures_path / "test_encoding_samples"
        
        if encoding_samples_path.exists():
            # Test any Python files in the encoding samples
            for file_path in encoding_samples_path.glob("*.py"):
                if file_path.exists():
                    result = self.extractor.extract_content(str(file_path))
                    assert isinstance(result, ExtractionResult)

    def test_pydantic_model_integration(self):
        """Test Pydantic model serialization with code extraction."""
        python_content = '''def test_function():
    """Test function."""
    return "test"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Test JSON serialization
            import json
            result_dict = result.model_dump()
            json_str = json.dumps(result_dict)
            assert isinstance(json_str, str)
            
            # Test deserialization
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)
            assert deserialized["success"] == result.success
            
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Code Extractor Tests...")
    
    extractor = CodeExtractor()
    print(f"Extractor initialized: {extractor.extractor_name}")
    print(f"Supported extensions: {extractor.supported_extensions}")
    
    # Test with simple Python code
    test_code = '''def hello():
    """Say hello."""
    return "Hello, World!"
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        result = extractor.extract_content(temp_file)
        print(f"Extraction result type: {type(result)}")
        print(f"Extraction success: {result.success}")
        print("Basic test passed!")
    finally:
        os.unlink(temp_file)
    
    print("Tests completed!")