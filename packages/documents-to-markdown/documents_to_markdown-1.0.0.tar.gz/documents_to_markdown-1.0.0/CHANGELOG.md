# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-21

### Added
- Initial release of Documents to Markdown Converter
- Support for Word documents (.docx, .doc)
- Support for PDF documents (.pdf)
- Support for Excel spreadsheets (.xlsx, .xlsm, .xls)
- Support for image files (.png, .jpg, .jpeg, .gif, .bmp, .tiff) with AI-powered text extraction
- Support for plain text files (.txt, .csv, .tsv, .log) with AI-enhanced formatting
- AI integration with OpenAI and OLLAMA services
- Automatic section numbering for headings
- Batch processing capabilities
- Command-line interface with multiple options
- Library API for programmatic usage
- Modular architecture with pluggable converters
- Comprehensive error handling and logging
- Image content extraction from embedded images in Word and PDF documents
- Flowchart detection and ASCII conversion
- Text chunking for large documents
- Auto-detection of AI services
- Privacy-focused local AI processing option (OLLAMA)

### Features
- **Multi-format Support**: Convert Word, PDF, Excel, Image, and Plain Text files
- **AI-Powered Processing**: Choose between OpenAI (cloud) and OLLAMA (local) AI services
- **Dual Usage**: Use as a Python library or command-line tool
- **Section Numbering**: Automatic hierarchical numbering (1, 1.1, 1.2, etc.)
- **Batch Processing**: Convert multiple documents efficiently
- **Image Processing**: Extract text from images and embedded images
- **Smart Formatting**: AI-enhanced text structure and formatting
- **Privacy Options**: Local AI processing to keep data private
- **Extensible Architecture**: Easy to add new document formats and AI services

### CLI Commands
- `documents-to-markdown`: Main command for document conversion
- `doc2md`: Alternative shorter command
- Support for custom input/output folders
- Single file conversion option
- Statistics and help commands
- Verbose logging option

### Library API
- `DocumentConverter`: Main API class
- `convert_document()`: Quick single file conversion
- `convert_folder()`: Quick folder conversion
- `get_supported_formats()`: List supported file formats
- Individual converter classes for advanced usage
- Comprehensive error handling and result reporting

### Dependencies
- python-docx>=1.2.0: Word document processing
- PyMuPDF>=1.24.14: PDF document processing
- openpyxl>=3.1.2: Excel document processing
- xlrd>=2.0.1: Legacy Excel support
- python-dotenv>=1.0.0: Environment configuration
- openai>=1.51.0: OpenAI AI services
- Pillow>=10.4.0: Image processing
- requests>=2.32.3: HTTP requests for AI services

### Documentation
- Comprehensive README with installation and usage examples
- AI services setup guides (OpenAI and OLLAMA)
- Image conversion and integration documentation
- Plain text converter guide with AI enhancement details
- Architecture documentation and extension guides

### Package Distribution
- Pip-installable Python package
- Proper package structure with setup.py and pyproject.toml
- MIT License for open-source distribution
- Entry points for global CLI access
- Automatic dependency management
