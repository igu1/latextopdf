"""
Helper utilities for the LaTeX to PDF converter
"""

import logging
import io
from typing import Any

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(level=level)
    logger.setLevel(level)


def create_pdf_response(pdf_bytes: bytes, filename: str) -> StreamingResponse:
    """
    Create a FastAPI StreamingResponse for PDF files
    
    Args:
        pdf_bytes: PDF file content as bytes
        filename: Filename for the downloaded file
        
    Returns:
        FastAPI StreamingResponse configured for PDF download
    """
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def validate_file_size(pdf_bytes: bytes, max_size_mb: int = 50) -> bool:
    """
    Validate that PDF file size is within acceptable limits
    
    Args:
        pdf_bytes: PDF file content as bytes
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        True if file size is valid, False otherwise
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return len(pdf_bytes) <= max_size_bytes
