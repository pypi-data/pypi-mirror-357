#!/usr/bin/env python3
"""
MarkMate Grade Command

Simplified grading using the enhanced multi-provider system with YAML configuration.
"""

import argparse
import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def add_parser(subparsers) -> argparse.ArgumentParser:
    """Add grade command parser."""
    parser = subparsers.add_parser(
        "grade",
        help="Grade student submissions using AI",
        description="AI-powered grading with multi-provider support and statistical aggregation",
    )

    parser.add_argument(
        "extracted_content",
        help="Path to extracted content JSON file (from extract command)",
    )

    parser.add_argument(
        "assignment_spec", help="Path to assignment specification/rubric file"
    )

    parser.add_argument(
        "--output",
        default="grading_results.json",
        help="Output JSON file for grading results (default: grading_results.json)",
    )

    parser.add_argument(
        "--rubric",
        help="Path to separate rubric file (optional, can be extracted from assignment spec)",
    )

    parser.add_argument(
        "--max-students",
        type=int,
        help="Maximum number of students to grade (for testing)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be graded without actually calling LLM APIs",
    )

    parser.add_argument(
        "--config",
        help="Path to YAML grading configuration file (optional - uses defaults if not provided)",
    )

    return parser


def check_available_providers():
    """
    Check which LLM providers have API keys available.

    Returns:
        List of available provider names
    """
    available = []

    if os.getenv("ANTHROPIC_API_KEY"):
        available.append("anthropic")
    else:
        logger.info("ANTHROPIC_API_KEY not found - Claude grading will be disabled")

    if os.getenv("OPENAI_API_KEY"):
        available.append("openai")
    else:
        logger.info("OPENAI_API_KEY not found - OpenAI grading will be disabled")

    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        available.append("gemini")
    else:
        logger.info(
            "GEMINI_API_KEY or GOOGLE_API_KEY not found - Gemini grading will be disabled"
        )

    return available


def create_default_config(available_providers):
    """
    Create a default grading configuration based on available providers.

    Args:
        available_providers: List of available provider names

    Returns:
        Dictionary containing default configuration
    """
    if not available_providers:
        raise ValueError("No API keys available for any LLM provider")

    graders = []

    # Add graders based on available providers
    if "anthropic" in available_providers:
        graders.append(
            {
                "name": "claude-sonnet",
                "provider": "anthropic",
                "model": "claude-3-5-sonnet",
                "weight": 2.0,
                "primary_feedback": True,
                "rate_limit": 50,
            }
        )

    if "openai" in available_providers:
        graders.append(
            {
                "name": "gpt4o-mini",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "weight": 1.0,
                "rate_limit": 100,
            }
        )

    if "gemini" in available_providers:
        graders.append(
            {
                "name": "gemini-pro",
                "provider": "gemini",
                "model": "gemini-1.5-pro",
                "weight": 1.0,
                "rate_limit": 60,
            }
        )

    # Determine runs based on number of graders
    runs_per_grader = 3 if len(graders) == 1 else 1

    return {
        "grading": {
            "runs_per_grader": runs_per_grader,
            "averaging_method": "weighted_mean" if len(graders) > 1 else "mean",
            "parallel_execution": True,
        },
        "graders": graders,
        "execution": {
            "max_cost_per_student": 0.50,
            "timeout_per_run": 60,
            "retry_attempts": 3,
            "show_progress": True,
        },
    }


def load_extracted_content(content_file):
    """
    Load extracted content from JSON file.

    Args:
        content_file: Path to the extracted content JSON file

    Returns:
        Dictionary containing extracted content data
    """
    try:
        with open(content_file, encoding="utf-8") as f:
            content = json.load(f)

        if "students" not in content:
            raise ValueError("Invalid content file format: missing 'students' key")

        logger.info(f"Loaded content for {len(content['students'])} students")
        return content

    except Exception as e:
        logger.error(f"Error loading extracted content: {e}")
        raise


def load_assignment_spec(spec_file):
    """
    Load assignment specification/rubric.

    Args:
        spec_file: Path to the assignment specification file

    Returns:
        String containing the assignment specification
    """
    try:
        with open(spec_file, encoding="utf-8") as f:
            spec = f.read()

        logger.info(f"Loaded assignment specification from: {spec_file}")
        return spec

    except Exception as e:
        logger.error(f"Error loading assignment specification: {e}")
        raise


def grade_submission(student_data, assignment_spec, grading_system, rubric=None):
    """
    Grade a single student submission.

    Args:
        student_data: Extracted content for the student
        assignment_spec: Assignment specification/rubric
        grading_system: EnhancedGradingSystem instance
        rubric: Optional separate rubric

    Returns:
        Dictionary containing grading results
    """
    try:
        result = grading_system.grade_submission(
            student_data, assignment_spec, rubric=rubric
        )

        return result

    except Exception as e:
        logger.error(
            f"Error grading student {student_data.get('student_id', 'unknown')}: {e}"
        )
        return {
            "error": str(e),
            "graded": False,
            "timestamp": datetime.now().isoformat(),
        }


