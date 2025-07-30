"""
MarkMate: Your AI Teaching Assistant for Assignments and Assessment

A comprehensive system for processing, consolidating, and grading student submissions
with support for multiple content types, GitHub repository analysis, WordPress assignments,
and AI-powered assessment.
"""

__version__ = "0.1.0"
__author__ = "MarkMate Development Team"
__email__ = "dev@markmate.ai"

# Import main classes for library usage
from .config.grading_config import GradingConfigManager
from .core.analyzer import ContentAnalyzer
from .core.enhanced_grader import EnhancedGradingSystem
from .core.llm_provider import LLMProvider
from .core.processor import AssignmentProcessor

# Legacy alias for backward compatibility (if needed)
GradingSystem = EnhancedGradingSystem

__all__ = [
    "EnhancedGradingSystem",
    "GradingSystem",  # Legacy alias
    "LLMProvider",
    "AssignmentProcessor",
    "ContentAnalyzer",
    "GradingConfigManager",
    "__version__",
]
