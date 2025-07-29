"""
Comprehensive tests for Office Extractor with International Encoding Support

Tests the OfficeExtractor's ability to handle CSV, Excel, and PowerPoint files
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

from mark_mate.extractors.office_extractor import OfficeExtractor
from mark_mate.extractors.models import ExtractionResult, FileInfo


class TestOfficeExtractorBasic:
    """Test basic OfficeExtractor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = OfficeExtractor()

    def test_extractor_initialization(self):
        """Test extractor initializes with correct structure."""
        assert hasattr(self.extractor, 'extractor_name')
        assert hasattr(self.extractor, 'supported_extensions')
        assert self.extractor.extractor_name == "office_extractor"
        assert isinstance(self.extractor.supported_extensions, list)
        assert ".csv" in self.extractor.supported_extensions
        assert ".xlsx" in self.extractor.supported_extensions
        assert ".pptx" in self.extractor.supported_extensions

    def test_can_extract_supported_files(self):
        """Test file extension detection."""
        # Supported files
        assert self.extractor.can_extract("data.csv") is True
        assert self.extractor.can_extract("report.xlsx") is True
        assert self.extractor.can_extract("slides.pptx") is True
        assert self.extractor.can_extract("table.tsv") is True
        
        # Unsupported files
        assert self.extractor.can_extract("document.pdf") is False
        assert self.extractor.can_extract("image.png") is False
        assert self.extractor.can_extract("code.py") is False


class TestOfficeExtractorCSV:
    """Test CSV extraction with international encoding support."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = OfficeExtractor()

    def test_csv_basic_extraction(self):
        """Test basic CSV file extraction."""
        csv_content = "name,age,city\\nJohn,25,NYC\\nJane,30,LA"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert isinstance(result, ExtractionResult)
            assert result.success is True
            assert isinstance(result.content, str)
            assert result.extractor == "office_extractor"
            assert result.file_info.extension == ".csv"
            
        finally:
            os.unlink(temp_file)

    def test_csv_international_encoding(self):
        """Test CSV with international characters from ESL students."""
        # CSV with multiple international character sets
        csv_content = '''Name,City,Country,Notes
张三,北京,中国,Software Engineer
María García,Madrid,España,Data Analyst  
Владимир,Москва,Россия,Product Manager
Ahmed,القاهرة,مصر,Designer
田中太郎,東京,日本,Developer
François,Paris,France,Étudiant
José,São Paulo,Brasil,Desenvolvedor'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            # Check that international characters are preserved
            assert "张三" in result.content
            assert "María" in result.content
            assert "Владимир" in result.content
            assert "القاهرة" in result.content
            assert "田中太郎" in result.content
            
            # Check analysis includes encoding info if available
            if "encoding_used" in result.analysis:
                assert result.analysis["encoding_used"] is not None
                
        finally:
            os.unlink(temp_file)

    def test_csv_with_delimiter_detection(self):
        """Test TSV (tab-separated) file handling."""
        tsv_content = "name\tage\tcity\\nJohn\t25\tNYC\\nJane\t30\tLA"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
            f.write(tsv_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            assert result.file_info.extension == ".tsv"
            # Should detect tab delimiter
            assert "tab" in result.content.lower() or "delimiter" in result.analysis
            
        finally:
            os.unlink(temp_file)

    def test_csv_large_file(self):
        """Test handling of large CSV files."""
        # Generate a larger CSV file
        csv_lines = ["name,age,city"]
        for i in range(1000):
            csv_lines.append(f"User{i},{20+i%50},City{i%10}")
        csv_content = "\\n".join(csv_lines)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            assert len(result.content) > 1000  # Should contain substantial content
            
        finally:
            os.unlink(temp_file)


class TestOfficeExtractorErrorHandling:
    """Test error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = OfficeExtractor()

    def test_non_existent_file(self):
        """Test handling of non-existent files."""
        result = self.extractor.extract_content("/non/existent/file.csv")
        
        assert isinstance(result, ExtractionResult)
        assert result.success is False
        assert result.error is not None

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not an office file")
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert isinstance(result, ExtractionResult)
            assert result.success is False
            assert result.error is not None
            
        finally:
            os.unlink(temp_file)

    def test_empty_csv_file(self):
        """Test handling of empty CSV files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")  # Empty file
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Should handle empty files gracefully
            assert isinstance(result, ExtractionResult)
            # May succeed with empty content or fail gracefully
            
        finally:
            os.unlink(temp_file)

    def test_malformed_csv(self):
        """Test handling of malformed CSV files."""
        # CSV with inconsistent columns
        csv_content = '''name,age,city
John,25,NYC,extra
Jane
incomplete,row'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Should handle malformed CSV gracefully
            assert isinstance(result, ExtractionResult)
            # Most CSV readers are tolerant of malformed data
            
        finally:
            os.unlink(temp_file)


class TestOfficeExtractorIntegration:
    """Integration tests using existing test fixtures."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = OfficeExtractor()
        self.fixtures_path = Path(__file__).parent / "fixtures"

    def test_with_existing_encoding_fixtures(self):
        """Test with existing encoding test fixtures if they exist."""
        encoding_samples_path = self.fixtures_path / "test_encoding_samples"
        
        if encoding_samples_path.exists():
            # Test any CSV files in the encoding samples
            for file_path in encoding_samples_path.glob("*.csv"):
                if file_path.exists():
                    result = self.extractor.extract_content(str(file_path))
                    assert isinstance(result, ExtractionResult)
                    # Should either succeed or fail gracefully

    def test_with_esl_submission_fixtures(self):
        """Test with ESL submission fixtures if they exist."""
        esl_path = self.fixtures_path / "test_esl_submission"
        
        if esl_path.exists():
            # Look for any office files in ESL submissions
            for pattern in ["*.csv", "*.xlsx", "*.pptx", "*.tsv"]:
                for file_path in esl_path.glob(pattern):
                    if file_path.exists():
                        result = self.extractor.extract_content(str(file_path))
                        assert isinstance(result, ExtractionResult)


