"""MarkMate Prompt Manager.

Handles prompt template loading, placeholder substitution, and prompt composition
for flexible and maintainable grading prompts.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """A grading prompt template with system and user components."""

    system: str
    template: str
    name: str = "default"


class PromptManager:
    """Manages prompt templates and placeholder substitution for grading."""

    prompts: dict[str, Any]
    prompt_sections: dict[str, Any]

    def __init__(self, prompt_config: dict[str, Any]) -> None:
        """Initialize prompt manager with configuration.

        Args:
            prompt_config: Dictionary containing prompt and prompt_sections configuration.
        """
        self.prompts = prompt_config.get("prompts", {})
        self.prompt_sections = prompt_config.get("prompt_sections", {})

        # Ensure we have a default prompt
        if "default" not in self.prompts:
            logger.warning("No default prompt found, using built-in fallback")
            self.prompts["default"] = self._get_fallback_prompt()

        # Validate prompt structure
        self._validate_prompts()

    def _get_fallback_prompt(self) -> dict[str, str]:
        """Provide a fallback prompt if none is configured.
        
        Returns:
            Dictionary containing system and template for fallback prompt.
        """
        return {
            "system": "You are an expert academic grader. Provide detailed, fair, and constructive feedback.",
            "template": """ASSIGNMENT SPECIFICATION:
{assignment_spec}

GRADING RUBRIC:
{rubric}

STUDENT SUBMISSION (Student ID: {student_id}):
{content_summary}

GRADING INSTRUCTIONS:
1. Evaluate the submission against each criterion in the rubric
2. Provide a mark out of {max_mark}
3. Give specific feedback on strengths and areas for improvement
4. Consider both technical implementation and documentation quality

