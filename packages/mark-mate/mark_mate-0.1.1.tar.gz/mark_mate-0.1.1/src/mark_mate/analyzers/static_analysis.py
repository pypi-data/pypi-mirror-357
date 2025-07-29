"""
Static analysis module for Python code quality assessment.

This module provides comprehensive Python code analysis using multiple tools:
- flake8: Style and syntax checking
- pylint: Code quality and best practices
- mypy: Type checking and annotations
- AST analysis: Code structure and complexity
"""

from __future__ import annotations

import ast
import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union

logger = logging.getLogger(__name__)


# Type definitions for analysis results
class PylintIssue(TypedDict):
    """Structure for a pylint issue."""
    type: str
    message: str
    line: int
    column: int
    severity: str


class PylintSummary(TypedDict):
    """Structure for pylint summary statistics."""
    convention: int
    refactor: int
    warning: int
    error: int
    fatal: int


class PylintResult(TypedDict):
    """Structure for pylint analysis results."""
    return_code: int
    score: float
    issues: List[PylintIssue]
    summary: PylintSummary


class MypyIssue(TypedDict):
    """Structure for a mypy issue."""
    line: int
    severity: str
    message: str


class MypySummary(TypedDict):
    """Structure for mypy summary statistics."""
    errors: int
    notes: int
    total_issues: int


class MypyResult(TypedDict):
    """Structure for mypy analysis results."""
    return_code: int
    issues: List[MypyIssue]
    summary: MypySummary


class Flake8Issue(TypedDict):
    """Structure for a flake8 issue."""
    line: int
    column: int
    code: str
    message: str


class Flake8Result(TypedDict):
    """Structure for flake8 analysis results."""
    return_code: int
    issues: List[Flake8Issue]
    total_issues: int


class ComplexityMetrics(TypedDict):
    """Structure for complexity metrics."""
    total_functions: int
    cyclomatic_complexity: int
    max_complexity: int
    avg_complexity: float


class ASTResult(TypedDict):
    """Structure for AST analysis results."""
    classes: List[str]
    functions: List[str]
    imports: List[str]
    complexity_metrics: ComplexityMetrics
    lines_of_code: int
    docstring_coverage: float


class AnalysisSummary(TypedDict):
    """Structure for overall analysis summary."""
    total_issues: int
    code_quality_score: float
    complexity_rating: str
    tools_run: List[str]
    recommendations: List[str]


class StaticAnalysisResult(TypedDict):
    """Complete structure for static analysis results."""
    file_path: str
    analysis_timestamp: str
    source_length: int
    tools_used: List[str]
    flake8_analysis: Union[Flake8Result, Dict[str, str]]  # Dict with error key if failed
    pylint_analysis: Union[PylintResult, Dict[str, str]]  # Dict with error key if failed
    mypy_analysis: Union[MypyResult, Dict[str, str]]      # Dict with error key if failed
    ast_analysis: Union[ASTResult, Dict[str, str]]        # Dict with error key if failed
    summary: AnalysisSummary


def _ensure_list_field(data: Dict[str, Any], field_name: str) -> List[Any]:
    """Ensure a dictionary field is a list, converting if necessary.
    
    Args:
        data: Dictionary to check/modify.
        field_name: Name of the field that should be a list.
        
    Returns:
        The field value as a list.
    """
    if field_name not in data:
        data[field_name] = []
    elif not isinstance(data[field_name], list):
        # Convert non-list to single-item list if it has meaningful content
        if data[field_name] is not None and data[field_name] != "" and data[field_name] != 0:
            data[field_name] = [data[field_name]]
        else:
            data[field_name] = []
    return data[field_name]


def _ensure_dict_field(data: Dict[str, Any], field_name: str) -> Dict[str, Any]:
    """Ensure a dictionary field is a dict, converting if necessary.
    
    Args:
        data: Dictionary to check/modify.
        field_name: Name of the field that should be a dict.
        
    Returns:
        The field value as a dict.
    """
    if field_name not in data or not isinstance(data[field_name], dict):
        data[field_name] = {}
    return data[field_name]


def _safe_len(obj: Any) -> int:
    """Safely get length of an object, returning 0 for non-sized objects.
    
    Args:
        obj: Object to get length of.
        
    Returns:
        Length of object, or 0 if not applicable.
    """
    try:
        if hasattr(obj, '__len__'):
            return len(obj)
        return 0
    except (TypeError, AttributeError):
        return 0


