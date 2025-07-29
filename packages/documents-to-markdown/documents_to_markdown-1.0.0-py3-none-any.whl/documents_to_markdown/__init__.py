#!/usr/bin/env python3
"""
Documents to Markdown Converter

A comprehensive Python library for converting various document types to Markdown format.

Supported formats:
- Word documents (.docx, .doc)
- PDF documents (.pdf)
- Excel spreadsheets (.xlsx, .xlsm, .xls)
- Images (.png, .jpg, .jpeg, .gif, .bmp, .tiff)
- Plain text files (.txt, .csv, .tsv, .log)

Features:
- Automatic section numbering
- Modular architecture with pluggable converters
- AI-powered image content extraction
- Text chunking for large documents
- Batch processing capabilities
- Comprehensive logging and error handling

Example usage:
    >>> from documents_to_markdown import DocumentConverter
    >>> converter = DocumentConverter()
    >>> result = converter.convert_file("document.docx", "output.md")
    >>> print(f"Conversion successful: {result}")

    >>> # Batch conversion
    >>> results = converter.convert_all("input_folder", "output_folder")
    >>> print(f"Converted {results['successful_conversions']} files")
"""

__version__ = "1.0.0"
__author__ = "Felix"
__email__ = "yangzhenwu@gmail.com"
__license__ = "MIT"

# Import main classes for easy access
from .api import DocumentConverter, convert_document, convert_folder, get_supported_formats
from .services.document_converter_manager import DocumentConverterManager
from .config import get_config, save_config, get_config_directory

# Import individual converters for advanced usage
from .services.word_converter import WordDocumentConverter
from .services.pdf_converter import PDFDocumentConverter
from .services.excel_converter import ExcelDocumentConverter
from .services.image_converter import ImageDocumentConverter
from .services.plain_text_converter import PlainTextConverter

# Import base converter for custom converter development
from .services.base_converter import BaseDocumentConverter

__all__ = [
    # Main API
    "DocumentConverter",
    "DocumentConverterManager",

    # Convenience functions
    "convert_document",
    "convert_folder",
    "get_supported_formats",

    # Configuration functions
    "get_config",
    "save_config",
    "get_config_directory",

    # Individual converters
    "WordDocumentConverter",
    "PDFDocumentConverter",
    "ExcelDocumentConverter",
    "ImageDocumentConverter",
    "PlainTextConverter",

    # Base class for custom converters
    "BaseDocumentConverter",

    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# Package-level configuration
import logging

# Set up default logging configuration
logging.getLogger(__name__).addHandler(logging.NullHandler())

def get_version():
    """Get the package version."""
    return __version__

def get_supported_formats():
    """Get list of all supported file formats."""
    return [
        '.docx', '.doc',  # Word documents
        '.pdf',           # PDF documents
        '.xlsx', '.xlsm', '.xls',  # Excel spreadsheets
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',  # Images
        '.txt', '.csv', '.tsv', '.log'  # Plain text files
    ]

def get_converter_info():
    """Get information about available converters."""
    converter = DocumentConverter()
    return converter.get_conversion_statistics()
