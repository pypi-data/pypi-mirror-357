"""
Comprehensive tests for React Analysis Module

These tests capture the expected behavior of the ReactAnalyzer, TypeScriptAnalyzer, 
and PackageAnalyzer classes before rewriting for type safety.
"""

import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime

# Import the current module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mark_mate.analyzers.react_analysis import ReactAnalyzer, TypeScriptAnalyzer, BuildConfigAnalyzer


class TestReactAnalyzer:
    """Test ReactAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ReactAnalyzer()

    def test_functional_component_detection(self):
        """Test detection of functional components."""
        source_code = """
        import React from 'react';
        
        const MyComponent = () => {
            return <div>Hello World</div>;
        };
        
        export default MyComponent;
        """
        
        result = self.analyzer.analyze_component("test.jsx", source_code)
        
        # Verify structure
        assert "component_analysis" in result
        assert "jsx_analysis" in result
        assert "hooks_analysis" in result
        assert "props_analysis" in result
        assert "best_practices" in result
        assert "summary" in result
        
        # Verify component detection
        component = result["component_analysis"]
        assert component["component_type"] in ["function", "functional", "arrow_functional"]
        assert component["component_name"] == "MyComponent"
        assert component["is_default_export"] is True

    def test_class_component_detection(self):
        """Test detection of class components."""
        source_code = """
        import React, { Component } from 'react';
        
        class MyClassComponent extends Component {
            render() {
                return <div>Hello World</div>;
            }
        }
        
        export default MyClassComponent;
        """
        
        result = self.analyzer.analyze_component("test.jsx", source_code)
        
        component = result["component_analysis"]
        assert component["component_type"] in ["class", "Class", "class_component"]
        assert component["component_name"] == "MyClassComponent"

    def test_jsx_pattern_analysis(self):
        """Test JSX pattern detection."""
        source_code = """
        const Component = () => {
            const items = [1, 2, 3];
            const isVisible = true;
            
            return (
                <div className="container" style={{color: 'red'}}>
                    {isVisible && <p>Visible content</p>}
                    {items.map(item => <span key={item}>{item}</span>)}
                    <button onClick={handleClick}>Click me</button>
                </div>
            );
        };
        """
        
        result = self.analyzer.analyze_component("test.jsx", source_code)
        jsx = result["jsx_analysis"]
        
        # Should detect conditional rendering
        assert jsx["conditional_rendering"] is not None
        assert jsx["list_rendering"] is True
        assert jsx["css_classes"] is True
        assert jsx["inline_styles"] is True
        
        # Should detect JSX elements
        assert "jsx_elements" in jsx
        assert isinstance(jsx["jsx_elements"], list)

    def test_hooks_analysis(self):
        """Test React hooks detection and analysis."""
        source_code = """
        import React, { useState, useEffect, useCallback } from 'react';
        
        const HooksComponent = () => {
            const [count, setCount] = useState(0);
            const [data, setData] = useState(null);
            
            useEffect(() => {
                fetchData();
            }, []);
            
            const handleClick = useCallback(() => {
                setCount(count + 1);
            }, [count]);
            
            return <div>{count}</div>;
        };
        """
        
        result = self.analyzer.analyze_component("test.jsx", source_code)
        hooks = result["hooks_analysis"]
        
        assert "hooks_used" in hooks
        assert "useState" in hooks["hooks_used"]
        assert "useEffect" in hooks["hooks_used"]
        assert "useCallback" in hooks["hooks_used"]
        
        assert "hooks_count" in hooks
        assert hooks["hooks_count"]["useState"] >= 2

    def test_props_analysis(self):
        """Test props pattern detection."""
        source_code = """
        interface Props {
            title: string;
            count: number;
            onClick: () => void;
        }
        
        const Component = ({ title, count, onClick }: Props) => {
            return (
                <div>
                    <h1>{title}</h1>
                    <p>Count: {count}</p>
                    <button onClick={onClick}>Click</button>
                </div>
            );
        };
        """
        
        result = self.analyzer.analyze_component("test.tsx", source_code)
        props = result["props_analysis"]
        
        assert "destructured_props" in props
        assert "title" in str(props["destructured_props"])

    def test_best_practices_scoring(self):
        """Test best practices analysis and scoring."""
        good_source = """
        const GoodComponent = ({ items }) => {
            return (
                <ul>
                    {items.map(item => (
                        <li key={item.id}>{item.name}</li>
                    ))}
                </ul>
            );
        };
        """
        
        bad_source = """
        const BadComponent = ({ items }) => {
            return (
                <ul>
                    {items.map(item => (
                        <li>{item.name}</li>
                    ))}
                </ul>
            );
        };
        """
        
        good_result = self.analyzer.analyze_component("good.jsx", good_source)
        bad_result = self.analyzer.analyze_component("bad.jsx", bad_source)
        
        good_bp = good_result["best_practices"]
        bad_bp = bad_result["best_practices"]
        
        # Good component should have higher score
        assert good_bp["score"] > bad_bp["score"]
        
        # Bad component should have issues
        assert len(bad_bp["issues"]) > 0

    def test_error_handling(self):
        """Test error handling for invalid code."""
        invalid_source = "This is not valid JavaScript/JSX code {"
        
        result = self.analyzer.analyze_component("invalid.jsx", invalid_source)
        
        # Should handle gracefully
        assert isinstance(result, dict)

    def test_summary_generation(self):
        """Test summary generation."""
        source_code = """
        const Component = () => {
            return <div>Hello</div>;
        };
        """
        
        result = self.analyzer.analyze_component("test.jsx", source_code)
        summary = result["summary"]
        
        assert "component_quality" in summary
        assert "complexity_level" in summary
        assert "total_issues" in summary
        assert isinstance(summary["total_issues"], int)


class TestTypeScriptAnalyzer:
    """Test TypeScriptAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TypeScriptAnalyzer()

    def test_type_analysis(self):
        """Test TypeScript type detection."""
        source_code = """
        type User = {
            id: number;
            name: string;
            email?: string;
        };
        
        const user: User = {
            id: 1,
            name: "John"
        };
        """
        
        result = self.analyzer.analyze_typescript("test.ts", source_code)
        
        assert "type_analysis" in result
        types = result["type_analysis"]
        assert "type_aliases" in types or "primitive_types" in types

    def test_interface_analysis(self):
        """Test interface detection."""
        source_code = """
        interface UserInterface {
            id: number;
            getName(): string;
        }
        
        class User implements UserInterface {
            id: number;
            getName(): string {
                return "test";
            }
        }
        """
        
        result = self.analyzer.analyze_typescript("test.ts", source_code)
        
        assert "interface_analysis" in result
        interfaces = result["interface_analysis"]
        assert "interfaces" in interfaces or "interface_properties" in interfaces

    def test_generic_analysis(self):
        """Test generic type detection."""
        source_code = """
        function identity<T>(arg: T): T {
            return arg;
        }
        
        const result = identity<string>("hello");
        """
        
        result = self.analyzer.analyze_typescript("test.ts", source_code)
        
        assert "generic_analysis" in result


