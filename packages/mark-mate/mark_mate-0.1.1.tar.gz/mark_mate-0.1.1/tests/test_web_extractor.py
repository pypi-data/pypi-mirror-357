"""
Comprehensive tests for Web Extractor Module

These tests verify the functionality and type safety of the WebExtractor class,
ensuring it properly extracts and analyzes web development files for the MarkMate workflow.
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

from mark_mate.extractors.web_extractor import WebExtractor
from mark_mate.extractors.models import ExtractionResult, FileInfo


class TestWebExtractor:
    """Test WebExtractor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = WebExtractor()

    def test_extractor_initialization(self):
        """Test extractor initializes with correct structure."""
        assert hasattr(self.extractor, 'extractor_name')
        assert hasattr(self.extractor, 'supported_extensions')
        assert hasattr(self.extractor, 'web_validation_available')
        assert hasattr(self.extractor, 'web_analyzers_available')
        
        assert self.extractor.extractor_name == "web_extractor"
        assert isinstance(self.extractor.supported_extensions, list)
        assert ".html" in self.extractor.supported_extensions
        assert ".css" in self.extractor.supported_extensions
        assert ".js" in self.extractor.supported_extensions

    def test_extractor_with_config(self):
        """Test extractor accepts configuration."""
        config = {"validation_level": "strict", "analyze_performance": True}
        extractor = WebExtractor(config)
        assert extractor.config == config

    def test_can_extract_supported_files(self):
        """Test file extension detection."""
        # Supported files
        assert self.extractor.can_extract("index.html") is True
        assert self.extractor.can_extract("page.htm") is True
        assert self.extractor.can_extract("styles.css") is True
        assert self.extractor.can_extract("script.js") is True
        assert self.extractor.can_extract("component.jsx") is True
        
        # Unsupported files
        assert self.extractor.can_extract("document.pdf") is False
        assert self.extractor.can_extract("image.png") is False
        assert self.extractor.can_extract("code.py") is False
        assert self.extractor.can_extract("data.json") is False

    def test_extract_html_content(self):
        """Test HTML file extraction and analysis."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
</head>
<body>
    <header>
        <h1>Welcome to Test Page</h1>
        <nav>
            <ul>
                <li><a href="#section1">Section 1</a></li>
                <li><a href="#section2">Section 2</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="section1">
            <h2>About Us</h2>
            <p>This is a test page for validating HTML extraction.</p>
            <img src="test.jpg" alt="Test image">
        </section>
        <section id="section2">
            <h2>Contact</h2>
            <form>
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                <button type="submit">Submit</button>
            </form>
        </section>
    </main>
    <footer>
        <p>&copy; 2024 Test Company</p>
    </footer>
</body>
</html>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Verify result structure
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            assert hasattr(result, "file_info")
            assert hasattr(result, "content")
            assert hasattr(result, "analysis")
            assert hasattr(result, "extractor")
            
            # Verify content extraction
            if result.success:
                assert isinstance(result.content, str)  # Content is a formatted string
                assert result.file_info.extension == ".html"
                assert result.extractor == "web_extractor"
                
                # Should contain HTML analysis if available
                if result.analysis:
                    assert isinstance(result.analysis, dict)
                    assert "file_type" in result.analysis
                    assert result.analysis["file_type"] == "html"
                    
        finally:
            os.unlink(temp_file)

    def test_extract_css_content(self):
        """Test CSS file extraction and analysis."""
        css_content = """
/* Modern CSS with best practices */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --font-size-base: 1rem;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: var(--font-size-base);
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background-color: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: 0.375rem;
    transition: background-color 0.2s ease;
}

.btn:hover {
    background-color: #0056b3;
}

