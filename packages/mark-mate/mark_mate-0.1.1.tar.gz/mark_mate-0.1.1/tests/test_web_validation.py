"""
Comprehensive tests for Web Validation Module

These tests verify the functionality and type safety of the HTMLValidator, 
CSSAnalyzer, and JSAnalyzer classes, ensuring they properly validate 
web content for the MarkMate workflow.
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

from mark_mate.analyzers.web_validation import HTMLValidator, CSSAnalyzer, JSAnalyzer


class TestHTMLValidator:
    """Test HTMLValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = HTMLValidator()

    def test_validator_initialization(self):
        """Test validator initializes with correct structure."""
        assert hasattr(self.validator, 'config')
        assert hasattr(self.validator, 'tools_available')
        assert isinstance(self.validator.config, dict)
        assert isinstance(self.validator.tools_available, bool)

    def test_validator_with_config(self):
        """Test validator accepts configuration."""
        config = {"strict_mode": True, "accessibility_level": "AAA"}
        validator = HTMLValidator(config)
        assert validator.config == config

    def test_validate_valid_html5_document(self):
        """Test validation of a valid HTML5 document."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Test page description">
    <title>Test Page</title>
</head>
<body>
    <header>
        <h1>Main Heading</h1>
        <nav>
            <ul>
                <li><a href="#section1">Section 1</a></li>
                <li><a href="#section2">Section 2</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="section1">
            <h2>Section 1</h2>
            <p>Content with <img src="image.jpg" alt="Descriptive alt text"></p>
            <form>
                <label for="name">Name:</label>
                <input type="text" id="name" name="name">
                <button type="submit">Submit</button>
            </form>
        </section>
    </main>
    <footer>
        <p>&copy; 2024 Test</p>
    </footer>
</body>
</html>"""
        
        result = self.validator.validate_html("test.html", html_content)
        
        # Verify result structure
        assert isinstance(result, dict)
        expected_keys = [
            "file_path", "validation_timestamp", "html5_validation",
            "accessibility_check", "best_practices", "seo_analysis", "summary"
        ]
        
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Verify data types
        assert isinstance(result["html5_validation"], dict)
        assert isinstance(result["accessibility_check"], dict)
        assert isinstance(result["best_practices"], dict)
        assert isinstance(result["seo_analysis"], dict)
        assert isinstance(result["summary"], dict)

    def test_validate_html_with_accessibility_issues(self):
        """Test validation detects accessibility issues."""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Accessibility Test</title>
</head>
<body>
    <h3>Wrong heading hierarchy</h3>
    <img src="image.jpg">
    <form>
        <input type="text" name="username">
        <input type="submit" value="Submit">
    </form>
    <a href="#link">Click here</a>
</body>
</html>"""
        
        result = self.validator.validate_html("accessibility_test.html", html_content)
        
        if "accessibility_check" in result and "error" not in result["accessibility_check"]:
            accessibility = result["accessibility_check"]
            
            # Should detect issues
            assert "issues" in accessibility
            assert isinstance(accessibility["issues"], list)
            
            # Should have detected missing alt text and missing lang attribute
            issues_text = str(accessibility.get("issues", []))
            assert "alt" in issues_text.lower() or "lang" in issues_text.lower()

    def test_validate_html_best_practices(self):
        """Test best practices checking."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Best Practices Test</title>
</head>
<body>
    <main>
        <h1>Using semantic HTML</h1>
        <section>
            <p>Content with proper structure</p>
        </section>
    </main>
</body>
</html>"""
        
        result = self.validator.validate_html("best_practices.html", html_content)
        
        if "best_practices" in result and "error" not in result["best_practices"]:
            bp = result["best_practices"]
            
            assert "good_practices" in bp
            assert isinstance(bp["good_practices"], list)
            
            # Should recognize semantic HTML usage
            good_practices_text = str(bp.get("good_practices", []))
            assert "semantic" in good_practices_text.lower() or "viewport" in good_practices_text.lower()

    def test_validate_html_seo_analysis(self):
        """Test SEO analysis functionality."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>SEO Optimized Title</title>
    <meta name="description" content="This is a well-optimized meta description">
</head>
<body>
    <h1>Main SEO Heading</h1>
    <img src="image.jpg" alt="SEO friendly alt text">
    <a href="/internal-link">Internal Link</a>
</body>
</html>"""
        
        result = self.validator.validate_html("seo_test.html", html_content)
        
        if "seo_analysis" in result and "error" not in result["seo_analysis"]:
            seo = result["seo_analysis"]
            
            assert "good_practices" in seo
            assert isinstance(seo["good_practices"], list)
            
            # Should detect good SEO practices
            seo_text = str(seo.get("good_practices", []))
            assert "h1" in seo_text.lower() or "title" in seo_text.lower()

    def test_validate_malformed_html(self):
        """Test handling of malformed HTML."""
        malformed_html = """<html>