def _safe_append(lst: Any, item: Any) -> None:
    """Safely append to a list-like object.
    
    Args:
        lst: List-like object to append to.
        item: Item to append.
    """
    if isinstance(lst, list):
        lst.append(item)
    else:
        logger.warning(f"Attempted to append to non-list: {type(lst)}")


class StaticAnalyzer:
    """Comprehensive Python static analysis using multiple tools."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the static analyzer.

        Args:
            config: Optional configuration for analysis tools.
        """
        self.config: Dict[str, Any] = config or {}
        self.tools_available: Dict[str, bool] = self._check_tool_availability()
        logger.info(
            f"Static analyzer initialized with tools: {list(self.tools_available.keys())}"
        )

    def _check_tool_availability(self) -> Dict[str, bool]:
        """Check which analysis tools are available.
        
        Returns:
            Dictionary mapping tool names to availability status.
        """
        tools: Dict[str, bool] = {}

        # Check flake8
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                ["flake8", "--version"], capture_output=True, text=True, timeout=10
            )
            tools["flake8"] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            tools["flake8"] = False

        # Check pylint
        try:
            result = subprocess.run(
                ["pylint", "--version"], capture_output=True, text=True, timeout=10
            )
            tools["pylint"] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            tools["pylint"] = False

        # Check mypy
        try:
            result = subprocess.run(
                ["mypy", "--version"], capture_output=True, text=True, timeout=10
            )
            tools["mypy"] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            tools["mypy"] = False

        return tools

    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:  # type: ignore[misc] - Complex return structure
        """Perform comprehensive analysis of a Python file.

        Args:
            file_path: Path to the Python file.

        Returns:
            Dictionary containing all analysis results.
        """
        if not os.path.exists(file_path) or not file_path.endswith(".py"):
            return {"error": "Invalid Python file path"}

        analysis_results: Dict[str, Any] = {
            "file_path": file_path,
            "analysis_timestamp": datetime.now().isoformat(),
            "tools_used": [],
            "flake8_analysis": {},
            "pylint_analysis": {},
            "mypy_analysis": {},
            "ast_analysis": {},
            "summary": {},
        }

        # Read source code for AST analysis
        try:
            with open(file_path, encoding="utf-8") as f:
                source_code: str = f.read()
            analysis_results["source_length"] = len(source_code)
        except Exception as e:
            logger.error(f"Could not read source file {file_path}: {e}")
            analysis_results["error"] = str(e)
            return analysis_results

        # Run flake8 analysis
        if self.tools_available.get("flake8", False):
            analysis_results["flake8_analysis"] = self._run_flake8(file_path)
            analysis_results["tools_used"].append("flake8")

        # Run pylint analysis
        if self.tools_available.get("pylint", False):
            analysis_results["pylint_analysis"] = self._run_pylint(file_path)
            analysis_results["tools_used"].append("pylint")

        # Run mypy analysis
        if self.tools_available.get("mypy", False):
            analysis_results["mypy_analysis"] = self._run_mypy(file_path)
            analysis_results["tools_used"].append("mypy")

        # Run AST analysis
        analysis_results["ast_analysis"] = self._analyze_ast(source_code)
        analysis_results["tools_used"].append("ast_analysis")

        # Generate summary
        analysis_results["summary"] = self._generate_summary(analysis_results)

        return analysis_results

    def _run_flake8(self, file_path: str) -> Dict[str, Any]:
        """Run flake8 analysis on a Python file.
        
        Args:
            file_path: Path to the Python file to analyze.
            
        Returns:
            Dictionary containing flake8 analysis results.
        """
        try:
            # Run flake8 with JSON output if possible, otherwise parse text
            result = subprocess.run(
                [
                    "flake8",
                    "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
                    "--max-line-length=88",  # More modern line length
                    "--extend-ignore=E203,W503",  # Common false positives
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            flake8_result: dict[str, Any] = {
                "return_code": result.returncode,
                "issues": [],
                "summary": {"errors": 0, "warnings": 0, "total_issues": 0},
            }

            if result.stdout:
                lines = result.stdout.strip().split("\\n")
                for line in lines:
                    if ":" in line and file_path in line:
                        parts = line.split(": ", 1)
                        if len(parts) == 2:
                            location, issue = parts
                            location_parts = location.split(":")
                            if len(location_parts) >= 3:
                                flake8_result["issues"].append(
                                    {
                                        "line": int(location_parts[-2])
                                        if location_parts[-2].isdigit()
                                        else 0,
                                        "column": int(location_parts[-1])
                                        if location_parts[-1].isdigit()
                                        else 0,
                                        "message": issue.strip(),
                                        "code": issue.split()[0]
                                        if issue
                                        else "UNKNOWN",
                                    }
                                )

                # Categorize issues
                for issue in flake8_result["issues"]:
                    code = issue.get("code", "")
                    if code.startswith("E"):
                        flake8_result["summary"]["errors"] += 1
                    elif code.startswith("W"):
                        flake8_result["summary"]["warnings"] += 1

                flake8_result["summary"]["total_issues"] = len(flake8_result["issues"])

            return flake8_result

        except subprocess.TimeoutExpired:
            logger.warning(f"flake8 analysis timed out for {file_path}")
            return {"error": "Analysis timed out", "timeout": True}
        except Exception as e:
            logger.error(f"flake8 analysis failed for {file_path}: {e}")
            return {"error": str(e)}

    def _run_pylint(self, file_path: str) -> Dict[str, Any]:
        """Run pylint analysis on a Python file.
        
        Args:
            file_path: Path to the Python file to analyze.
            
        Returns:
            Dictionary containing pylint analysis results.
        """
        try:
            # Run pylint with JSON output
            result = subprocess.run(
                [
                    "pylint",
                    "--output-format=json",
                    "--disable=C0114,C0115,C0116",  # Disable missing docstring warnings
                    "--max-line-length=88",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            pylint_result: Dict[str, Any] = {
                "return_code": result.returncode,
                "score": 0.0,
                "issues": [],
                "summary": {
                    "convention": 0,
                    "refactor": 0,
                    "warning": 0,
                    "error": 0,
                    "fatal": 0,
                },
            }
            
            # Ensure list and dict fields are properly typed
            issues_list = _ensure_list_field(pylint_result, "issues")
            summary_dict = _ensure_dict_field(pylint_result, "summary")

            # Parse JSON output
            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                    # Clear and repopulate the issues list
                    issues_list.clear()
                    issues_list.extend(issues)

                    # Categorize issues
                    for issue in issues:
                        issue_type = issue.get("type", "unknown")
                        if issue_type in summary_dict and isinstance(summary_dict[issue_type], int):
                            summary_dict[issue_type] += 1

                except json.JSONDecodeError:
                    # Fallback to text parsing if JSON fails
                    lines = result.stdout.split("\\n")
                    for line in lines:
                        if "Your code has been rated at" in line:
                            try:
                                score_part = line.split("rated at ")[1].split("/")[0]
                                pylint_result["score"] = float(score_part)
                            except (IndexError, ValueError):
                                pass

            # Extract score from stderr if not found in stdout
            if pylint_result["score"] == 0.0 and result.stderr:
                lines = result.stderr.split("\\n")
                for line in lines:
                    if "Your code has been rated at" in line:
                        try:
                            score_part = line.split("rated at ")[1].split("/")[0]
                            pylint_result["score"] = float(score_part)
                        except (IndexError, ValueError):
                            pass

            return pylint_result

        except subprocess.TimeoutExpired:
            logger.warning(f"pylint analysis timed out for {file_path}")
            return {"error": "Analysis timed out", "timeout": True}
        except Exception as e:
            logger.error(f"pylint analysis failed for {file_path}: {e}")
            return {"error": str(e)}

    def _run_mypy(self, file_path: str) -> Dict[str, Any]:
        """Run mypy analysis on a Python file.
        
        Args:
            file_path: Path to the Python file to analyze.
            
        Returns:
            Dictionary containing mypy analysis results.
        """
        try:
            result = subprocess.run(
                ["mypy", "--ignore-missing-imports", "--no-error-summary", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            mypy_result: Dict[str, Any] = {
                "return_code": result.returncode,
                "issues": [],
                "summary": {"errors": 0, "notes": 0, "total_issues": 0},
            }
            
            # Ensure list and dict fields are properly typed
            issues_list = _ensure_list_field(mypy_result, "issues")
            summary_dict = _ensure_dict_field(mypy_result, "summary")

            if result.stdout:
                lines = result.stdout.strip().split("\\n")
                for line in lines:
                    if ":" in line and file_path in line:
                        parts = line.split(": ", 2)
                        if len(parts) >= 3:
                            location, severity, message = parts
                            location_parts = location.split(":")
                            _safe_append(issues_list, {
                                "line": int(location_parts[-1])
                                if location_parts[-1].isdigit()
                                else 0,
                                "severity": severity.strip(),
                                "message": message.strip(),
                            })

                            severity_clean = severity.strip().lower()
                            if severity_clean == "error" and "errors" in summary_dict:
                                summary_dict["errors"] += 1
                            elif "notes" in summary_dict:
                                summary_dict["notes"] += 1

                if "total_issues" in summary_dict:
                    summary_dict["total_issues"] = _safe_len(mypy_result.get("issues", []))

            return mypy_result

        except subprocess.TimeoutExpired:
            logger.warning(f"mypy analysis timed out for {file_path}")
            return {"error": "Analysis timed out", "timeout": True}
        except Exception as e:
            logger.error(f"mypy analysis failed for {file_path}: {e}")
            return {"error": str(e)}

    def _analyze_ast(self, source_code: str) -> Dict[str, Any]:
        """Analyze Python code using AST (Abstract Syntax Tree).
        
        Args:
            source_code: Python source code to analyze.
            
        Returns:
            Dictionary containing AST analysis results.
        """
        try:
            tree = ast.parse(source_code)

            ast_result: Dict[str, Any] = {
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity_metrics": {
                    "cyclomatic_complexity": 0,
                    "total_functions": 0,
                    "total_classes": 0,
                    "total_lines": len(source_code.split("\\n")),
                    "total_imports": 0,
                },
                "code_quality": {
                    "has_main_guard": False,
                    "has_docstrings": False,
                    "function_docstring_coverage": 0.0,
                    "class_docstring_coverage": 0.0,
                },
            }
            
            # Ensure list and dict fields are properly typed
            functions_list = _ensure_list_field(ast_result, "functions")
            classes_list = _ensure_list_field(ast_result, "classes")
            imports_list = _ensure_list_field(ast_result, "imports")
            complexity_dict = _ensure_dict_field(ast_result, "complexity_metrics")
            quality_dict = _ensure_dict_field(ast_result, "code_quality")

            # Walk through AST nodes
            for node in ast.walk(tree):
                # Analyze functions
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args_count": len(node.args.args),
                        "has_docstring": ast.get_docstring(node) is not None,
                        "is_private": node.name.startswith("_"),
                        "complexity": self._calculate_function_complexity(node),
                    }
                    _safe_append(functions_list, func_info)
                    if "total_functions" in complexity_dict:
                        complexity_dict["total_functions"] += 1
                    if "cyclomatic_complexity" in complexity_dict:
                        complexity_dict["cyclomatic_complexity"] += func_info["complexity"]

                    if func_info["has_docstring"] and "has_docstrings" in quality_dict:
                        quality_dict["has_docstrings"] = True

                # Analyze classes
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "methods_count": len(
                            [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        ),
                        "has_docstring": ast.get_docstring(node) is not None,
                        "is_private": node.name.startswith("_"),
                    }
                    _safe_append(classes_list, class_info)
                    if "total_classes" in complexity_dict:
                        complexity_dict["total_classes"] += 1

                    if class_info["has_docstring"] and "has_docstrings" in quality_dict:
                        quality_dict["has_docstrings"] = True

                # Analyze imports
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            _safe_append(imports_list, {
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            })
                    else:  # ast.ImportFrom
                        for alias in node.names:
                            _safe_append(imports_list, {
                                "type": "from_import",
                                "module": node.module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            })

                    if "total_imports" in complexity_dict:
                        complexity_dict["total_imports"] += 1

                # Check for main guard
                elif isinstance(node, ast.If):
                    if (
                        isinstance(node.test, ast.Compare)
                        and isinstance(node.test.left, ast.Name)
                        and node.test.left.id == "__name__"
                        and any(isinstance(comp, ast.Eq) for comp in node.test.ops)
                        and any(
                            isinstance(comp, ast.Str) and comp.s == "__main__"
                            for comp in node.test.comparators
                        )
                    ):
                        if "has_main_guard" in quality_dict:
                            quality_dict["has_main_guard"] = True

            # Calculate docstring coverage
            total_functions = complexity_dict.get("total_functions", 0)
            if total_functions > 0:
                documented_functions = sum(
                    1 for f in functions_list if f.get("has_docstring", False)
                )
                if "function_docstring_coverage" in quality_dict:
                    quality_dict["function_docstring_coverage"] = documented_functions / total_functions

            total_classes = complexity_dict.get("total_classes", 0)
            if total_classes > 0:
                documented_classes = sum(
                    1 for c in classes_list if c.get("has_docstring", False)
                )
                if "class_docstring_coverage" in quality_dict:
                    quality_dict["class_docstring_coverage"] = documented_classes / total_classes

            return ast_result

        except SyntaxError as e:
            logger.warning(f"Syntax error in code: {e}")
            return {"error": f"Syntax error: {e}", "syntax_error": True}
        except Exception as e:
            logger.error(f"AST analysis failed: {e}")
            return {"error": str(e)}

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function.
        
        Args:
            func_node: AST function definition node.
            
        Returns:
            Cyclomatic complexity score.
        """
        complexity: int = 1  # Base complexity

        for node in ast.walk(func_node):
            # Control flow statements that increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With, ast.ExceptHandler, ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _generate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of all analysis results.
        
        Args:
            analysis_results: Complete analysis results from all tools.
            
        Returns:
            Dictionary containing analysis summary.
        """
        summary: Dict[str, Any] = {
            "overall_quality": "unknown",
            "total_issues": 0,
            "critical_issues": 0,
            "code_style_score": 0.0,
            "complexity_assessment": "unknown",
            "recommendations": [],
        }
        
        # Ensure list fields are properly typed
        recommendations_list = _ensure_list_field(summary, "recommendations")

        # Aggregate issue counts
        if "flake8_analysis" in analysis_results:
            flake8: Dict[str, Any] = analysis_results["flake8_analysis"]
            if "summary" in flake8:
                summary["total_issues"] += flake8["summary"].get("total_issues", 0)
                summary["critical_issues"] += flake8["summary"].get("errors", 0)

        if "pylint_analysis" in analysis_results:
            pylint: Dict[str, Any] = analysis_results["pylint_analysis"]
            if "summary" in pylint:
                summary["total_issues"] += pylint["summary"].get("error", 0)
                summary["total_issues"] += pylint["summary"].get("warning", 0)
                summary["critical_issues"] += pylint["summary"].get("error", 0)

            # Use pylint score as base code style score
            if "score" in pylint and pylint["score"] > 0:
                summary["code_style_score"] = pylint["score"]

        if "mypy_analysis" in analysis_results:
            mypy: Dict[str, Any] = analysis_results["mypy_analysis"]
            if "summary" in mypy:
                summary["total_issues"] += mypy["summary"].get("total_issues", 0)
                summary["critical_issues"] += mypy["summary"].get("errors", 0)

        # Assess complexity
        if "ast_analysis" in analysis_results:
            ast_data: Dict[str, Any] = analysis_results["ast_analysis"]
            if "complexity_metrics" in ast_data and isinstance(ast_data["complexity_metrics"], dict):
                metrics: Dict[str, Any] = ast_data["complexity_metrics"]
                total_functions: int = metrics.get("total_functions", 0)
                total_complexity: int = metrics.get("cyclomatic_complexity", 0)

                if total_functions > 0:
                    avg_complexity: float = total_complexity / total_functions
                    if avg_complexity <= 3:
                        summary["complexity_assessment"] = "low"
                    elif avg_complexity <= 7:
                        summary["complexity_assessment"] = "moderate"
                    else:
                        summary["complexity_assessment"] = "high"

        # Generate overall quality assessment
        if summary["critical_issues"] == 0 and summary["total_issues"] <= 2:
            summary["overall_quality"] = "excellent"
        elif summary["critical_issues"] <= 1 and summary["total_issues"] <= 5:
            summary["overall_quality"] = "good"
        elif summary["critical_issues"] <= 3 and summary["total_issues"] <= 10:
            summary["overall_quality"] = "fair"
        else:
            summary["overall_quality"] = "needs_improvement"

        # Generate recommendations
        if summary["critical_issues"] > 0:
            _safe_append(recommendations_list, "Fix critical errors and syntax issues")

        if summary["code_style_score"] < 7.0:
            _safe_append(recommendations_list, "Improve code style and PEP 8 compliance")

        if summary["complexity_assessment"] == "high":
            _safe_append(recommendations_list, "Consider refactoring complex functions")

        if "ast_analysis" in analysis_results:
            ast_data = analysis_results["ast_analysis"]
            quality: Dict[str, Any] = ast_data.get("code_quality", {})
            if not quality.get("has_main_guard", False):
                _safe_append(recommendations_list, 'Add main guard (__name__ == "__main__")')

            if quality.get("function_docstring_coverage", 0) < 0.5:
                _safe_append(recommendations_list, "Add docstrings to functions")

        return summary


