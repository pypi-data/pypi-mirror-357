"""Pydantic models for extractor results.

This module defines the data structures used by all extractors,
replacing the loose dict[str, Any] structures with validated models.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """File metadata information."""
    
    filename: str = Field(..., description="Name of the file")
    size: int = Field(ge=0, description="File size in bytes")
    extension: str = Field(..., description="File extension (lowercase)")
    extractor: str = Field(..., description="Name of the extractor that processed this file")
    error: Optional[str] = Field(default=None, description="Error message if file info retrieval failed")


class ExtractionResult(BaseModel):
    """Base result structure for all extraction operations."""
    
    success: bool = Field(..., description="Whether extraction was successful")
    content: str = Field(default="", description="Extracted text content")
    file_info: FileInfo = Field(..., description="File metadata")
    extractor: str = Field(..., description="Name of the extractor used")
    content_length: int = Field(ge=0, description="Length of extracted content")
    analysis: Dict[str, Any] = Field(default_factory=dict, description="Analysis results")
    error: Optional[str] = Field(default=None, description="Error message if extraction failed")

    @classmethod
    def create_error(
        cls, 
        file_path: str, 
        error: Exception, 
        extractor_name: str,
        file_info: FileInfo
    ) -> "ExtractionResult":
        """Create a standardized error result."""
        import os
        return cls(
            success=False,
            error=str(error),
            file_info=file_info,
            extractor=extractor_name,
            content=f"[EXTRACTION ERROR] Could not process {os.path.basename(file_path)}: {str(error)[:100]}",
            content_length=0,
        )

    @classmethod
    def create_success(
        cls,
        content: str,
        extractor_name: str,
        file_info: FileInfo,
        analysis: Optional[Dict[str, Any]] = None,
    ) -> "ExtractionResult":
        """Create a standardized success result."""
        return cls(
            success=True,
            content=content,
            file_info=file_info,
            extractor=extractor_name,
            analysis=analysis or {},
            content_length=len(content) if content else 0,
        )