class TestOfficeExtractorPydanticModels:
    """Test Pydantic model integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = OfficeExtractor()

    def test_extraction_result_serialization(self):
        """Test that results can be serialized/deserialized."""
        csv_content = "name,age\\nJohn,25\\nJane,30"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Test JSON serialization
            import json
            result_dict = result.model_dump()
            
            # Handle pandas dtypes which aren't JSON serializable
            def make_json_serializable(obj):
                if hasattr(obj, 'to_dict') and callable(obj.to_dict):
                    return obj.to_dict()
                elif hasattr(obj, '__str__'):
                    return str(obj)
                return obj
            
            # Convert pandas dtypes to strings for JSON serialization
            if 'analysis' in result_dict and isinstance(result_dict['analysis'], dict):
                for key, value in result_dict['analysis'].items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if hasattr(subvalue, 'to_dict'):
                                result_dict['analysis'][key][subkey] = subvalue.to_dict()
                            elif not isinstance(subvalue, (str, int, float, bool, list, dict, type(None))):
                                result_dict['analysis'][key][subkey] = str(subvalue)
            
            json_str = json.dumps(result_dict)
            assert isinstance(json_str, str)
            
            # Test deserialization
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)
            assert deserialized["success"] == result.success
            assert deserialized["extractor"] == result.extractor
            
        finally:
            os.unlink(temp_file)

    def test_file_info_structure(self):
        """Test FileInfo model structure."""
        csv_content = "name,age\\nJohn,25"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert isinstance(result.file_info, FileInfo)
            assert result.file_info.filename == os.path.basename(temp_file)
            assert result.file_info.extension == ".csv"
            assert result.file_info.extractor == "office_extractor"
            assert result.file_info.size >= 0
            
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Office Extractor Tests...")
    
    extractor = OfficeExtractor()
    print(f"Extractor initialized: {extractor.extractor_name}")
    print(f"Supported extensions: {extractor.supported_extensions}")
    
    # Test with simple CSV
    test_csv = "name,age,city\\nJohn,25,NYC\\nJane,30,LA"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(test_csv)
        temp_file = f.name
    
    try:
        result = extractor.extract_content(temp_file)
        print(f"Extraction result type: {type(result)}")
        print(f"Extraction success: {result.success}")
        print("Basic test passed!")
    finally:
        os.unlink(temp_file)
    
    print("Tests completed!")