{output_format}""",
        }

    def _validate_prompts(self) -> None:
        """Validate prompt structure and required fields.
        
        Raises:
            ValueError: If prompt structure is invalid.
        """
        for prompt_name, prompt_data in self.prompts.items():
            if not isinstance(prompt_data, dict):
                raise ValueError(f"Prompt '{prompt_name}' must be a dictionary")

            if "template" not in prompt_data:
                raise ValueError(
                    f"Prompt '{prompt_name}' missing required 'template' field"
                )

            # System prompt is optional, but log if missing
            if "system" not in prompt_data:
                logger.info(f"Prompt '{prompt_name}' has no system prompt")

    def get_prompt_template(
        self, prompt_name: str = "default", assignment_type: Optional[str] = None
    ) -> PromptTemplate:
        """Get a prompt template by name with assignment type fallback.

        Args:
            prompt_name: Name of the prompt template.
            assignment_type: Type of assignment (wordpress, programming, etc.).

        Returns:
            PromptTemplate object with system and template content.
        """
        # Try assignment type specific prompt first
        if assignment_type and assignment_type in self.prompts:
            prompt_data = self.prompts[assignment_type]
            logger.debug(f"Using {assignment_type}-specific prompt")
        # Fall back to requested prompt name
        elif prompt_name in self.prompts:
            prompt_data = self.prompts[prompt_name]
            logger.debug(f"Using prompt: {prompt_name}")
        # Final fallback to default
        else:
            prompt_data = self.prompts["default"]
            logger.warning(f"Prompt '{prompt_name}' not found, using default")

        return PromptTemplate(
            system=prompt_data.get("system", ""),
            template=prompt_data["template"],
            name=prompt_name,
        )

    def build_grading_prompt(
        self,
        student_data: dict[str, Any],
        assignment_spec: str,
        rubric: str,
        max_mark: int,
        prompt_name: str = "default",
        assignment_type: Optional[str] = None,
    ) -> dict[str, str]:
        """Build a complete grading prompt with placeholder substitution.

        Args:
            student_data: Student submission data.
            assignment_spec: Assignment specification text.
            rubric: Grading rubric text.
            max_mark: Maximum possible mark.
            prompt_name: Name of prompt template to use.
            assignment_type: Type of assignment for prompt selection.

        Returns:
            Dictionary with 'system' and 'user' prompts ready for LLM.
        """
        # Get the appropriate template
        template = self.get_prompt_template(prompt_name, assignment_type)

        # Build context for placeholder substitution
        context = self._build_prompt_context(
            student_data, assignment_spec, rubric, max_mark, assignment_type
        )

        # Substitute placeholders in template
        user_prompt = self._substitute_placeholders(template.template, context)

        return {"system": template.system, "user": user_prompt}

    def _build_prompt_context(
        self,
        student_data: dict[str, Any],
        assignment_spec: str,
        rubric: str,
        max_mark: int,
        assignment_type: Optional[str] = None,
    ) -> dict[str, str]:
        """Build context dictionary for placeholder substitution.
        
        Args:
            student_data: Student submission data.
            assignment_spec: Assignment specification text.
            rubric: Grading rubric text.
            max_mark: Maximum possible mark.
            assignment_type: Type of assignment for prompt selection.
            
        Returns:
            Dictionary of context values for placeholder substitution.
        """

        # Basic context
        context = {
            "assignment_spec": assignment_spec,
            "rubric": rubric,
            "student_id": student_data.get("student_id", "unknown"),
            "max_mark": str(max_mark),
            "assignment_type": assignment_type or "general",
        }

        # Generate content summary
        context["content_summary"] = self._generate_content_summary(
            student_data.get("content", {})
        )

        # Add prompt sections
        context.update(self._get_prompt_sections(assignment_type))

        # Add submission metadata
        context.update(self._get_submission_metadata(student_data))

        return context

    def _substitute_placeholders(self, template: str, context: dict[str, str]) -> str:
        """Safely substitute placeholders in template.

        Args:
            template: Template string with {placeholder} markers.
            context: Dictionary of placeholder values.

        Returns:
            Template with placeholders substituted.
        """
        try:
            # Find all placeholders in template
            placeholders = re.findall(r"\{([^}]+)\}", template)

            # Check for missing placeholders
            missing = [p for p in placeholders if p not in context]
            if missing:
                logger.warning(f"Missing placeholders in template: {missing}")
                # Add empty values for missing placeholders
                for placeholder in missing:
                    context[placeholder] = f"[{placeholder} not available]"

            # Perform substitution
            return template.format(**context)

        except KeyError as e:
            logger.error(f"Placeholder substitution failed: {e}")
            return template
        except Exception as e:
            logger.error(f"Unexpected error in placeholder substitution: {e}")
            return template

    def _generate_content_summary(self, content: dict[str, Any]) -> str:
        """Generate a summary of student submission content.
        
        Args:
            content: Dictionary containing student submission content.
            
        Returns:
            Formatted string summary of submission content.
        """
        summary_parts = []

        # Document content
        if "documents" in content:
            doc_count = len(content["documents"])
            total_chars = sum(len(doc.get("text", "")) for doc in content["documents"])
            summary_parts.append(
                f"DOCUMENTS: {doc_count} files, {total_chars:,} characters total"
            )

            for doc in content["documents"][:3]:  # Show first 3 documents
                filename = doc.get("filename", "Unknown")
                char_count = len(doc.get("text", ""))
                summary_parts.append(f"  - {filename}: {char_count:,} characters")

            if doc_count > 3:
                summary_parts.append(f"  ... and {doc_count - 3} more documents")

        # Code content
        if "code" in content:
            code_count = len(content["code"])
            total_lines = sum(
                len(code.get("content", "").splitlines()) for code in content["code"]
            )
            summary_parts.append(
                f"CODE FILES: {code_count} files, {total_lines:,} lines total"
            )

            for code_file in content["code"][:3]:
                filename = code_file.get("filename", "Unknown")
                line_count = len(code_file.get("content", "").splitlines())
                file_type = code_file.get("language", "unknown")
                summary_parts.append(
                    f"  - {filename} ({file_type}): {line_count:,} lines"
                )

            if code_count > 3:
                summary_parts.append(f"  ... and {code_count - 3} more code files")

        # Web content
        if "web" in content:
            web_count = len(content["web"])
            summary_parts.append(f"WEB FILES: {web_count} files")

            for web_file in content["web"][:3]:
                filename = web_file.get("filename", "Unknown")
                file_type = web_file.get("file_type", "unknown")
                summary_parts.append(f"  - {filename}: {file_type} file")

            if web_count > 3:
                summary_parts.append(f"  ... and {web_count - 3} more web files")

        # GitHub analysis
        if "github_analysis" in content:
            github = content["github_analysis"]
            summary_parts.append("GITHUB REPOSITORY ANALYSIS:")
            summary_parts.append(f"  - Total commits: {github.get('total_commits', 0)}")
            summary_parts.append(
                f"  - Development span: {github.get('development_span_days', 0)} days"
            )

            if "commit_message_quality" in github:
                quality = github["commit_message_quality"]
                summary_parts.append(
                    f"  - Commit message quality: {quality.get('score', 0)}/100 ({quality.get('quality_level', 'unknown')})"
                )

            summary_parts.append(
                f"  - Consistency score: {github.get('consistency_score', 0):.2f}"
            )

        # WordPress analysis
        if any(key.startswith("wordpress_") for key in content):
            summary_parts.append("WORDPRESS SITE ANALYSIS:")
            for key, value in content.items():
                if key.startswith("wordpress_"):
                    component = key.replace("wordpress_", "").replace("_", " ").title()
                    file_count = len(value.get("files_found", []))
                    summary_parts.append(f"  - {component}: {file_count} files")

        return (
            "\n".join(summary_parts)
            if summary_parts
            else "No content available for analysis"
        )

    def _get_prompt_sections(
        self, assignment_type: Optional[str] = None
    ) -> dict[str, str]:
        """Get reusable prompt sections based on assignment type.
        
        Args:
            assignment_type: Type of assignment for section selection.
            
        Returns:
            Dictionary of prompt sections for template substitution.
        """
        sections = {}

        # Get output format section
        if "output_format" in self.prompt_sections:
            sections["output_format"] = self.prompt_sections["output_format"]
        else:
            # Fallback output format
            sections["output_format"] = """REQUIRED OUTPUT FORMAT:
