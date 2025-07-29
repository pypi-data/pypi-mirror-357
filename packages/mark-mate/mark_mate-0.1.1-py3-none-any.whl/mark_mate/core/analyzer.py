"""
MarkMate Core Analyzer

Provides content analysis capabilities and utilities.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Content analysis utilities for MarkMate."""

    def __init__(self) -> None:
        """Initialize the content analyzer."""
        pass

    def analyze_submission_structure(self, submission_path: str) -> dict[str, Any]:
        """Analyze the structure of a submission.

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
            analysis["total_size"] = os.path.getsize(submission_path)
            file_ext = Path(submission_path).suffix.lower()
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
                        analysis["total_size"] += os.path.getsize(file_path)
                    except OSError:
                        pass  # Skip files we can't read

                    file_ext = Path(file).suffix.lower()
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

    def detect_assignment_type(self, content: dict[str, Any]) -> str:
        """Detect the type of assignment based on content.

        Args:
            content: Extracted content dictionary.

        Returns:
            Detected assignment type.
        """
        # Check for WordPress indicators
        if any(key.startswith("wordpress_") for key in content):
            return "wordpress"

        # Check for GitHub repository
        if "github_analysis" in content:
            return "programming_with_git"

        # Check for code files
        code_extensions: set[str] = {
            ".py",
            ".js",
            ".html",
            ".css",
            ".tsx",
            ".ts",
            ".jsx",
            ".json",
        }
        if "code" in content or any(
            any(file_item.get("filename", "").endswith(ext) for ext in code_extensions)
            for file_list in content.values()
            if isinstance(file_list, list)
            for file_item in file_list
        ):
            return "programming"

        # Check for web files
        web_extensions: set[str] = {".html", ".css", ".js"}
        if "web" in content or any(
            any(file_item.get("filename", "").endswith(ext) for ext in web_extensions)
            for file_list in content.values()
            if isinstance(file_list, list)
            for file_item in file_list
        ):
            return "web_development"

        # Check for documents
        if "documents" in content or any(
            key in ["pdf", "docx", "txt", "md"] for key in content
        ):
            return "document"

        return "unknown"

    def analyze_code_quality(
        self, code_content: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze code quality metrics.

        Args:
            code_content: List of code files with their content.

        Returns:
            Code quality analysis.
        """
        analysis: dict[str, Any] = {
            "total_files": len(code_content),
            "total_lines": 0,
            "languages": set(),
            "complexity_indicators": {
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "comments": 0,
            },
            "issues": [],
        }

        for code_file in code_content:
            content = code_file.get("content", "")
            filename = code_file.get("filename", "")

            lines = content.split("\n")
            analysis["total_lines"] += len(lines)

            # Detect language from extension
            ext = Path(filename).suffix.lower()
            if ext in [".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css"]:
                analysis["languages"].add(ext[1:])  # Remove dot

            # Simple complexity analysis
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith("def ") or line_stripped.startswith(
                    "function "
                ):
                    analysis["complexity_indicators"]["functions"] += 1
                elif line_stripped.startswith("class "):
                    analysis["complexity_indicators"]["classes"] += 1
                elif line_stripped.startswith("import ") or line_stripped.startswith(
                    "from "
                ):
                    analysis["complexity_indicators"]["imports"] += 1
                elif line_stripped.startswith("#") or line_stripped.startswith("//"):
                    analysis["complexity_indicators"]["comments"] += 1

        # Convert set to list for JSON serialization
        analysis["languages"] = list(analysis["languages"])

        # Calculate quality score
        if analysis["total_lines"] > 0:
            comment_ratio = (
                analysis["complexity_indicators"]["comments"] / analysis["total_lines"]
            )
            analysis["comment_ratio"] = round(comment_ratio, 3)

            if comment_ratio < 0.1:
                analysis["issues"].append(
                    "Low comment density - code may lack documentation"
                )

            if (
                analysis["complexity_indicators"]["functions"] == 0
                and analysis["total_lines"] > 20
            ):
                analysis["issues"].append(
                    "No functions detected - code may lack modularity"
                )

        return analysis

    def analyze_github_patterns(
        self, github_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze GitHub development patterns.

        Args:
            github_analysis: GitHub analysis data.

        Returns:
            Development pattern analysis.
        """
        patterns: dict[str, Any] = {
            "development_style": "unknown",
            "consistency": "unknown",
            "collaboration": "unknown",
            "quality_indicators": [],
            "concerns": [],
        }

        commits: int = github_analysis.get("total_commits", 0)
        span_days: int = github_analysis.get("development_span_days", 0)

        # Analyze development style
        if span_days > 0:
            commits_per_day: float = commits / span_days
            if commits_per_day > 2:
                patterns["development_style"] = "intensive"
            elif commits_per_day > 0.5:
                patterns["development_style"] = "steady"
            else:
                patterns["development_style"] = "sporadic"

        # Analyze consistency
        if span_days > 7:
            if commits > span_days * 0.3:
                patterns["consistency"] = "good"
            elif commits > span_days * 0.1:
                patterns["consistency"] = "moderate"
            else:
                patterns["consistency"] = "poor"
                patterns["concerns"].append("Inconsistent development pattern")

        # Quality indicators
        if github_analysis.get("has_readme", False):
            patterns["quality_indicators"].append("Has README documentation")

        if github_analysis.get("commit_message_quality", {}).get("score", 0) > 70:
            patterns["quality_indicators"].append("Good commit message quality")

        # Concerns
        if commits < 3:
            patterns["concerns"].append(
                "Very few commits - limited development history"
            )

        if span_days < 1:
            patterns["concerns"].append(
                "All commits in single day - possible last-minute work"
            )

        return patterns

    def generate_submission_summary(
        self, content: dict[str, Any], metadata: dict[str, Any]
    ) -> str:
        """Generate a human-readable summary of the submission.

        Args:
            content: Extracted content.
            metadata: Processing metadata.

        Returns:
            Summary string.
        """
        summary_parts: list[str] = []

        # Assignment type
        assignment_type: str = self.detect_assignment_type(content)
        summary_parts.append(
            f"Assignment Type: {assignment_type.replace('_', ' ').title()}"
        )

        # File statistics
        file_types: list[str] = metadata.get("file_types_detected", [])
        if file_types:
            summary_parts.append(f"File Types: {', '.join(file_types)}")

        # Content summary
        if "documents" in content:
            doc_count: int = len(content["documents"])
            summary_parts.append(f"Documents: {doc_count} file(s)")

        if "code" in content:
            code_analysis: dict[str, Any] = self.analyze_code_quality(content["code"])
            summary_parts.append(
                f"Code: {code_analysis['total_files']} file(s), {code_analysis['total_lines']} lines"
            )

        if "github_analysis" in content:
            github: dict[str, Any] = content["github_analysis"]
            commits: int = github.get("total_commits", 0)
            span: int = github.get("development_span_days", 0)
            summary_parts.append(f"GitHub: {commits} commits over {span} days")

        if any(key.startswith("wordpress_") for key in content):
            wp_components: list[str] = [
                key.replace("wordpress_", "")
                for key in content
                if key.startswith("wordpress_")
            ]
            summary_parts.append(f"WordPress: {', '.join(wp_components)} components")

        # Processing info
        extractors: list[str] = metadata.get("extractors_used", [])
        if extractors:
            summary_parts.append(f"Processed with: {', '.join(extractors)}")

        errors: list[str] = metadata.get("errors", [])
        if errors:
            summary_parts.append(f"Processing errors: {len(errors)}")

        return "\n".join(summary_parts)