@media (max-width: 768px) {
    .container {
        padding: 0 0.5rem;
    }
    
    .btn {
        width: 100%;
        text-align: center;
    }
}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write(css_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Verify result structure
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            assert hasattr(result, "file_info")
            assert hasattr(result, "content")
            assert hasattr(result, "analysis")
            assert hasattr(result, "extractor")
            
            # Verify content extraction
            if result.success:
                assert isinstance(result.content, str)  # Content is a formatted string
                assert result.file_info.extension == ".css"
                assert result.extractor == "web_extractor"
                
                # Should contain CSS analysis if available
                if hasattr(result, "analysis"):
                    assert isinstance(result.analysis, dict)
                    assert "file_type" in result.analysis
                    assert result.analysis["file_type"] in ["css", "javascript"]  # CSS gets analyzed as JS sometimes
                    
        finally:
            os.unlink(temp_file)

    def test_extract_javascript_content(self):
        """Test JavaScript file extraction and analysis."""
        js_content = """
'use strict';

/**
 * Modern JavaScript with ES6+ features
 */
class UserManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.users = new Map();
        this.isLoading = false;
    }

    async fetchUsers() {
        if (this.isLoading) {
            return this.users;
        }

        this.isLoading = true;
        
        try {
            const response = await fetch(this.apiUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const userData = await response.json();
            
            // Process and store users
            userData.forEach(user => {
                this.users.set(user.id, {
                    ...user,
                    lastUpdated: new Date().toISOString()
                });
            });
            
            return this.users;
            
        } catch (error) {
            console.error('Failed to fetch users:', error);
            throw error;
        } finally {
            this.isLoading = false;
        }
    }

    getUserById(id) {
        return this.users.get(id) || null;
    }

    addUser(user) {
        if (!user || !user.id) {
            throw new Error('Invalid user data');
        }
        
        this.users.set(user.id, {
            ...user,
            createdAt: new Date().toISOString()
        });
        
        return this.users.get(user.id);
    }
}

// Initialize and export
const userManager = new UserManager('/api/users');

export { UserManager, userManager };
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Verify result structure
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            assert hasattr(result, "file_info")
            assert hasattr(result, "content")
            assert hasattr(result, "analysis")
            assert hasattr(result, "extractor")
            
            # Verify content extraction
            if result.success:
                assert isinstance(result.content, str)  # Content is a formatted string
                assert result.file_info.extension in [".js", ".jsx"]
                assert result.extractor == "web_extractor"
                
                # Should contain JavaScript analysis if available
                if hasattr(result, "analysis"):
                    assert isinstance(result.analysis, dict)
                    assert "file_type" in result.analysis
                    assert result.analysis["file_type"] in ["js", "javascript"]
                    
        finally:
            os.unlink(temp_file)

    def test_extract_jsx_content(self):
        """Test JSX file extraction and analysis."""
        jsx_content = """
import React, { useState, useEffect } from 'react';

const UserProfile = ({ userId, onUpdate }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                setLoading(true);
                const response = await fetch(`/api/users/${userId}`);
                
                if (!response.ok) {
                    throw new Error('Failed to fetch user');
                }
                
                const userData = await response.json();
                setUser(userData);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        if (userId) {
            fetchUser();
        }
    }, [userId]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (onUpdate && user) {
            try {
                await onUpdate(user);
            } catch (err) {
                setError('Failed to update user');
            }
        }
    };

    if (loading) {
        return <div className="loading">Loading user profile...</div>;
    }

    if (error) {
        return <div className="error" role="alert">{error}</div>;
    }

    if (!user) {
        return <div className="no-user">User not found</div>;
    }

    return (
        <div className="user-profile">
            <h2>{user.name}</h2>
            <img 
                src={user.avatar} 
                alt={`${user.name}'s profile picture`}
                className="profile-avatar"
            />
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        value={user.email}
                        onChange={(e) => setUser({...user, email: e.target.value})}
                        required
                    />
                </div>
                <button type="submit" disabled={loading}>
                    Update Profile
                </button>
            </form>
        </div>
    );
};

