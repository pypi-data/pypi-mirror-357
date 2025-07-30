"""
MarkMate GUI Module

Cross-platform desktop application for MarkMate using Flet framework.
Provides a user-friendly interface for all MarkMate functionality while
sharing the same core business logic as the CLI.
"""

__version__ = "0.1.1"

from .main import main

__all__ = ["main"]