class TestBuildConfigAnalyzer:
    """Test BuildConfigAnalyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = BuildConfigAnalyzer()

    def test_package_json_analysis(self):
        """Test package.json analysis."""
        package_data = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "typescript": "^4.0.0"
            },
            "devDependencies": {
                "eslint": "^8.0.0",
                "@types/react": "^18.0.0"
            },
            "scripts": {
                "build": "webpack",
                "test": "jest",
                "dev": "webpack-dev-server"
            }
        }
        
        result = self.analyzer.analyze_package_json("package.json", package_data)
        
        assert "build_analysis" in result
        assert "dependency_analysis" in result
        assert "script_analysis" in result
        assert "quality_tools" in result

    def test_dependency_analysis(self):
        """Test dependency categorization."""
        package_data = {
            "dependencies": {
                "react": "^18.0.0",
                "lodash": "^4.0.0"
            },
            "devDependencies": {
                "typescript": "^4.0.0",
                "eslint": "^8.0.0"
            }
        }
        
        result = self.analyzer.analyze_package_json("package.json", package_data)
        deps = result["dependency_analysis"]
        
        assert "framework_dependencies" in deps
        assert "development_count" in deps
        assert "total_dependencies" in deps

    def test_build_tool_detection(self):
        """Test build tool detection."""
        package_data = {
            "devDependencies": {
                "webpack": "^5.0.0",
                "vite": "^4.0.0"
            },
            "scripts": {
                "build": "webpack"
            }
        }
        
        result = self.analyzer.analyze_package_json("package.json", package_data)
        build_analysis = result["build_analysis"]
        
        assert "primary_build_tool" in build_analysis

    def test_quality_tools_detection(self):
        """Test quality tools detection."""
        package_data = {
            "devDependencies": {
                "eslint": "^8.0.0",
                "prettier": "^2.0.0",
                "jest": "^29.0.0"
            }
        }
        
        result = self.analyzer.analyze_package_json("package.json", package_data)
        quality = result["quality_tools"]
        
        assert "linting" in quality
        assert "testing" in quality


# Integration tests
class TestReactAnalysisIntegration:
    """Test integration scenarios."""

    def test_react_extractor_integration(self):
        """Test that the module works with ReactExtractor."""
        # This is a placeholder for integration testing
        # Should verify the output format matches ReactExtractor expectations
        analyzer = ReactAnalyzer()
        
        sample_component = """
        const App = () => {
            return <div>Hello World</div>;
        };
        export default App;
        """
        
        result = analyzer.analyze_component("App.jsx", sample_component)
        
        # Verify the expected structure for ReactExtractor
        required_keys = [
            "file_path", "analysis_timestamp", "component_analysis",
            "jsx_analysis", "hooks_analysis", "props_analysis", 
            "best_practices", "summary"
        ]
        
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_output_format_consistency(self):
        """Test that output format is consistent."""
        analyzer = ReactAnalyzer()
        
        # Test with various inputs
        test_cases = [
            "const A = () => <div/>;",
            "class B extends Component { render() { return <div/>; } }",
            "function C() { return <div/>; }",
        ]
        
        for i, source in enumerate(test_cases):
            result = analyzer.analyze_component(f"test{i}.jsx", source)
            
            # All should have the same structure
            assert isinstance(result, dict)
            assert "component_analysis" in result
            assert isinstance(result["component_analysis"], dict)


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running React Analysis Tests...")
    
    # Basic functionality test
    analyzer = ReactAnalyzer()
    result = analyzer.analyze_component("test.jsx", "const A = () => <div/>;")
    print(f"Basic test passed: {type(result)} with keys: {list(result.keys())}")
    
    print("Tests completed!")