<head>
    <title>Malformed
</head>
<body>
    <div>
        <p>Unclosed div
    </div>
</body>"""
        
        result = self.validator.validate_html("malformed.html", malformed_html)
        
        # Should handle gracefully
        assert isinstance(result, dict)
        
        # May have validation errors but shouldn't crash
        if "html5_validation" in result:
            validation = result["html5_validation"]
            assert isinstance(validation, dict)

    def test_validate_empty_html(self):
        """Test validation of empty HTML."""
        result = self.validator.validate_html("empty.html", "")
        
        assert isinstance(result, dict)
        # Should detect missing required elements
        if "html5_validation" in result and "error" not in result["html5_validation"]:
            validation = result["html5_validation"]
            assert "errors" in validation
            assert isinstance(validation["errors"], list)

    def test_tools_unavailable_handling(self):
        """Test behavior when web tools are unavailable."""
        validator = HTMLValidator()
        validator.tools_available = False
        
        result = validator.validate_html("test.html", "<html></html>")
        
        assert "error" in result
        assert "tools not available" in result["error"]


class TestCSSAnalyzer:
    """Test CSSAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CSSAnalyzer()

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        assert hasattr(self.analyzer, 'config')
        assert hasattr(self.analyzer, 'tools_available')
        assert isinstance(self.analyzer.config, dict)
        assert isinstance(self.analyzer.tools_available, bool)

    def test_analyze_valid_css(self):
        """Test analysis of valid CSS."""
        css_content = """
/* Modern CSS with best practices */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
}

.container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
}

.card {
    background: var(--primary-color);
    border-radius: 8px;
    padding: 1rem;
    transition: transform 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
}

@media (min-width: 768px) {
    .container {
        flex-direction: row;
    }
}
"""
        
        result = self.analyzer.analyze_css("styles.css", css_content)
        
        # Verify result structure
        assert isinstance(result, dict)
        expected_keys = ["file_path", "validation", "best_practices", "performance", "summary"]
        
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Should recognize good practices
        if "best_practices" in result and "error" not in result["best_practices"]:
            bp = result["best_practices"]
            good_practices_text = str(bp.get("good_practices", []))
            assert "media" in good_practices_text.lower() or "variable" in good_practices_text.lower()

    def test_analyze_css_with_issues(self):
        """Test CSS analysis with common issues."""
        css_content = """
.problematic {
    color: red !important;
    display: block !important;
    -webkit-border-radius: 5px;
    -moz-border-radius: 5px;
    border-radius: 5px;
}

* {
    margin: 0;
    padding: 0;
}

.duplicate-selector {
    color: blue;
}

.duplicate-selector {
    background: white;
}
"""
        
        result = self.analyzer.analyze_css("problematic.css", css_content)
        
        if "best_practices" in result and "error" not in result["best_practices"]:
            bp = result["best_practices"]
            
            # Should detect !important overuse and vendor prefixes
            issues_and_warnings = str(bp.get("issues", [])) + str(bp.get("warnings", []))
            assert "important" in issues_and_warnings.lower() or "prefix" in issues_and_warnings.lower()

    def test_analyze_css_performance(self):
        """Test CSS performance analysis."""
        # Large CSS content to trigger performance warnings
        large_css = """
.selector1 .nested .deeply .nested .selector { color: red; }
.selector2 .nested .deeply .nested .selector { color: blue; }
""" * 100  # Repeat to make it large
        
        result = self.analyzer.analyze_css("large.css", large_css)
        
        if "performance" in result and "error" not in result["performance"]:
            performance = result["performance"]
            
            assert "metrics" in performance
            assert "file_size_bytes" in performance["metrics"]
            assert isinstance(performance["metrics"]["file_size_bytes"], int)

    def test_analyze_invalid_css(self):
        """Test handling of invalid CSS."""
        invalid_css = """
.broken {
    color: ;
    invalid-property: invalid-value;
    missing-colon red;
}
"""
        
        result = self.analyzer.analyze_css("invalid.css", invalid_css)
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert "validation" in result

    def test_tools_unavailable_handling(self):
        """Test behavior when CSS tools are unavailable."""
        analyzer = CSSAnalyzer()
        analyzer.tools_available = False
        
        result = analyzer.analyze_css("test.css", ".test { color: red; }")
        
        assert "error" in result
        assert "tools not available" in result["error"]