You MUST respond with a valid JSON object in exactly this format:

{
  "mark": [numeric score out of {max_mark}],
  "max_mark": {max_mark},
  "feedback": "[Detailed feedback covering strengths, weaknesses, and specific improvements needed]",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "confidence": [0.0 to 1.0 indicating your confidence in this assessment]
}

IMPORTANT:
- Respond ONLY with valid JSON - no additional text before or after
- Use double quotes for all strings
- Ensure the mark is a number between 0 and {max_mark}
- Keep feedback concise but comprehensive
- List 2-4 key strengths and improvements"""

        # Get additional instructions for assignment type
        if assignment_type and "additional_instructions" in self.prompt_sections:
            instructions = self.prompt_sections["additional_instructions"]
            if assignment_type in instructions:
                sections["additional_instructions"] = instructions[assignment_type]
            else:
                sections["additional_instructions"] = ""
        else:
            sections["additional_instructions"] = ""

        return sections

    def _get_submission_metadata(self, student_data: dict[str, Any]) -> dict[str, str]:
        """Extract additional metadata for prompt context.
        
        Args:
            student_data: Student submission data.
            
        Returns:
            Dictionary of metadata for prompt context.
        """
        metadata = {}

        # File count information
        content = student_data.get("content", {})
        total_files = 0

        for content_type in ["documents", "code", "web"]:
            if content_type in content:
                count = len(content[content_type])
                total_files += count
                metadata[f"{content_type}_count"] = str(count)

        metadata["total_files"] = str(total_files)

        # Repository information
        if "github_analysis" in content:
            github = content["github_analysis"]
            metadata["has_github"] = "yes"
            metadata["github_commits"] = str(github.get("total_commits", 0))
        else:
            metadata["has_github"] = "no"
            metadata["github_commits"] = "0"

        return metadata

    def list_available_prompts(self) -> list[str]:
        """Get list of available prompt template names.
        
        Returns:
            List of available prompt template names.
        """
        return list(self.prompts.keys())

    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and is properly formatted.
        
        Args:
            template_name: Name of template to validate.
            
        Returns:
            True if template is valid, False otherwise.
        """
        if template_name not in self.prompts:
            return False

        template_data = self.prompts[template_name]

        # Check required fields
        if "template" not in template_data:
            return False

        # Check for common placeholders
        template_text = template_data["template"]
        required_placeholders = [
            "assignment_spec",
            "rubric",
            "student_id",
            "content_summary",
        ]

        for placeholder in required_placeholders:
            if f"{{{placeholder}}}" not in template_text:
                logger.warning(
                    f"Template '{template_name}' missing recommended placeholder: {{{placeholder}}}"
                )

        return True
