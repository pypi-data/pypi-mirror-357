"""MarkMate Grading Configuration Management.

Handles loading and validation of grading configurations from YAML files.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class GraderConfig:
    """Configuration for a single grader."""

    name: str
    provider: str
    model: str
    weight: float = 1.0
    primary_feedback: bool = False
    rate_limit: Optional[int] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2000


@dataclass
class GradingConfig:
    """Complete grading configuration."""

    runs_per_grader: int = 1
    averaging_method: str = "mean"
    parallel_execution: bool = True
    graders: list[GraderConfig] = field(default_factory=list)

    # Execution settings
    max_cost_per_student: float = 1.0
    timeout_per_run: int = 60
    retry_attempts: int = 3
    show_progress: bool = True

    # Statistical settings
    confidence_threshold: float = 0.7
    max_variance_threshold: float = 0.15  # As fraction of max_mark

    # Prompt configuration
    prompts: dict[str, Any] = field(default_factory=dict)
    prompt_sections: dict[str, Any] = field(default_factory=dict)


class GradingConfigManager:
    """Manages grading configurations and provides defaults."""

    DEFAULT_CONFIG: dict[str, Any] = {
        "grading": {
            "runs_per_grader": 1,
            "averaging_method": "mean",
            "parallel_execution": True,
        },
        "graders": [
            {
                "name": "claude-sonnet",
                "provider": "anthropic",
                "model": "claude-3-5-sonnet",
                "weight": 2.0,
                "primary_feedback": True,
                "rate_limit": 50,
            },
            {
                "name": "gpt4o-mini",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "weight": 1.0,
                "rate_limit": 100,
            },
        ],
        "execution": {
            "max_cost_per_student": 0.50,
            "timeout_per_run": 60,
            "retry_attempts": 3,
            "show_progress": True,
        },
        "prompts": {
            "default": {
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
{additional_instructions}

{output_format}""",
            },
            "wordpress": {
                "system": "You are an expert WordPress developer and educator evaluating student work.",
                "template": """WORDPRESS ASSIGNMENT:
{assignment_spec}

GRADING RUBRIC:
{rubric}

STUDENT WORDPRESS SITE (Student ID: {student_id}):
{content_summary}

WORDPRESS-SPECIFIC EVALUATION:
- Assess theme customization and design choices
- Evaluate plugin usage and AI integration
- Review content quality and organization
- Check security configuration
{additional_instructions}

{output_format}""",
            },
        },
        "prompt_sections": {
            "additional_instructions": {
                "wordpress": """5. For WordPress assignments, assess security, AI integration, and content quality
6. Evaluate theme customization and plugin implementation
7. Check for appropriate use of AI-related plugins""",
                "programming": """5. Assess code quality, structure, and best practices
6. Evaluate testing and documentation
7. Check for proper error handling and edge cases""",
                "general": """5. Assess overall presentation and organization
6. Evaluate adherence to assignment requirements""",
            },
            "output_format": """REQUIRED OUTPUT FORMAT:
You MUST respond with a valid JSON object in exactly this format:

{{
  "mark": [numeric score out of {max_mark}],
  "max_mark": {max_mark},
  "feedback": "[Detailed feedback covering strengths, weaknesses, and specific improvements needed]",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "confidence": [0.0 to 1.0 indicating your confidence in this assessment]
}}

IMPORTANT:
- Respond ONLY with valid JSON - no additional text before or after
- Use double quotes for all strings
- Ensure the mark is a number between 0 and {max_mark}
- Keep feedback concise but comprehensive
- List 2-4 key strengths and improvements""",
        },
    }

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        pass

    def load_config(self, config_path: Optional[str] = None) -> GradingConfig:
        """Load grading configuration from file or use defaults.

        Args:
            config_path: Path to YAML configuration file. If None, uses defaults.

        Returns:
            GradingConfig object with loaded configuration.
        """
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
                logger.info(f"Loaded grading configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                logger.info("Using default configuration")
                config_data = self.DEFAULT_CONFIG
        else:
            if config_path:
                logger.warning(f"Config file {config_path} not found, using defaults")
            config_data = self.DEFAULT_CONFIG

        return self._parse_config(config_data)

    def _parse_config(self, config_data: dict[str, Any]) -> GradingConfig:
        """Parse configuration data into GradingConfig object.
        
        Args:
            config_data: Raw configuration dictionary.
            
        Returns:
            Parsed GradingConfig object.
        """
        # Extract grading settings
        grading_settings = config_data.get("grading", {})
        execution_settings = config_data.get("execution", {})

        # Parse graders
        graders: list[GraderConfig] = []
        for grader_data in config_data.get("graders", []):
            grader = GraderConfig(
                name=grader_data["name"],
                provider=grader_data["provider"],
                model=grader_data["model"],
                weight=grader_data.get("weight", 1.0),
                primary_feedback=grader_data.get("primary_feedback", False),
                rate_limit=grader_data.get("rate_limit"),
                system_prompt=grader_data.get("system_prompt"),
                temperature=grader_data.get("temperature", 0.1),
                max_tokens=grader_data.get("max_tokens", 2000),
            )
            graders.append(grader)

        # Create main config
        config = GradingConfig(
            runs_per_grader=grading_settings.get("runs_per_grader", 1),
            averaging_method=grading_settings.get("averaging_method", "mean"),
            parallel_execution=grading_settings.get("parallel_execution", True),
            graders=graders,
            max_cost_per_student=execution_settings.get("max_cost_per_student", 0.50),
            timeout_per_run=execution_settings.get("timeout_per_run", 60),
            retry_attempts=execution_settings.get("retry_attempts", 3),
            show_progress=execution_settings.get("show_progress", True),
            prompts=config_data.get("prompts", {}),
            prompt_sections=config_data.get("prompt_sections", {}),
        )

        # Validate configuration
        self._validate_config(config)

        return config

    def _validate_config(self, config: GradingConfig) -> None:
        """Validate configuration settings.
        
        Args:
            config: Configuration to validate.
            
        Raises:
            ValueError: If configuration is invalid.
        """
        if not config.graders:
            raise ValueError("At least one grader must be configured")

        if config.runs_per_grader < 1:
            raise ValueError("runs_per_grader must be at least 1")

        if config.averaging_method not in [
            "mean",
            "median",
            "weighted_mean",
            "trimmed_mean",
        ]:
            raise ValueError(f"Invalid averaging_method: {config.averaging_method}")

        # Validate graders
        provider_counts: dict[str, int] = {}
        primary_feedback_count = 0

        for grader in config.graders:
            if grader.provider not in ["anthropic", "openai", "gemini"]:
                raise ValueError(f"Invalid provider: {grader.provider}")

            if grader.weight <= 0:
                raise ValueError(f"Grader {grader.name} weight must be positive")

            if grader.primary_feedback:
                primary_feedback_count += 1

            provider_counts[grader.provider] = (
                provider_counts.get(grader.provider, 0) + 1
            )

        if primary_feedback_count > 1:
            raise ValueError("Only one grader can be marked as primary_feedback")

        logger.info(
            f"Configuration validated: {len(config.graders)} graders, "
            f"{config.runs_per_grader} runs each, "
            f"{config.averaging_method} averaging"
        )

    def save_default_config(self, output_path: str) -> None:
        """Save default configuration to a YAML file.
        
        Args:
            output_path: Path where to save the configuration file.
        """
        with open(output_path, "w") as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, indent=2)
        logger.info(f"Default configuration saved to {output_path}")

    def create_gemini_config(self) -> dict[str, Any]:
        """Create a configuration that includes Gemini provider.
        
        Returns:
            Configuration dictionary with Gemini grader included.
        """
        config = self.DEFAULT_CONFIG.copy()

        # Add Gemini grader
        gemini_grader = {
            "name": "gemini-pro",
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "weight": 1.0,
            "rate_limit": 60,
        }

        config["graders"].append(gemini_grader)
        return config

    def create_minimal_config(self) -> dict[str, Any]:
        """Create a minimal single-grader configuration.
        
        Returns:
            Minimal configuration dictionary with single grader.
        """
        return {
            "grading": {
                "runs_per_grader": 1,
                "averaging_method": "mean",
                "parallel_execution": False,
            },
            "graders": [
                {
                    "name": "claude-sonnet",
                    "provider": "anthropic",
                    "model": "claude-3-5-sonnet",
                    "weight": 1.0,
                    "primary_feedback": True,
                    "rate_limit": 50,
                }
            ],
            "execution": {
                "max_cost_per_student": 0.25,
                "timeout_per_run": 60,
                "retry_attempts": 2,
                "show_progress": True,
            },
        }

    def get_providers_from_config(self, config: GradingConfig) -> list[str]:
        """Extract unique providers from configuration.
        
        Args:
            config: Grading configuration.
            
        Returns:
            List of unique provider names.
        """
        providers: set[str] = set()
        for grader in config.graders:
            providers.add(grader.provider)
        return list(providers)

    def filter_graders_by_availability(
        self, config: GradingConfig, available_providers: list[str]
    ) -> GradingConfig:
        """Filter graders based on available providers.
        
        Args:
            config: Original grading configuration.
            available_providers: List of available provider names.
            
        Returns:
            New configuration with only available graders.
            
        Raises:
            ValueError: If no graders are available.
        """
        filtered_graders = [
            grader
            for grader in config.graders
            if grader.provider in available_providers
        ]

        if not filtered_graders:
            raise ValueError("No graders available with current API key configuration")

        # Create new config with filtered graders
        new_config = GradingConfig(
            runs_per_grader=config.runs_per_grader,
            averaging_method=config.averaging_method,
            parallel_execution=config.parallel_execution,
            graders=filtered_graders,
            max_cost_per_student=config.max_cost_per_student,
            timeout_per_run=config.timeout_per_run,
            retry_attempts=config.retry_attempts,
            show_progress=config.show_progress,
        )

        logger.info(f"Filtered to {len(filtered_graders)} available graders")
        return new_config
