#!/usr/bin/env python3
"""
Documents to Markdown Converter - Public API

This module provides a clean, user-friendly API for converting documents to Markdown format.
It wraps the internal DocumentConverterManager with a simplified interface suitable for
library usage.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from .services.document_converter_manager import DocumentConverterManager
from .config import get_config, ensure_config_exists


class DocumentConverter:
    """
    Main API class for converting documents to Markdown format.
    
    This class provides a simplified interface for document conversion operations,
    suitable for use as a library in other Python applications.
    
    Example:
        >>> converter = DocumentConverter()
        >>> result = converter.convert_file("document.docx", "output.md")
        >>> print(f"Conversion successful: {result}")
        
        >>> # Batch conversion
        >>> results = converter.convert_all("input_folder", "output_folder")
        >>> print(f"Converted {results['successful_conversions']} files")
    """
    
    def __init__(self, add_section_numbers: bool = None, verbose: bool = None):
        """
        Initialize the document converter.

        Args:
            add_section_numbers: Whether to add automatic section numbering to headings
                                (None = use config, True/False = override config)
            verbose: Enable verbose logging output
                    (None = use config, True/False = override config)
        """
        # Load configuration
        config = ensure_config_exists()

        # Use config values if not explicitly overridden
        self.add_section_numbers = add_section_numbers if add_section_numbers is not None else config.get('add_section_numbers', True)
        self.verbose = verbose if verbose is not None else config.get('verbose_logging', False)

        # Configure logging
        log_level = config.get('logging', {}).get('level', 'INFO')
        if self.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(getattr(logging, log_level.upper(), logging.INFO))

        self._manager = None
        self._config = config
    
    def _get_manager(self, input_folder: str = "input", output_folder: str = "output") -> DocumentConverterManager:
        """Get or create a DocumentConverterManager instance."""
        if self._manager is None or self._manager.input_folder != Path(input_folder) or self._manager.output_folder != Path(output_folder):
            self._manager = DocumentConverterManager(
                input_folder=input_folder,
                output_folder=output_folder,
                add_section_numbers=self.add_section_numbers
            )
        return self._manager
    
    def convert_file(self, input_file: Union[str, Path], output_file: Union[str, Path]) -> bool:
        """
        Convert a single document to Markdown format.
        
        Args:
            input_file: Path to the input document file
            output_file: Path where the Markdown file should be saved
            
        Returns:
            True if conversion was successful, False otherwise
            
        Example:
            >>> converter = DocumentConverter()
            >>> success = converter.convert_file("report.docx", "report.md")
            >>> if success:
            ...     print("Document converted successfully!")
        """
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use a temporary manager for single file conversion
        temp_manager = DocumentConverterManager(
            input_folder=str(input_path.parent),
            output_folder=str(output_path.parent),
            add_section_numbers=self.add_section_numbers
        )
        
        return temp_manager.convert_file(input_path)
    
    def convert_all(self, input_folder: Union[str, Path] = "input", 
                   output_folder: Union[str, Path] = "output") -> Dict[str, Any]:
        """
        Convert all supported documents in a folder to Markdown format.
        
        Args:
            input_folder: Path to folder containing documents to convert
            output_folder: Path to folder where Markdown files will be saved
            
        Returns:
            Dictionary with conversion results and statistics:
            {
                "total_files": int,
                "successful_conversions": int,
                "failed_conversions": int,
                "results": [{"file": str, "status": str, "converter": str}, ...]
            }
            
        Example:
            >>> converter = DocumentConverter()
            >>> results = converter.convert_all("docs", "markdown")
            >>> print(f"Converted {results['successful_conversions']} out of {results['total_files']} files")
        """
        manager = self._get_manager(str(input_folder), str(output_folder))
        return manager.convert_all()
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of all supported file formats.
        
        Returns:
            List of supported file extensions (e.g., ['.docx', '.pdf', '.xlsx'])
            
        Example:
            >>> converter = DocumentConverter()
            >>> formats = converter.get_supported_formats()
            >>> print(f"Supported formats: {', '.join(formats)}")
        """
        manager = self._get_manager()
        return manager.get_supported_extensions()
    
    def can_convert(self, file_path: Union[str, Path]) -> bool:
        """
        Check if a file can be converted to Markdown.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file can be converted, False otherwise
            
        Example:
            >>> converter = DocumentConverter()
            >>> if converter.can_convert("document.docx"):
            ...     print("This file can be converted!")
        """
        path = Path(file_path)
        manager = self._get_manager()
        return manager.find_converter_for_file(path) is not None
    
    def get_convertible_files(self, folder_path: Union[str, Path]) -> List[Path]:
        """
        Get list of all convertible files in a folder.
        
        Args:
            folder_path: Path to the folder to scan
            
        Returns:
            List of file paths that can be converted
            
        Example:
            >>> converter = DocumentConverter()
            >>> files = converter.get_convertible_files("documents")
            >>> print(f"Found {len(files)} convertible files")
        """
        manager = self._get_manager(str(folder_path), "output")
        return manager.get_convertible_files()
    
    def get_conversion_statistics(self) -> Dict[str, Any]:
        """
        Get detailed information about available converters and supported formats.
        
        Returns:
            Dictionary with converter statistics and information
            
        Example:
            >>> converter = DocumentConverter()
            >>> stats = converter.get_conversion_statistics()
            >>> print(f"Available converters: {stats['total_converters']}")
            >>> for conv in stats['converters']:
            ...     print(f"- {conv['name']}: {', '.join(conv['supported_extensions'])}")
        """
        manager = self._get_manager()
        return manager.get_conversion_statistics()
    
    def set_section_numbering(self, enabled: bool) -> None:
        """
        Enable or disable automatic section numbering.
        
        Args:
            enabled: True to enable section numbering, False to disable
            
        Example:
            >>> converter = DocumentConverter()
            >>> converter.set_section_numbering(False)  # Disable numbering
        """
        self.add_section_numbers = enabled
        self._manager = None  # Reset manager to apply new setting
    
    def set_verbose_logging(self, enabled: bool) -> None:
        """
        Enable or disable verbose logging.
        
        Args:
            enabled: True to enable verbose logging, False for normal logging
            
        Example:
            >>> converter = DocumentConverter()
            >>> converter.set_verbose_logging(True)  # Enable debug output
        """
        self.verbose = enabled
        if enabled:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)


