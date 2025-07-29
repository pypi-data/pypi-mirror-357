"""
Code extractor for Python files with comprehensive static analysis.

This module handles extraction and analysis of Python source code files,
providing detailed code quality assessment, structure analysis, and
best practices evaluation.
"""

from __future__ import annotations

import ast
import logging
import os
from typing import Any, Optional

from .base_extractor import BaseExtractor
from .models import ExtractionResult

# Enhanced encoding support
try:
    from mark_mate.utils.encoding_utils import create_encoding_error_message, safe_read_text_file
    encoding_utils_available = True
except ImportError:
    create_encoding_error_message = None  # type: ignore[assignment]
    safe_read_text_file = None  # type: ignore[assignment]
    encoding_utils_available = False

# Static analysis imports
try:
    from mark_mate.analyzers.static_analysis import StaticAnalyzer
    static_analysis_available = True
except ImportError:
    StaticAnalyzer = None  # type: ignore[misc,assignment]
    static_analysis_available = False

logger = logging.getLogger(__name__)


class CodeExtractor(BaseExtractor):
    """Extractor for Python source code with static analysis."""

    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.extractor_name: str = "code_extractor"
        self.supported_extensions: list[str] = [".py"]

        # Initialize static analyzer if available
        self.static_analyzer: Optional[Any] = None
        self.static_analysis_available: bool = static_analysis_available
        if self.static_analysis_available:
            try:
                if StaticAnalyzer is not None:
                    self.static_analyzer = StaticAnalyzer(config)
                logger.info("Static analyzer initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize static analyzer: {e}")
                self.static_analysis_available = False

    def can_extract(self, file_path: str) -> bool:
        """Check if this extractor can handle the given file.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            True if this is a Python file, False otherwise.
        """
        ext: str = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions

    def extract_content(self, file_path: str) -> ExtractionResult:
        """Extract content and perform static analysis on Python files.
        
        Args:
            file_path: Path to the Python file to extract.
            
        Returns:
            Dictionary containing extracted content and analysis results.
        """
        if not self.can_extract(file_path):
            return self.create_error_result(file_path, ValueError("Not a Python file"))

        try:
            # Read source code with enhanced encoding support
            if encoding_utils_available:
                source_code, encoding_used, error_msg = safe_read_text_file(
                    file_path, "python"
                )

                if source_code is None:
                    logger.error(f"Could not read Python file {file_path}: {error_msg}")
                    if create_encoding_error_message is not None:
                        error_message = create_encoding_error_message(file_path, "Python code")
                    else:
                        error_message = f"Could not read file {file_path}"
                    return self.create_error_result(
                        file_path,
                        ValueError(error_message),
                    )

                logger.info(
                    f"Successfully read Python file using {encoding_used}: {os.path.basename(file_path)}"
                )
            else:
                # Fallback to basic UTF-8
                with open(file_path, encoding="utf-8") as f:
                    source_code = f.read()

            if not source_code.strip():
                logger.warning(f"Empty Python file: {file_path}")
                return self.create_success_result(
                    file_path,
                    "[EMPTY FILE] Python file contains no code",
                    {"analysis_type": "empty_file"},
                )

            # Basic code structure analysis
            basic_analysis: dict[str, Any] = self._analyze_basic_structure(source_code, file_path)

            # Full static analysis if available
            static_analysis: dict[str, Any] = {}
            if self.static_analyzer and self.static_analysis_available:
                try:
                    static_analysis = self.static_analyzer.analyze_python_file(
                        file_path
                    )
                    logger.info(
                        f"Static analysis completed for {os.path.basename(file_path)}"
                    )
                except Exception as e:
                    logger.warning(f"Static analysis failed for {file_path}: {e}")
                    static_analysis = {"error": str(e)}
            else:
                static_analysis = {"warning": "Static analysis tools not available"}

            # Create comprehensive content text
            content_text: str = self._create_content_text(
                source_code, basic_analysis, static_analysis
            )

            # Combine all analysis results
            comprehensive_analysis: dict[str, Any] = {
                "basic_structure": basic_analysis,
                "static_analysis": static_analysis,
                "content_metrics": {
                    "source_lines": len(source_code.split("\\n")),
                    "source_size": len(source_code),
                    "non_empty_lines": len(
                        [line for line in source_code.split("\\n") if line.strip()]
                    ),
                    "comment_lines": len(
                        [
                            line
                            for line in source_code.split("\\n")
                            if line.strip().startswith("#")
                        ]
                    ),
                },
            }

            return self.create_success_result(
                file_path, content_text, comprehensive_analysis
            )

        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {file_path}: {e}")
            return self.create_error_result(file_path, e)
        except Exception as e:
            logger.error(f"Error extracting Python code from {file_path}: {e}")
            return self.create_error_result(file_path, e)

    def _analyze_basic_structure(
        self, source_code: str, file_path: str
    ) -> dict[str, Any]:
        """Perform basic structure analysis without external tools.
        
        Args:
            source_code: Python source code to analyze.
            file_path: Path to the source file.
            
        Returns:
            Dictionary containing basic structure analysis.
        """
        try:
            tree: ast.AST = ast.parse(source_code)

            analysis: dict[str, Any] = {
                "functions": [],
                "classes": [],
                "imports": [],
                "global_variables": [],
                "file_type": "script",  # script, module, test, main
                "structure_quality": {},
            }

            # Analyze top-level nodes
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_info: dict[str, Any] = {
                        "name": node.name,
                        "line": node.lineno,
                        "is_private": node.name.startswith("_"),
                        "args_count": len(node.args.args),
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                    analysis["functions"].append(func_info)

                elif isinstance(node, ast.ClassDef):
                    class_info: dict[str, Any] = {
                        "name": node.name,
                        "line": node.lineno,
                        "is_private": node.name.startswith("_"),
                        "has_docstring": ast.get_docstring(node) is not None,
                        "methods": [],
                    }

                    # Analyze class methods
                    for class_node in node.body:
                        if isinstance(class_node, ast.FunctionDef):
                            class_info["methods"].append(
                                {
                                    "name": class_node.name,
                                    "line": class_node.lineno,
                                    "is_private": class_node.name.startswith("_"),
                                    "is_special": class_node.name.startswith("__")
                                    and class_node.name.endswith("__"),
                                }
                            )

                    analysis["classes"].append(class_info)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(
                                {
                                    "type": "import",
                                    "module": alias.name,
                                    "line": node.lineno,
                                }
                            )
                    else:
                        for alias in node.names:
                            analysis["imports"].append(
                                {
                                    "type": "from_import",
                                    "module": node.module or "",
                                    "name": alias.name,
                                    "line": node.lineno,
                                }
                            )

                elif isinstance(node, ast.Assign):
                    # Simple global variable detection
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis["global_variables"].append(
                                {
                                    "name": target.id,
                                    "line": node.lineno,
                                    "is_constant": target.id.isupper(),
                                }
                            )

            # Determine file type
            filename: str = os.path.basename(file_path).lower()
            if "test" in filename or any(
                f["name"].startswith("test_") for f in analysis["functions"]
            ):
                analysis["file_type"] = "test"
            elif filename == "__main__.py" or any(
                "if __name__" in line for line in source_code.split("\\n")
            ):
                analysis["file_type"] = "main"
            elif analysis["classes"] or analysis["functions"]:
                analysis["file_type"] = "module"

            # Structure quality assessment
            analysis["structure_quality"] = {
                "has_functions": len(analysis["functions"]) > 0,
                "has_classes": len(analysis["classes"]) > 0,
                "has_imports": len(analysis["imports"]) > 0,
                "functions_with_docstrings": sum(
                    1 for f in analysis["functions"] if f["has_docstring"]
                ),
                "classes_with_docstrings": sum(
                    1 for c in analysis["classes"] if c["has_docstring"]
                ),
                "import_organization": self._assess_import_organization(
                    analysis["imports"]
                ),
            }

            return analysis

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return {
                "error": f"Syntax error: {e}",
                "syntax_error": True,
                "line": getattr(e, "lineno", 0),
                "message": str(e),
            }
        except Exception as e:
            logger.error(f"Basic structure analysis failed for {file_path}: {e}")
            return {"error": str(e)}

    def _assess_import_organization(self, imports: list[dict[str, Any]]) -> str:
        """Assess the organization of imports.
        
        Args:
            imports: List of import information dictionaries.
            
        Returns:
            Assessment of import organization quality.
        """
        if not imports:
            return "no_imports"

        # Check if imports are grouped (standard library, third-party, local)
        import_lines: list[int] = [imp["line"] for imp in imports]

        # Simple heuristic: well-organized if imports are at the top and grouped
        if all(line < 20 for line in import_lines):  # Imports within first 20 lines
            return "well_organized"
        elif all(line < 50 for line in import_lines):  # Imports within first 50 lines
            return "acceptable"
        else:
            return "scattered"

    def _create_content_text(
        self,
        source_code: str,
        basic_analysis: dict[str, Any],
        static_analysis: dict[str, Any],
    ) -> str:
        """Create comprehensive text content for the Python file.
        
        Args:
            source_code: Python source code.
            basic_analysis: Basic structure analysis results.
            static_analysis: Static analysis results.
            
        Returns:
            Formatted content text for the Python file.
        """
        content_parts: list[str] = []

        # Header with file analysis
        content_parts.append("PYTHON CODE ANALYSIS")
        content_parts.append("=" * 50)

        # Basic file information
        if "error" not in basic_analysis:
            content_parts.append(
                f"File Type: {basic_analysis.get('file_type', 'unknown')}"
            )
            content_parts.append(
                f"Functions: {len(basic_analysis.get('functions', []))}"
            )
            content_parts.append(f"Classes: {len(basic_analysis.get('classes', []))}")
            content_parts.append(f"Imports: {len(basic_analysis.get('imports', []))}")
            content_parts.append("")

            # Function details
            if basic_analysis.get("functions"):
                content_parts.append("FUNCTIONS:")
                for func in basic_analysis["functions"]:
                    func_doc_status: str = (
                        "✓ documented" if func["has_docstring"] else "✗ no docstring"
                    )
                    visibility: str = "private" if func["is_private"] else "public"
                    content_parts.append(
                        f"  - {func['name']} (line {func['line']}, {visibility}, {func_doc_status})"
                    )
                content_parts.append("")

            # Class details
            if basic_analysis.get("classes"):
                content_parts.append("CLASSES:")
                for cls in basic_analysis["classes"]:
                    class_doc_status: str = (
                        "✓ documented" if cls["has_docstring"] else "✗ no docstring"
                    )
                    content_parts.append(
                        f"  - {cls['name']} (line {cls['line']}, {class_doc_status})"
                    )
                    if cls.get("methods"):
                        for method in cls["methods"][:5]:  # Show first 5 methods
                            method_type: str = (
                                "special"
                                if method["is_special"]
                                else "private"
                                if method["is_private"]
                                else "public"
                            )
                            content_parts.append(
                                f"    * {method['name']} ({method_type})"
                            )
                content_parts.append("")

            # Import analysis
            if basic_analysis.get("imports"):
                content_parts.append("IMPORTS:")
                for imp in basic_analysis["imports"][:10]:  # Show first 10 imports
                    if imp["type"] == "import":
                        content_parts.append(f"  - import {imp['module']}")
                    else:
                        content_parts.append(
                            f"  - from {imp['module']} import {imp['name']}"
                        )
                content_parts.append("")

        # Static analysis summary
        if static_analysis and "error" not in static_analysis:
            content_parts.append("CODE QUALITY ANALYSIS:")

            if "summary" in static_analysis:
                summary: dict[str, Any] = static_analysis["summary"]
                content_parts.append(
                    f"Overall Quality: {summary.get('overall_quality', 'unknown')}"
                )
                content_parts.append(f"Total Issues: {summary.get('total_issues', 0)}")
                content_parts.append(
                    f"Critical Issues: {summary.get('critical_issues', 0)}"
                )
                content_parts.append(
                    f"Code Style Score: {summary.get('code_style_score', 0):.1f}/10"
                )
                content_parts.append(
                    f"Complexity: {summary.get('complexity_assessment', 'unknown')}"
                )

                if summary.get("recommendations"):
                    content_parts.append("\\nRecommendations:")
                    for rec in summary["recommendations"]:
                        content_parts.append(f"  • {rec}")
                content_parts.append("")

            # Tool-specific results
            if "flake8_analysis" in static_analysis:
                flake8: dict[str, Any] = static_analysis["flake8_analysis"]
                if "summary" in flake8:
                    content_parts.append(
                        f"Style Issues (flake8): {flake8['summary'].get('total_issues', 0)}"
                    )

            if "pylint_analysis" in static_analysis:
                pylint: dict[str, Any] = static_analysis["pylint_analysis"]
                if "score" in pylint and pylint["score"] > 0:
                    content_parts.append(f"Pylint Score: {pylint['score']:.1f}/10")

        # Source code section
        content_parts.append("SOURCE CODE:")
        content_parts.append("-" * 30)
        content_parts.append(source_code)

        return "\\n".join(content_parts)

    def analyze_python_project(self, file_paths: list[str]) -> dict[str, Any]:
        """Analyze multiple Python files as a project.
        
        Args:
            file_paths: List of Python file paths to analyze.
            
        Returns:
            Dictionary containing project-wide analysis results.
        """
        project_analysis: dict[str, Any] = {
            "total_files": len(file_paths),
            "files_analyzed": [],
            "project_structure": {
                "total_functions": 0,
                "total_classes": 0,
                "total_lines": 0,
                "has_tests": False,
                "has_main": False,
                "has_init": False,
            },
            "quality_summary": {
                "average_quality": "unknown",
                "total_issues": 0,
                "files_with_issues": 0,
            },
        }

        for file_path in file_paths:
            if self.can_extract(file_path):
                try:
                    result: ExtractionResult = self.extract_content(file_path)
                    if result.success:
                        project_analysis["files_analyzed"].append(
                            {
                                "file": os.path.basename(file_path),
                                "analysis": result.analysis,
                            }
                        )

                        # Aggregate project metrics
                        if "basic_structure" in result.analysis:
                            basic: dict[str, Any] = result.analysis["basic_structure"]
                            project_analysis["project_structure"][
                                "total_functions"
                            ] += len(basic.get("functions", []))
                            project_analysis["project_structure"]["total_classes"] += (
                                len(basic.get("classes", []))
                            )

                        if "content_metrics" in result.analysis:
                            metrics: dict[str, Any] = result.analysis["content_metrics"]
                            project_analysis["project_structure"]["total_lines"] += (
                                metrics.get("source_lines", 0)
                            )

                        # Check file types
                        filename: str = os.path.basename(file_path).lower()
                        if "test" in filename:
                            project_analysis["project_structure"]["has_tests"] = True
                        elif filename == "__main__.py":
                            project_analysis["project_structure"]["has_main"] = True
                        elif filename == "__init__.py":
                            project_analysis["project_structure"]["has_init"] = True

                except Exception as e:
                    logger.error(f"Error analyzing {file_path} in project context: {e}")

        return project_analysis
