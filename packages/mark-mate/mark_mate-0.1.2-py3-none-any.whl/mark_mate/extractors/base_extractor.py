"""Base extractor class for the content extraction system.

This module provides the abstract base class that all extractors should inherit from,
ensuring consistent interface and behavior across different file type extractors.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

from .models import ExtractionResult, FileInfo

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for all content extractors."""

    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        """Initialize the extractor.

        Args:
            config: Optional configuration dictionary for extractor settings.
        """
        self.config: dict[str, Any] = config or {}
        self.supported_extensions: list[str] = []
        self.extractor_name: str = ""

    @abstractmethod
    def can_extract(self, file_path: str) -> bool:
        """Check if this extractor can handle the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if this extractor can handle the file, False otherwise.
        """
        pass

    @abstractmethod
    def extract_content(self, file_path: str) -> ExtractionResult:
        """Extract content from the specified file.

        Args:
            file_path: Path to the file to extract content from.

        Returns:
            ExtractionResult containing extracted content and metadata.
        """
        pass

    def get_file_info(self, file_path: str) -> FileInfo:
        """Get basic file information.

        Args:
            file_path: Path to the file.

        Returns:
            FileInfo containing file metadata.
        """
        try:
            stat: os.stat_result = os.stat(file_path)
            return FileInfo(
                filename=os.path.basename(file_path),
                size=stat.st_size,
                extension=os.path.splitext(file_path)[1].lower(),
                extractor=self.extractor_name,
            )
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return FileInfo(
                filename=os.path.basename(file_path),
                size=0,
                extension=os.path.splitext(file_path)[1].lower(),
                extractor=self.extractor_name,
                error=str(e),
            )

    def create_error_result(self, file_path: str, error: Exception) -> ExtractionResult:
        """Create a standardized error result.

        Args:
            file_path: Path to the file that caused the error.
            error: The exception that occurred.

        Returns:
            Standardized error result.
        """
        file_info = self.get_file_info(file_path)
        return ExtractionResult.create_error(
            file_path=file_path,
            error=error,
            extractor_name=self.extractor_name,
            file_info=file_info,
        )

    def create_success_result(
        self, file_path: str, content: str, analysis: Optional[dict[str, Any]] = None
    ) -> ExtractionResult:
        """Create a standardized success result.

        Args:
            file_path: Path to the successfully processed file.
            content: Extracted text content.
            analysis: Optional analysis results.

        Returns:
            Standardized success result.
        """
        file_info = self.get_file_info(file_path)
        return ExtractionResult.create_success(
            content=content,
            extractor_name=self.extractor_name,
            file_info=file_info,
            analysis=analysis,
        )