# Convenience functions for quick operations
def convert_document(input_file: Union[str, Path], output_file: Union[str, Path], 
                    add_section_numbers: bool = True) -> bool:
    """
    Quick function to convert a single document.
    
    Args:
        input_file: Path to the input document
        output_file: Path for the output Markdown file
        add_section_numbers: Whether to add section numbering
        
    Returns:
        True if conversion successful, False otherwise
        
    Example:
        >>> from documents_to_markdown import convert_document
        >>> success = convert_document("report.docx", "report.md")
    """
    converter = DocumentConverter(add_section_numbers=add_section_numbers)
    return converter.convert_file(input_file, output_file)


def convert_folder(input_folder: Union[str, Path], output_folder: Union[str, Path],
                  add_section_numbers: bool = True) -> Dict[str, Any]:
    """
    Quick function to convert all documents in a folder.
    
    Args:
        input_folder: Path to folder with documents to convert
        output_folder: Path to folder for output Markdown files
        add_section_numbers: Whether to add section numbering
        
    Returns:
        Dictionary with conversion results
        
    Example:
        >>> from documents_to_markdown import convert_folder
        >>> results = convert_folder("docs", "markdown")
        >>> print(f"Converted {results['successful_conversions']} files")
    """
    converter = DocumentConverter(add_section_numbers=add_section_numbers)
    return converter.convert_all(input_folder, output_folder)


def get_supported_formats() -> List[str]:
    """
    Get list of all supported file formats.
    
    Returns:
        List of supported file extensions
        
    Example:
        >>> from documents_to_markdown import get_supported_formats
        >>> formats = get_supported_formats()
        >>> print(f"Supported: {', '.join(formats)}")
    """
    converter = DocumentConverter()
    return converter.get_supported_formats()
