"""Enhanced file type detection for the content extraction system.

This module provides intelligent file type detection and content type
classification for automatic processing decisions.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class FileTypeDetector:
    """Intelligent file type detector for content extraction."""

    def __init__(self) -> None:
        """Initialize the file type detector with predefined file patterns."""
        # File type mappings
        self.document_extensions: set[str] = {".pdf", ".docx", ".doc", ".txt", ".md", ".markdown"}
        self.office_extensions: set[str] = {".pptx", ".xlsx", ".xls", ".csv", ".tsv"}
        self.notebook_extensions: set[str] = {".ipynb"}
        self.code_extensions: set[str] = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css"}
        self.archive_extensions: set[str] = {".zip", ".tar", ".gz", ".rar", ".7z"}
        self.image_extensions: set[str] = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".svg",
            ".webp",
        }

        # WordPress-specific patterns
        self.wordpress_patterns: list[str] = [
            "-uploads.zip",
            "-others.zip",
            "-db.gz",
            "-db.zip",
            "-plugins.zip",
            "-themes.zip",
            "-mu-plugins.zip",
        ]

        # Project type indicators
        self.project_indicators: dict[str, set[str]] = {
            "web_project": {
                "package.json",
                "index.html",
                "webpack.config.js",
                "vite.config.js",
            },
            "python_project": {
                "requirements.txt",
                "setup.py",
                "pyproject.toml",
                "__init__.py",
            },
            "react_project": {"package.json", "src/", "public/", "tsx", "jsx"},
            "data_science": {".ipynb", ".csv", ".xlsx", "data/", "datasets/"},
            "wordpress_backup": {"wordpress_backup/", "-db.gz", "-plugins.zip"},
        }

    def detect_file_type(self, file_path: str) -> dict[str, Any]:
        """Detect the type and characteristics of a file.

        Args:
            file_path: Path to the file.

        Returns:
            Dictionary containing file type information.
        """
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        result: dict[str, Any] = {
            "filename": filename,
            "extension": ext,
            "file_path": file_path,
            "size": self._get_file_size(file_path),
            "categories": [],
            "extractors": [],
            "priority": "medium",
        }

        # Categorize file
        if ext in self.document_extensions:
            result["categories"].append("document")
            result["extractors"].append("document_extractor")

        if ext in self.office_extensions:
            result["categories"].append("office_document")
            result["extractors"].append("office_extractor")
            result["priority"] = "high"  # Office docs often contain key deliverables

        if ext in self.notebook_extensions:
            result["categories"].append("jupyter_notebook")
            result["extractors"].append("notebook_extractor")
            result["priority"] = "high"  # Notebooks are primary deliverables

        if ext in self.code_extensions:
            result["categories"].append("source_code")
            result["extractors"].append("code_extractor")

        if self._is_wordpress_file(filename):
            result["categories"].append("wordpress_backup")
            result["extractors"].append("wordpress_extractor")
            result["priority"] = "high"

        if ext in self.archive_extensions:
            result["categories"].append("archive")

        if ext in self.image_extensions:
            result["categories"].append("image")
            result["priority"] = "low"  # Images usually not processed for text

        # Default to unknown if no categories found
        if not result["categories"]:
            result["categories"].append("unknown")
            result["extractors"].append("basic_extractor")

        return result

    def detect_submission_type(self, file_list: list[str]) -> dict[str, Any]:
        """Analyze a list of files to determine submission type and processing strategy.

        Args:
            file_list: List of file paths.

        Returns:
            Dictionary containing submission analysis and processing recommendations.
        """
        file_types = [self.detect_file_type(f) for f in file_list]

        # Count file categories
        category_counts: dict[str, int] = {}
        for file_info in file_types:
            for category in file_info["categories"]:
                category_counts[category] = category_counts.get(category, 0) + 1

        # Detect project types
        detected_projects = self._detect_project_types(file_list)

        # Determine primary submission type
        primary_type = self._determine_primary_type(category_counts, detected_projects)

        # Get processing recommendations
        processing_strategy = self._get_processing_strategy(
            primary_type, category_counts
        )

        return {
            "total_files": len(file_list),
            "file_categories": category_counts,
            "detected_projects": detected_projects,
            "primary_type": primary_type,
            "processing_strategy": processing_strategy,
            "high_priority_files": [f for f in file_types if f["priority"] == "high"],
            "recommended_extractors": list(
                {ext for f in file_types for ext in f["extractors"]}
            ),
        }

    def _get_file_size(self, file_path: str) -> int:
        """Get file size safely.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            File size in bytes, or 0 if file cannot be accessed.
        """
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0

    def _is_wordpress_file(self, filename: str) -> bool:
        """Check if filename matches WordPress backup patterns.
        
        Args:
            filename: Name of the file to check.
            
        Returns:
            True if filename matches WordPress backup patterns.
        """
        filename_lower = filename.lower()
        return any(
            filename_lower.endswith(pattern) for pattern in self.wordpress_patterns
        )

    def _detect_project_types(self, file_list: list[str]) -> list[str]:
        """Detect project types based on file patterns.
        
        Args:
            file_list: List of file paths to analyze.
            
        Returns:
            List of detected project types.
        """
        detected: list[str] = []

        # Convert to set of basenames and paths for efficient lookup
        basenames = {os.path.basename(f).lower() for f in file_list}
        paths = {f.lower() for f in file_list}

        for project_type, indicators in self.project_indicators.items():
            matches = 0
            for indicator in indicators:
                if indicator.endswith("/"):
                    # Directory indicator
                    if any(indicator in path for path in paths):
                        matches += 1
                elif "." in indicator and not indicator.startswith("."):
                    # Extension indicator
                    if any(f.endswith(indicator) for f in file_list):
                        matches += 1
                else:
                    # Filename indicator
                    if indicator in basenames:
                        matches += 1

            # If we find at least 2 indicators, consider it a match
            if matches >= 2:
                detected.append(project_type)

        return detected

    def _determine_primary_type(
        self, category_counts: dict[str, int], detected_projects: list[str]
    ) -> str:
        """Determine the primary submission type.
        
        Args:
            category_counts: Count of files by category.
            detected_projects: List of detected project types.
            
        Returns:
            Primary submission type.
        """
        # Project types take precedence
        if detected_projects:
            return detected_projects[0]  # Return first detected project type

        # Otherwise, use file category with highest count
        if not category_counts:
            return "unknown"

        # Prioritize certain categories
        priority_order = [
            "jupyter_notebook",
            "wordpress_backup",
            "office_document",
            "source_code",
            "document",
            "archive",
        ]

        for category in priority_order:
            if category in category_counts and category_counts[category] > 0:
                return category

        # Return most common category
        return max(category_counts.items(), key=lambda x: x[1])[0]

    def _get_processing_strategy(
        self, primary_type: str, _category_counts: dict[str, int]
    ) -> dict[str, Any]:
        """Get recommended processing strategy based on submission type.
        
        Args:
            primary_type: Primary submission type.
            category_counts: Count of files by category.
            
        Returns:
            Dictionary containing processing strategy recommendations.
        """
        strategies = {
            "jupyter_notebook": {
                "analysis_depth": "comprehensive",
                "focus_areas": ["code_quality", "output_analysis", "documentation"],
                "recommended_tools": ["nbconvert", "static_analysis"],
            },
            "wordpress_backup": {
                "analysis_depth": "comprehensive",
                "focus_areas": [
                    "content_analysis",
                    "plugin_analysis",
                    "security_review",
                ],
                "recommended_tools": ["wordpress_analyzer", "database_parser"],
            },
            "office_document": {
                "analysis_depth": "standard",
                "focus_areas": ["content_extraction", "structure_analysis"],
                "recommended_tools": ["office_analyzers", "data_profiling"],
            },
            "web_project": {
                "analysis_depth": "comprehensive",
                "focus_areas": ["html_validation", "css_analysis", "js_quality"],
                "recommended_tools": ["w3c_validator", "eslint"],
            },
            "python_project": {
                "analysis_depth": "comprehensive",
                "focus_areas": ["code_quality", "structure_analysis", "documentation"],
                "recommended_tools": ["flake8", "pylint", "mypy"],
            },
            "document": {
                "analysis_depth": "standard",
                "focus_areas": ["content_extraction", "structure_analysis"],
                "recommended_tools": ["document_processors"],
            },
        }

        return strategies.get(
            primary_type,
            {
                "analysis_depth": "minimal",
                "focus_areas": ["basic_extraction"],
                "recommended_tools": ["basic_extractor"],
            },
        )

    def analyze_submission_structure(self, submission_path: str) -> dict[str, Any]:
        """Analyze the structure of a submission directory or file.
        
        Args:
            submission_path: Path to the submission.
            
        Returns:
            Dictionary containing structure analysis.
        """
        analysis: dict[str, Any] = {
            "path": submission_path,
            "is_file": os.path.isfile(submission_path),
            "is_directory": os.path.isdir(submission_path),
            "file_count": 0,
            "directory_count": 0,
            "file_types": {},
            "total_size": 0,
            "structure": [],
        }

        if os.path.isfile(submission_path):
            # Single file
            analysis["file_count"] = 1
            analysis["total_size"] = self._get_file_size(submission_path)
            file_ext = os.path.splitext(submission_path)[1].lower()
            analysis["file_types"][file_ext] = 1
            analysis["structure"] = [os.path.basename(submission_path)]

        elif os.path.isdir(submission_path):
            # Directory
            for root, dirs, files in os.walk(submission_path):
                analysis["directory_count"] += len(dirs)
                analysis["file_count"] += len(files)

                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        analysis["total_size"] += self._get_file_size(file_path)
                    except OSError:
                        pass  # Skip files we can't read

                    file_ext = os.path.splitext(file)[1].lower()
                    analysis["file_types"][file_ext] = (
                        analysis["file_types"].get(file_ext, 0) + 1
                    )

                # Build structure representation
                rel_root = os.path.relpath(root, submission_path)
                level = "" if rel_root == "." else "  " * (rel_root.count(os.sep) + 1)

                for dir_name in dirs:
                    analysis["structure"].append(f"{level}{dir_name}/")

                for file_name in files:
                    analysis["structure"].append(f"{level}{file_name}")

        return analysis


# Create global detector instance
_detector = FileTypeDetector()


# Wrapper functions for easier import
def detect_file_type(file_path: str) -> str:
    """Simple wrapper to detect file type and return the primary category.

    Args:
        file_path: Path to the file.

    Returns:
        String representing the primary file type.
    """
    result = _detector.detect_file_type(file_path)
    if result["categories"]:
        return result["categories"][0]
    return "unknown"


def analyze_submission_structure(submission_path: str) -> dict[str, Any]:
    """Wrapper for analyzing submission structure.

    Args:
        submission_path: Path to the submission.

    Returns:
        Dictionary containing submission analysis.
    """
    return _detector.analyze_submission_structure(submission_path)
