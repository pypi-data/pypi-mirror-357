#!/usr/bin/env python3
"""
MarkMate Generate Config Command

Generate YAML configuration templates for grading.
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Any, Dict

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def add_parser(subparsers) -> argparse.ArgumentParser:
    """Add generate-config command parser."""
    parser = subparsers.add_parser(
        "generate-config",
        help="Generate grading configuration templates",
        description="Generate YAML configuration files for customized grading setups",
    )

    parser.add_argument(
        "--output",
        default="grading_config.yaml",
        help="Output YAML file path (default: grading_config.yaml)",
    )

    parser.add_argument(
        "--template",
        choices=["full", "minimal", "single-provider", "cost-optimized"],
        default="full",
        help="Configuration template type (default: full)",
    )

    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "gemini"],
        help="Single provider for single-provider template",
    )

    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing configuration file"
    )

    return parser


def check_available_providers():
    """Check which providers have API keys available."""
    available = []

    if os.getenv("ANTHROPIC_API_KEY"):
        available.append("anthropic")

    if os.getenv("OPENAI_API_KEY"):
        available.append("openai")

    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        available.append("gemini")

    return available


def _add_default_prompts(config):
    """Add default prompts to a configuration."""
    from ..config.grading_config import GradingConfigManager

    config_manager = GradingConfigManager()
    default_prompts = config_manager.DEFAULT_CONFIG.get("prompts", {})
    default_prompt_sections = config_manager.DEFAULT_CONFIG.get("prompt_sections", {})

    config["prompts"] = default_prompts
    config["prompt_sections"] = default_prompt_sections
    return config


def create_full_template() -> Dict[str, Any]:
    """Create full-featured configuration template."""
    config = {
        "grading": {
            "runs_per_grader": 3,
            "averaging_method": "weighted_mean",
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
                "system_prompt": "You are an expert academic grader. Provide detailed, fair, and constructive feedback.",
                "temperature": 0.1,
                "max_tokens": 2000,
            },
            {
                "name": "gpt4o",
                "provider": "openai",
                "model": "gpt-4o",
                "weight": 1.5,
                "rate_limit": 60,
                "system_prompt": "You are an experienced educator providing thorough assessment.",
                "temperature": 0.1,
                "max_tokens": 2000,
            },
            {
                "name": "gpt4o-mini",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "weight": 1.0,
                "rate_limit": 100,
                "temperature": 0.1,
                "max_tokens": 1500,
            },
            {
                "name": "gemini-pro",
                "provider": "gemini",
                "model": "gemini-1.5-pro",
                "weight": 1.0,
                "rate_limit": 60,
                "temperature": 0.1,
                "max_tokens": 2000,
            },
        ],
        "execution": {
            "max_cost_per_student": 0.75,
            "timeout_per_run": 60,
            "retry_attempts": 3,
            "show_progress": True,
        },
    }

    return _add_default_prompts(config)


def create_minimal_template() -> Dict[str, Any]:
    """Create minimal configuration template."""
    available = check_available_providers()

    # Use the best available provider
    if "anthropic" in available:
        provider_config = {
            "name": "claude-sonnet",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet",
            "weight": 1.0,
            "primary_feedback": True,
            "rate_limit": 50,
        }
    elif "openai" in available:
        provider_config = {
            "name": "gpt4o-mini",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "weight": 1.0,
            "primary_feedback": True,
            "rate_limit": 100,
        }
    elif "gemini" in available:
        provider_config = {
            "name": "gemini-pro",
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "weight": 1.0,
            "primary_feedback": True,
            "rate_limit": 60,
        }
    else:
        # Default to Claude if no API keys available (user will need to add them)
        provider_config = {
            "name": "claude-sonnet",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet",
            "weight": 1.0,
            "primary_feedback": True,
            "rate_limit": 50,
        }

    config = {
        "grading": {
            "runs_per_grader": 3,
            "averaging_method": "mean",
            "parallel_execution": False,
        },
        "graders": [provider_config],
        "execution": {
            "max_cost_per_student": 0.25,
            "timeout_per_run": 60,
            "retry_attempts": 2,
            "show_progress": True,
        },
    }

    return _add_default_prompts(config)


def create_single_provider_template(provider: str) -> Dict[str, Any]:
    """Create single-provider configuration template."""
    provider_configs = {
        "anthropic": {
            "name": "claude-sonnet",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet",
            "weight": 1.0,
            "primary_feedback": True,
            "rate_limit": 50,
        },
        "openai": {
            "name": "gpt4o",
            "provider": "openai",
            "model": "gpt-4o",
            "weight": 1.0,
            "primary_feedback": True,
            "rate_limit": 60,
        },
        "gemini": {
            "name": "gemini-pro",
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "weight": 1.0,
            "primary_feedback": True,
            "rate_limit": 60,
        },
    }

    config = {
        "grading": {
            "runs_per_grader": 5,  # More runs with single provider
            "averaging_method": "mean",
            "parallel_execution": False,
        },
        "graders": [provider_configs[provider]],
        "execution": {
            "max_cost_per_student": 0.50,
            "timeout_per_run": 60,
            "retry_attempts": 3,
            "show_progress": True,
        },
    }

    return _add_default_prompts(config)


def create_cost_optimized_template() -> Dict[str, Any]:
    """Create cost-optimized configuration template."""
    available = check_available_providers()
    graders = []

    # Prioritize cheapest models
    if "openai" in available:
        graders.append(
            {
                "name": "gpt4o-mini",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "weight": 2.0,
                "primary_feedback": True,
                "rate_limit": 100,
            }
        )

    if "gemini" in available:
        graders.append(
            {
                "name": "gemini-pro",
                "provider": "gemini",
                "model": "gemini-pro",  # Use cheaper gemini-pro instead of 1.5-pro
                "weight": 1.0,
                "rate_limit": 60,
            }
        )

    # Add Claude as validation if available (but lower weight due to cost)
    if "anthropic" in available:
        graders.append(
            {
                "name": "claude-haiku",
                "provider": "anthropic",
                "model": "claude-3-haiku",  # Use cheaper Haiku model
                "weight": 1.0,
                "rate_limit": 50,
            }
        )

    if not graders:
        # Fallback to minimal config
        graders = [
            {
                "name": "gpt4o-mini",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "weight": 1.0,
                "primary_feedback": True,
                "rate_limit": 100,
            }
        ]

    config = {
        "grading": {
            "runs_per_grader": 1,  # Single run to minimize cost
            "averaging_method": "weighted_mean",
            "parallel_execution": True,
        },
        "graders": graders,
        "execution": {
            "max_cost_per_student": 0.15,  # Lower cost limit
            "timeout_per_run": 45,
            "retry_attempts": 2,
            "show_progress": True,
        },
    }

    return _add_default_prompts(config)


def add_comments_to_config(config_dict):
    """Add helpful comments to configuration."""
    # This is a simplified version - in practice you'd want to use a YAML library
    # that preserves comments, but for now we'll add them as string prefixes

    commented_lines = [
        "# MarkMate Grading Configuration",
        "# Generated automatically - customize as needed",
        "",
        "# Grading behavior settings",
    ]

    return commented_lines


def main(args) -> int:
    """Main config generation logic."""
    output_file = args.output
    template_type = args.template
    provider = args.provider
    force = args.force

    logger.info(f"Generating {template_type} configuration template")

    # Check if output file exists
    if Path(output_file).exists() and not force:
        logger.error(f"Configuration file {output_file} already exists")
        logger.error("Use --force to overwrite or choose a different --output path")
        return 1

    # Validate single-provider template
    if template_type == "single-provider" and not provider:
        logger.error("--provider is required when using single-provider template")
        return 1

    # Generate configuration
    try:
        if template_type == "full":
            config = create_full_template()
        elif template_type == "minimal":
            config = create_minimal_template()
        elif template_type == "single-provider":
            config = create_single_provider_template(provider)
        elif template_type == "cost-optimized":
            config = create_cost_optimized_template()
        else:
            logger.error(f"Unknown template type: {template_type}")
            return 1

        # Save configuration
        with open(output_file, "w") as f:
            # Add header comment
            f.write("# MarkMate Grading Configuration\n")
            f.write(f"# Template: {template_type}\n")
            f.write("# Generated automatically - customize as needed\n\n")

            yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)

        logger.info(f"Configuration saved to: {output_file}")

        # Show helpful information
        logger.info("Configuration details:")
        logger.info(f"  - Graders: {len(config['graders'])}")
        logger.info(f"  - Runs per grader: {config['grading']['runs_per_grader']}")
        logger.info(f"  - Averaging method: {config['grading']['averaging_method']}")
        logger.info(
            f"  - Max cost per student: ${config['execution']['max_cost_per_student']}"
        )

        # Check API key availability
        required_providers = set()
        for grader in config["graders"]:
            required_providers.add(grader["provider"])

        available_providers = check_available_providers()
        missing_providers = required_providers - set(available_providers)

        if missing_providers:
            logger.warning("Missing API keys for the following providers:")
            for provider in missing_providers:
                if provider == "anthropic":
                    logger.warning("  - Set ANTHROPIC_API_KEY for Claude grading")
                elif provider == "openai":
                    logger.warning("  - Set OPENAI_API_KEY for OpenAI grading")
                elif provider == "gemini":
                    logger.warning(
                        "  - Set GEMINI_API_KEY or GOOGLE_API_KEY for Gemini grading"
                    )
        else:
            logger.info("✓ All required API keys are available")

        logger.info("\nTo use this configuration:")
        logger.info(
            f"  mark-mate grade extracted.json assignment.txt --config {output_file}"
        )

        return 0

    except Exception as e:
        logger.error(f"Error generating configuration: {e}")
        return 1