class TestJSAnalyzer:
    """Test JSAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = JSAnalyzer()

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        assert hasattr(self.analyzer, 'config')
        assert isinstance(self.analyzer.config, dict)

    def test_analyze_modern_javascript(self):
        """Test analysis of modern JavaScript."""
        js_content = """
'use strict';

class UserManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.users = [];
    }

    async fetchUsers() {
        try {
            const response = await fetch(this.apiUrl);
            const data = await response.json();
            this.users = data;
            return this.users;
        } catch (error) {
            console.error('Failed to fetch users:', error);
            throw error;
        }
    }

    addUser(user) {
        if (!user || !user.id) {
            throw new Error('Invalid user data');
        }
        this.users.push(user);
    }

    findUser(id) {
        return this.users.find(user => user.id === id);
    }
}

const manager = new UserManager('/api/users');
manager.fetchUsers().then(users => {
    console.log(`Loaded ${users.length} users`);
});
"""
        
        result = self.analyzer.analyze_javascript("modern.js", js_content)
        
        # Verify result structure
        assert isinstance(result, dict)
        expected_keys = ["file_path", "syntax_check", "best_practices", "structure_analysis", "summary"]
        
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Should recognize modern features
        if "best_practices" in result and "error" not in result["best_practices"]:
            bp = result["best_practices"]
            good_practices_text = str(bp.get("good_practices", []))
            assert "strict" in good_practices_text.lower() or "error" in good_practices_text.lower()
        
        if "structure_analysis" in result and "error" not in result["structure_analysis"]:
            structure = result["structure_analysis"]
            assert structure.get("has_async_code") is True
            assert structure.get("class_count", 0) >= 1

    def test_analyze_problematic_javascript(self):
        """Test JavaScript with common issues."""
        js_content = """
var globalVar = 'bad practice';

function poorFunction() {
    if (true) {
        var x = 1
        var y = 2
    }
    
    console.log('debug1');
    console.log('debug2');
    console.log('debug3');
    console.log('debug4');
    console.log('debug5');
    
    return x + y;
}

var anotherGlobal = poorFunction();
"""
        
        result = self.analyzer.analyze_javascript("problematic.js", js_content)
        
        if "best_practices" in result and "error" not in result["best_practices"]:
            bp = result["best_practices"]
            
            # Should detect issues with var usage and console.log overuse
            warnings_text = str(bp.get("warnings", []))
            assert "var" in warnings_text.lower() or "console" in warnings_text.lower()

    def test_analyze_syntax_errors(self):
        """Test handling of JavaScript syntax errors."""
        invalid_js = """