def main(args) -> int:
    """Main grading logic."""
    content_file = args.extracted_content
    spec_file = args.assignment_spec
    output_file = args.output
    rubric_file = args.rubric
    max_students = args.max_students
    dry_run = args.dry_run
    config_file = args.config

    logger.info(f"Grading extracted content from: {content_file}")
    logger.info(f"Assignment specification: {spec_file}")
    if rubric_file:
        logger.info(f"Separate rubric file: {rubric_file}")
    if dry_run:
        logger.info("DRY RUN MODE - No API calls will be made")

    # Initialize grading system
    try:
        from ..core.enhanced_grader import EnhancedGradingSystem

        if config_file:
            logger.info(f"Using configuration file: {config_file}")
            grading_system = EnhancedGradingSystem(config_file)
        else:
            logger.info(
                "No configuration file provided, creating default configuration"
            )

            # Check available providers
            available_providers = check_available_providers()
            if not available_providers:
                logger.error("No API keys available for any LLM provider")
                logger.error(
                    "Please set at least one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY"
                )
                return 1

            logger.info(f"Available providers: {', '.join(available_providers)}")

            # Create default config
            default_config = create_default_config(available_providers)

            # Save temporary config file
            import tempfile

            import yaml

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
                temp_config_path = f.name

            logger.info(
                f"Created default configuration with {len(default_config['graders'])} graders"
            )
            grading_system = EnhancedGradingSystem(temp_config_path)

            # Clean up temp file
            os.unlink(temp_config_path)

        logger.info(
            f"Initialized grading system with {len(grading_system.config.graders)} graders"
        )

        # Show grader details
        for grader in grading_system.config.graders:
            logger.info(
                f"  - {grader.name} ({grader.provider}/{grader.model}, weight: {grader.weight})"
            )

        logger.info(f"Runs per grader: {grading_system.config.runs_per_grader}")
        logger.info(f"Averaging method: {grading_system.config.averaging_method}")

    except Exception as e:
        logger.error(f"Failed to initialize grading system: {e}")
        return 1

    # Load content and assignment spec
    try:
        content_data = load_extracted_content(content_file)
        assignment_spec = load_assignment_spec(spec_file)

        rubric = None
        if rubric_file:
            rubric = load_assignment_spec(rubric_file)  # Same loading logic

    except Exception as e:
        logger.error(f"Failed to load required files: {e}")
        return 1

    # Filter students if max_students is specified
    students = content_data["students"]
    if max_students:
        student_ids = list(students.keys())[:max_students]
        students = {sid: students[sid] for sid in student_ids}
        logger.info(f"Processing only first {len(students)} students")

    if dry_run:
        logger.info("DRY RUN - Would grade the following students:")
        for student_id in sorted(students.keys()):
            logger.info(f"  {student_id}")
        logger.info(
            f"Using {len(grading_system.config.graders)} graders with {grading_system.config.runs_per_grader} runs each"
        )
        return 0

    # Grade each student
    grading_results = {
        "grading_session": {
            "timestamp": datetime.now().isoformat(),
            "total_students": len(students),
            "assignment_spec_file": spec_file,
            "rubric_file": rubric_file,
            "source_content_file": content_file,
            "config": {
                "graders": [g.name for g in grading_system.config.graders],
                "runs_per_grader": grading_system.config.runs_per_grader,
                "averaging_method": grading_system.config.averaging_method,
                "config_file": config_file,
            },
        },
        "results": {},
    }

    graded_count = 0
    for student_id, student_data in sorted(students.items()):
        logger.info(
            f"Grading student {student_id} ({graded_count + 1}/{len(students)})"
        )

        result = grade_submission(
            student_data, assignment_spec, grading_system, rubric=rubric
        )

        grading_results["results"][student_id] = result
        graded_count += 1

    # Save results
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(grading_results, f, indent=2, ensure_ascii=False)

        logger.info("Grading complete!")
        logger.info(f"Graded {graded_count} students")
        logger.info(f"Results saved to: {output_file}")

        # Show summary statistics
        successful_grades = [
            r for r in grading_results["results"].values() if not r.get("error")
        ]
        if successful_grades:
            logger.info(f"Successfully graded: {len(successful_grades)} students")

        # Show enhanced grading statistics
        session_summary = grading_system.get_session_summary()
        logger.info(
            f"Total API calls: {session_summary['session_stats']['total_api_calls']}"
        )
        logger.info(
            f"Total cost: ${session_summary['session_stats']['total_cost']:.4f}"
        )
        if session_summary["duration_seconds"] > 0:
            logger.info(
                f"Processing time: {session_summary['duration_seconds']:.1f} seconds"
            )

        return 0

    except Exception as e:
        logger.error(f"Error saving results: {e}")
        return 1
