"""
Banana Slides - AI-powered PPT generation CLI tool
"""

from banana_slides.core.generator import AIService, ProjectContext
from banana_slides.core.exporter import ExportService
from banana_slides.core.file_service import FileService

__version__ = "1.0.0"

__all__ = [
    "AIService",
    "ProjectContext",
    "ExportService",
    "FileService",
    "__version__",
]