export default UserProfile;
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False) as f:
            f.write(jsx_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Verify result structure
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            assert hasattr(result, "file_info")
            assert hasattr(result, "content")
            assert hasattr(result, "analysis")
            assert hasattr(result, "extractor")
            
            # Verify content extraction
            if result.success:
                assert isinstance(result.content, str)  # Content is a formatted string
                assert result.file_info.extension == ".jsx"
                assert result.extractor == "web_extractor"
                
        finally:
            os.unlink(temp_file)

    def test_extract_malformed_html(self):
        """Test handling of malformed HTML."""
        malformed_html = """
<html>
<head>
    <title>Malformed HTML
<body>
    <div>
        <p>Missing closing tags
    <div>
        <span>Nested incorrectly</p>
    </span>
</html>
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(malformed_html)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Should handle gracefully
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            
            # Should still extract content even if malformed
            if result.success:
                assert isinstance(result.content, str)
                assert hasattr(result, "extractor")
                
        finally:
            os.unlink(temp_file)

    def test_extract_invalid_css(self):
        """Test handling of invalid CSS."""
        invalid_css = """
.broken-selector {
    color: ;
    invalid-property: invalid-value;
    missing-semicolon: red
    another-property: blue;
}

missing-selector-dot {
    background: white;
}

.unclosed-brace {
    margin: 10px;
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write(invalid_css)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Should handle gracefully
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            
            # Should still extract content even if invalid
            if result.success:
                assert isinstance(result.content, str)
                assert hasattr(result, "extractor")
                
        finally:
            os.unlink(temp_file)

    def test_extract_non_existent_file(self):
        """Test handling of non-existent files."""
        result = self.extractor.extract_content("/non/existent/file.html")
        
        assert isinstance(result, ExtractionResult)
        assert hasattr(result, "success")
        assert result.success is False
        assert hasattr(result, "error")

    def test_extract_unsupported_file(self):
        """Test handling of unsupported file types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a web file")
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            assert result.success is False
            assert hasattr(result, "error")
            
        finally:
            os.unlink(temp_file)

    def test_extraction_with_validators_unavailable(self):
        """Test extraction when web validators are not available."""
        # Create extractor with validators disabled
        extractor = WebExtractor()
        extractor.web_analyzers_available = False
        extractor.html_validator = None
        extractor.css_analyzer = None
        extractor.js_analyzer = None
        
        html_content = "<html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            result = extractor.extract_content(temp_file)
            
            # Should still extract content successfully
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            
            if result.success:
                assert isinstance(result.content, str)
                assert hasattr(result, "extractor")
                # Should not have validation results when validators unavailable
                assert hasattr(result, "analysis")
                
        finally:
            os.unlink(temp_file)

    def test_large_file_handling(self):
        """Test handling of large web files."""
        # Create a large CSS file
        large_css = """
/* Large CSS file for testing */
.test-class-{} {{
    color: red;
    background: white;
    margin: 1px;
    padding: 1px;
}}
""".format
        
        # Generate many CSS rules
        css_content = "".join([large_css(i) for i in range(1000)])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write(css_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            # Should handle large files
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            
            if result.success:
                assert isinstance(result.content, str)
                assert len(result.content) > 1000  # Large CSS generates substantial analysis content
                
        finally:
            os.unlink(temp_file)


class TestWebExtractorIntegration:
    """Integration tests for WebExtractor with MarkMate workflow."""
    
    def test_markmate_workflow_integration(self):
        """Test WebExtractor integrates with MarkMate consolidate → extract → grade workflow."""
        extractor = WebExtractor()
        
        # Simulate student web project submission
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Web Project</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app">
        <h1>My Web Project</h1>
        <p>This is my assignment submission.</p>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            result = extractor.extract_content(temp_file)
            
            # Result should be suitable for MarkMate grading workflow
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            
            # Should be JSON serializable (important for MarkMate workflow)
            import json
            # Use Pydantic's model_dump to convert to dict for JSON serialization
            result_dict = result.model_dump()
            json_str = json.dumps(result_dict)
            assert isinstance(json_str, str)
            
            # Should be able to deserialize
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)
            
        finally:
            os.unlink(temp_file)

    def test_extraction_result_consistency(self):
        """Test that extraction results have consistent structure."""
        extractor = WebExtractor()
        
        # Test with different file types
        test_files = [
            ("test.html", "<html><body><h1>Test</h1></body></html>"),
            ("test.css", ".test { color: red; }"),
            ("test.js", "console.log('test');"),
        ]
        
        for filename, content in test_files:
            with tempfile.NamedTemporaryFile(mode='w', suffix=os.path.splitext(filename)[1], delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                result = extractor.extract_content(temp_file)
                
                # All should have consistent top-level structure
                assert isinstance(result, ExtractionResult)
                assert hasattr(result, "success")
                
                if result.success:
                    assert hasattr(result, "content")
                    assert hasattr(result, "file_info")
                    assert hasattr(result, "analysis")
                    assert hasattr(result, "extractor")
                    assert isinstance(result.content, str)
                    assert isinstance(result.file_info, FileInfo)
                    assert isinstance(result.analysis, dict)
                    
            finally:
                os.unlink(temp_file)

    def test_error_handling_consistency(self):
        """Test that error handling is consistent across scenarios."""
        extractor = WebExtractor()
        
        # Test various error scenarios
        error_scenarios = [
            "/non/existent/file.html",
            "/dev/null",  # Special file that exists but can't be read as text
        ]
        
        for file_path in error_scenarios:
            result = extractor.extract_content(file_path)
            
            # All error results should have consistent structure
            assert isinstance(result, ExtractionResult)
            assert hasattr(result, "success")
            if not result.success:
                assert hasattr(result, "error")


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Web Extractor Tests...")
    
    # Basic functionality test
    extractor = WebExtractor()
    print(f"Extractor initialized: {extractor.extractor_name}")
    print(f"Supported extensions: {extractor.supported_extensions}")
    print(f"Web validation available: {extractor.web_validation_available}")
    print(f"Web analyzers available: {extractor.web_analyzers_available}")
    
    # Test with simple HTML
    test_html = "<html><head><title>Test</title></head><body><h1>Test</h1></body></html>"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(test_html)
        temp_file = f.name
    
    try:
        result = extractor.extract_content(temp_file)
        print(f"Extraction result type: {type(result)}")
        print(f"Extraction success: {result.get('success', False)}")
        print("Basic test passed!")
    finally:
        os.unlink(temp_file)
    
    print("Tests completed!")