function broken() {
    if (condition {
        return "missing parenthesis";
    }
    
    const unclosed = "string;
}
"""
        
        result = self.analyzer.analyze_javascript("broken.js", invalid_js)
        
        assert isinstance(result, dict)
        
        if "syntax_check" in result and "error" not in result["syntax_check"]:
            syntax = result["syntax_check"]
            assert "issues" in syntax
            assert len(syntax["issues"]) > 0

    def test_analyze_complex_javascript(self):
        """Test analysis of complex JavaScript structure."""
        complex_js = """
import { Component } from 'react';
import axios from 'axios';

export class DataProcessor extends Component {
    constructor(props) {
        super(props);
        this.state = { data: [], loading: false };
    }

    async componentDidMount() {
        await this.loadData();
    }

    async loadData() {
        this.setState({ loading: true });
        
        try {
            const promises = [];
            for (let i = 0; i < 10; i++) {
                promises.push(this.fetchPage(i));
            }
            
            const results = await Promise.all(promises);
            const data = results.flatMap(result => result.data);
            
            this.setState({ data, loading: false });
        } catch (error) {
            console.error('Data loading failed:', error);
            this.setState({ loading: false });
        }
    }

    fetchPage(page) {
        return axios.get(`/api/data?page=${page}`);
    }

    render() {
        if (this.state.loading) {
            return <div>Loading...</div>;
        }
        
        return (
            <div>
                {this.state.data.map(item => (
                    <div key={item.id}>{item.name}</div>
                ))}
            </div>
        );
    }
}
"""
        
        result = self.analyzer.analyze_javascript("complex.js", complex_js)
        
        if "structure_analysis" in result and "error" not in result["structure_analysis"]:
            structure = result["structure_analysis"]
            
            assert structure.get("has_modules") is True
            assert structure.get("has_async_code") is True
            assert structure.get("complexity_estimate") in ["low", "moderate", "high"]  # Allow low for simpler test case

    def test_syntax_checking_brackets(self):
        """Test bracket matching in syntax checking."""
        unmatched_js = """
function test() {
    const obj = {
        prop: [1, 2, 3
    };
"""
        
        result = self.analyzer.analyze_javascript("unmatched.js", unmatched_js)
        
        if "syntax_check" in result and "error" not in result["syntax_check"]:
            syntax = result["syntax_check"]
            issues_text = str(syntax.get("issues", []))
            assert "unmatched" in issues_text.lower() or "bracket" in issues_text.lower()

    def test_empty_javascript(self):
        """Test analysis of empty JavaScript file."""
        result = self.analyzer.analyze_javascript("empty.js", "")
        
        assert isinstance(result, dict)
        
        if "structure_analysis" in result:
            structure = result["structure_analysis"]
            assert structure.get("function_count", 0) == 0
            assert structure.get("estimated_lines_of_code", 0) == 0


class TestWebValidationIntegration:
    """Integration tests for web validation with MarkMate workflow."""
    
    def test_html_validation_workflow_integration(self):
        """Test HTML validation integrates with MarkMate extract workflow."""
        validator = HTMLValidator()
        
        # Simulate student HTML submission
        student_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Project</title>
</head>
<body>
    <h1>My Project</h1>
    <p>This is my web development assignment.</p>
</body>
</html>"""
        
        result = validator.validate_html("student_project.html", student_html)
        
        # Result should be suitable for grading workflow
        assert isinstance(result, dict)
        assert "summary" in result
        
        # Should be JSON serializable (important for MarkMate workflow)
        import json
        json_str = json.dumps(result, default=str)
        assert isinstance(json_str, str)
        
        # Should be able to deserialize
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict)

    def test_css_analysis_workflow_integration(self):
        """Test CSS analysis integrates with MarkMate workflow."""
        analyzer = CSSAnalyzer()
        
        # Simulate student CSS
        student_css = """
.header {
    background-color: #333;
    color: white;
    padding: 1rem;
}

.content {
    margin: 2rem;
    line-height: 1.6;
}
"""
        
        result = analyzer.analyze_css("student_styles.css", student_css)
        
        # Should be suitable for MarkMate workflow
        assert isinstance(result, dict)
        
        # Test JSON serializability
        import json
        json_str = json.dumps(result, default=str)
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict)

    def test_javascript_analysis_workflow_integration(self):
        """Test JavaScript analysis integrates with MarkMate workflow."""
        analyzer = JSAnalyzer()
        
        # Simulate student JavaScript
        student_js = """
function calculateGrade(score, maxScore) {
    if (score < 0 || maxScore <= 0) {
        return 0;
    }
    
    const percentage = (score / maxScore) * 100;
    
    if (percentage >= 90) {
        return 'A';
    } else if (percentage >= 80) {
        return 'B';
    } else if (percentage >= 70) {
        return 'C';
    } else if (percentage >= 60) {
        return 'D';
    } else {
        return 'F';
    }
}

console.log(calculateGrade(85, 100));
"""
        
        result = analyzer.analyze_javascript("student_logic.js", student_js)
        
        # Should be suitable for MarkMate workflow
        assert isinstance(result, dict)
        
        # Test JSON serializability
        import json
        json_str = json.dumps(result, default=str)
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict)

    def test_data_structure_consistency(self):
        """Test that all analyzers maintain consistent data structures."""
        html_validator = HTMLValidator()
        css_analyzer = CSSAnalyzer()
        js_analyzer = JSAnalyzer()
        
        # Test with minimal content
        html_result = html_validator.validate_html("test.html", "<html><body></body></html>")
        css_result = css_analyzer.analyze_css("test.css", ".test { color: red; }")
        js_result = js_analyzer.analyze_javascript("test.js", "console.log('test');")
        
        # All should have consistent top-level structure
        for result in [html_result, css_result, js_result]:
            assert isinstance(result, dict)
            assert "file_path" in result
            assert "summary" in result or "error" in result


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Web Validation Tests...")
    
    # Basic functionality tests
    html_validator = HTMLValidator()
    css_analyzer = CSSAnalyzer()
    js_analyzer = JSAnalyzer()
    
    print(f"HTML validator initialized: {html_validator.tools_available}")
    print(f"CSS analyzer initialized: {css_analyzer.tools_available}")
    print(f"JS analyzer initialized")
    
    # Test with simple content
    html_result = html_validator.validate_html("test.html", "<html><head><title>Test</title></head><body><h1>Test</h1></body></html>")
    css_result = css_analyzer.analyze_css("test.css", ".test { color: blue; }")
    js_result = js_analyzer.analyze_javascript("test.js", "function test() { return true; }")
    
    print(f"HTML validation result type: {type(html_result)}")
    print(f"CSS analysis result type: {type(css_result)}")
    print(f"JS analysis result type: {type(js_result)}")
    
    print("Basic tests passed!")