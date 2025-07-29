#!/usr/bin/env python3
"""
MarkMate CLI Main Entry Point

Command-line interface for MarkMate: Your AI Teaching Assistant for Assignments and Assessment
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from . import consolidate, extract, generate_config, grade, scan


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands.
    
    Returns:
        Configured ArgumentParser with all subcommands.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="mark-mate",
        description="MarkMate: Your AI Teaching Assistant for Assignments and Assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic workflow
  mark-mate consolidate submissions/
  mark-mate scan processed_submissions/ --output github_urls.txt
  mark-mate extract processed_submissions/ --output results.json
  mark-mate grade results.json rubric.txt --output grades.json

  # Use custom grading configuration
  mark-mate grade results.json rubric.txt --config grading_config.yaml

  # Generate a configuration template
  mark-mate generate-config --output my_config.yaml

API Keys Required:
  Set at least one of the following environment variables:
  - ANTHROPIC_API_KEY    (for Claude 3.5 Sonnet)
  - OPENAI_API_KEY       (for GPT-4o/GPT-4o-mini)
  - GEMINI_API_KEY       (for Google Gemini Pro)

Auto-Configuration:
  When no --config is provided, MarkMate automatically creates an optimal
  configuration based on your available API keys.

For more help on a specific command:
  mark-mate <command> --help
        """,
    )

    parser.add_argument("--version", action="version", version="MarkMate 0.1.0")

    subparsers: argparse._SubParsersAction[argparse.ArgumentParser] = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # Add subcommand parsers
    consolidate.add_parser(subparsers)
    scan.add_parser(subparsers)
    extract.add_parser(subparsers)
    grade.add_parser(subparsers)
    generate_config.add_parser(subparsers)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point.
    
    Args:
        argv: Optional command line arguments.
        
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser: argparse.ArgumentParser = create_parser()
    args: argparse.Namespace = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Route to appropriate command handler
        if args.command == "consolidate":
            return consolidate.main(args)
        elif args.command == "scan":
            return scan.main(args)
        elif args.command == "extract":
            return extract.main(args)
        elif args.command == "grade":
            return grade.main(args)
        elif args.command == "generate-config":
            return generate_config.main(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
