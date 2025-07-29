# Documents to Markdown Converter

A comprehensive Python library for converting various document types to Markdown format with AI-powered image extraction and processing capabilities.

[![PyPI version](https://badge.fury.io/py/documents-to-markdown.svg)](https://badge.fury.io/py/documents-to-markdown)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install documents-to-markdown

# Or install from source
git clone https://github.com/ChaosAIs/DocumentsToMarkdown.git
cd DocumentsToMarkdown
pip install -e .
```

### Library Usage

```python
from documents_to_markdown import DocumentConverter

# Initialize converter
converter = DocumentConverter()

# Convert a single file
success = converter.convert_file("document.docx", "output.md")
print(f"Conversion successful: {success}")

# Convert all files in a folder
results = converter.convert_all("input_folder", "output_folder")
print(f"Converted {results['successful_conversions']} files")
```

### Command Line Usage

```bash
# Convert all files in input folder
documents-to-markdown

# Convert specific file
documents-to-markdown --file document.docx output.md

# Custom input/output folders
documents-to-markdown --input docs --output markdown

# Show help
documents-to-markdown --help
```

## 📋 Supported Formats

- **Word Documents**: `.docx`, `.doc`
- **PDF Documents**: `.pdf`
- **Excel Spreadsheets**: `.xlsx`, `.xlsm`, `.xls`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff` (AI-powered)
- **Plain Text**: `.txt`, `.csv`, `.tsv`, `.log` (AI-enhanced)

## ✨ Features

### Core Capabilities
- **Multi-format support**: Word, PDF, Excel, Plain Text, and Image documents
- **AI-powered processing**: Choose between OpenAI (cloud) and OLLAMA (local)
- **Batch processing**: Convert multiple documents efficiently
- **Preserves formatting**: Bold, italic, tables, and document structure
- **Automatic section numbering**: Hierarchical numbering (1, 1.1, 1.2, etc.)
- **Modular architecture**: Extensible converter system

### AI-Enhanced Features
- **Image text extraction**: Extract text from images using AI vision
- **Embedded image processing**: Process images within Word/PDF documents
- **Flowchart conversion**: Convert flowcharts to ASCII diagrams
- **Smart text processing**: AI-enhanced plain text formatting
- **Privacy options**: Local AI processing with OLLAMA

## 📚 Library API

### Basic Usage

```python
from documents_to_markdown import DocumentConverter

# Initialize converter
converter = DocumentConverter(
    add_section_numbers=True,  # Enable section numbering
    verbose=False              # Enable verbose logging
)

# Convert single file
success = converter.convert_file("input.docx", "output.md")

# Convert all files in folder
results = converter.convert_all("input_folder", "output_folder")

# Check supported formats
formats = converter.get_supported_formats()
print(f"Supported: {formats}")

# Check if file can be converted
if converter.can_convert("document.pdf"):
    print("File can be converted!")
```

### Advanced Usage

```python
from documents_to_markdown import DocumentConverter, convert_document, convert_folder

# Quick single file conversion
success = convert_document("report.docx", "report.md")

# Quick folder conversion
results = convert_folder("documents", "markdown_output")

# Advanced converter configuration
converter = DocumentConverter()
converter.set_section_numbering(False)  # Disable numbering
converter.set_verbose_logging(True)     # Enable debug output

# Get detailed statistics
stats = converter.get_conversion_statistics()
print(f"Available converters: {stats['total_converters']}")
for conv in stats['converters']:
    print(f"- {conv['name']}: {', '.join(conv['supported_extensions'])}")
```

### Working with Results

```python
# Convert folder and handle results
results = converter.convert_all("input", "output")

print(f"Total files: {results['total_files']}")
print(f"Successful: {results['successful_conversions']}")
print(f"Failed: {results['failed_conversions']}")

# Process individual results
for result in results['results']:
    status = "✓" if result['status'] == 'success' else "✗"
    print(f"{status} {result['file']} ({result['converter']})")
```

## 🖥️ Command Line Interface

### Installation

After installing the package, you can use the command-line interface:

```bash
# Install the package
pip install documents-to-markdown

# Now you can use the CLI commands
documents-to-markdown --help
doc2md --help  # Alternative shorter command
```

### Basic Commands

```bash
# Convert all files in current input folder
documents-to-markdown

# Convert all files with custom folders
documents-to-markdown --input docs --output markdown

# Convert a single file
documents-to-markdown --file document.docx output.md

# Show converter statistics
documents-to-markdown --stats

# Disable section numbering
documents-to-markdown --no-numbering

# Enable verbose output
documents-to-markdown --verbose
```

### Command Options

```bash
documents-to-markdown [OPTIONS]

Options:
  -i, --input FOLDER     Input folder (default: input)
  -o, --output FOLDER    Output folder (default: output)
  -f, --file INPUT OUTPUT Convert single file
  --no-numbering         Disable section numbering
  --stats               Show converter statistics
  -v, --verbose         Enable verbose logging
  --version             Show version
  --help                Show help message
```

## 🤖 AI Configuration (Optional)

For enhanced image processing and text analysis, you can configure AI services:

### Option 1: OLLAMA (Local AI) - Recommended for Privacy

```bash
# Install OLLAMA (see https://ollama.ai)
ollama serve
ollama pull llava:latest

# Create .env file
echo "AI_SERVICE=ollama" > .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
echo "OLLAMA_MODEL=llava:latest" >> .env
```

**Benefits:**
- ✅ **Free**: No API costs
- ✅ **Private**: Data never leaves your computer
- ✅ **Offline**: Works without internet

### Option 2: OpenAI (Cloud AI) - Recommended for Ease

```bash
# Get API key from https://platform.openai.com/api-keys
# Create .env file
echo "AI_SERVICE=openai" > .env
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

**Benefits:**
- ✅ **Easy Setup**: Just need API key
- ✅ **High Quality**: Consistently good results
- ❌ **Costs Money**: Pay per API call

### Auto-Detection (Recommended)

```bash
# Configure both services - system will choose best available
cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest
OPENAI_API_KEY=your_api_key_here
EOF
```

### Advanced Configuration

```bash
# Complete .env configuration
AI_SERVICE=ollama|openai          # Specific service or leave empty for auto-detection

# OpenAI Settings
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1

# OLLAMA Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest
OLLAMA_TIMEOUT=120

# Image Processing
IMAGE_MAX_SIZE_MB=20
IMAGE_QUALITY_COMPRESSION=85
IMAGE_MAX_SIZE_PIXELS=2048

# Logging
LOG_LEVEL=INFO
```

## 📖 Examples

### Converting Different File Types

```python
from documents_to_markdown import DocumentConverter

converter = DocumentConverter()

# Word document
converter.convert_file("report.docx", "report.md")

# PDF document
converter.convert_file("manual.pdf", "manual.md")

# Excel spreadsheet
converter.convert_file("data.xlsx", "data.md")

# Image with text (requires AI setup)
converter.convert_file("screenshot.png", "screenshot.md")

# Plain text/CSV
converter.convert_file("data.csv", "data.md")
```

### Batch Processing

```python
from documents_to_markdown import convert_folder

# Convert entire folder
results = convert_folder("documents", "markdown_output")

print(f"✅ Converted: {results['successful_conversions']}")
print(f"❌ Failed: {results['failed_conversions']}")

# Process results
for result in results['results']:
    if result['status'] == 'success':
        print(f"✓ {result['file']} -> Converted with {result['converter']}")
    else:
        print(f"✗ {result['file']} -> Failed")
```

### Custom Configuration

```python
from documents_to_markdown import DocumentConverter

# Initialize with custom settings
converter = DocumentConverter(
    add_section_numbers=False,  # Disable numbering
    verbose=True               # Enable debug logging
)

# Check what formats are supported
formats = converter.get_supported_formats()
print(f"Supported formats: {', '.join(formats)}")

# Get detailed converter information
stats = converter.get_conversion_statistics()
for conv_info in stats['converters']:
    name = conv_info['name']
    exts = ', '.join(conv_info['supported_extensions'])
    print(f"{name}: {exts}")
```

## 🏗️ Architecture

### Library Structure

```
documents_to_markdown/
├── __init__.py              # Main package exports
├── api.py                   # Public API interface
├── cli.py                   # Command-line interface
└── services/                # Core conversion services
    ├── document_converter_manager.py  # Main orchestrator
    ├── base_converter.py             # Abstract base converter
    ├── word_converter.py             # Word document converter
    ├── pdf_converter.py              # PDF document converter
    ├── excel_converter.py            # Excel spreadsheet converter
    ├── image_converter.py            # Image converter (AI-powered)
    ├── plain_text_converter.py       # Text/CSV converter (AI-enhanced)
    ├── text_chunking_utils.py        # Text processing utilities
    └── ai_services/                  # AI service abstraction
        ├── base_ai_service.py        # AI service interface
        ├── openai_service.py         # OpenAI implementation
        ├── ollama_service.py         # OLLAMA implementation
        └── ai_service_factory.py     # Service factory
```

### Converter Architecture

- **DocumentConverter**: Main public API class
- **DocumentConverterManager**: Orchestrates multiple converters
- **BaseDocumentConverter**: Abstract base for all converters
- **Specialized Converters**: Word, PDF, Excel, Image, PlainText
- **AI Services**: Pluggable AI backends (OpenAI, OLLAMA)

### Extensibility

The modular design makes it easy to:
- Add new document formats
- Integrate additional AI services
- Customize conversion behavior
- Extend processing capabilities

```python
# Example: Custom converter
from documents_to_markdown.services.base_converter import BaseDocumentConverter

class MyCustomConverter(BaseDocumentConverter):
    def get_supported_extensions(self):
        return ['.custom']

    def can_convert(self, file_path):
        return file_path.suffix.lower() == '.custom'

    def _convert_document_to_markdown(self, doc_path):
        # Your conversion logic here
        return "# Converted Content\n\nCustom format converted!"

# Add to converter manager
from documents_to_markdown import DocumentConverter
converter = DocumentConverter()
converter._get_manager().add_converter(MyCustomConverter())
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/ChaosAIs/DocumentsToMarkdown.git
cd DocumentsToMarkdown

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run specific tests
python test_converter.py
python test_ai_services.py
```

### Running Tests

```bash
# Test basic conversion
python test_converter.py

# Test AI services
python test_ai_services.py

# Test image conversion
python test_image_converter.py

# Test flowchart conversion
python test_flowchart_conversion.py
```

### Building and Publishing

```bash
# Build the package
python -m build

# Install locally for testing
pip install dist/documents_to_markdown-1.0.0-py3-none-any.whl

# Publish to PyPI (maintainers only)
python -m twine upload dist/*
```

## 📋 Output Examples

### Word Document Conversion
Input Word document with formatting:
```markdown
# 1. Project Report

Some **bold text** and *italic text*

## 1.1 Data Summary

| Header 1 | Header 2 | Header 3 |
| --- | --- | --- |
| Data 1 | Data 2 | Data 3 |
| Data 4 | Data 5 | Data 6 |
```

### CSV to Markdown Table
Input CSV:
```csv
Employee ID,Name,Department,Salary
001,Alice Johnson,Engineering,75000
002,Bob Smith,Marketing,65000
```

Output:
```markdown
| Employee ID | Name         | Department  | Salary |
|:-----------:|:-------------|:------------|-------:|
| 001         | Alice Johnson| Engineering |  75000 |
| 002         | Bob Smith    | Marketing   |  65000 |
```

### AI-Enhanced Image Processing
Images containing flowcharts are automatically converted to ASCII diagrams:
```markdown
┌─────────────┐
│    Start    │
└──────┬──────┘
       ↓
┌─────────────┐
│  Process A  │
└──────┬──────┘
       ↓
┌─────────────┐
│     End     │
└─────────────┘
```

## 🔧 Troubleshooting

### Common Issues

**Installation Problems:**
```bash
# Missing dependencies
pip install documents-to-markdown

# Development installation
git clone https://github.com/ChaosAIs/DocumentsToMarkdown.git
cd DocumentsToMarkdown
pip install -e .
```

**AI Service Issues:**
```bash
# Test AI services
python -c "from documents_to_markdown.services.ai_services import ai_service_factory; print('AI services available:', ai_service_factory.get_available_services())"

# OLLAMA not running
ollama serve
ollama pull llava:latest

# OpenAI API key issues
echo "OPENAI_API_KEY=your_key_here" > .env
```

**File Processing Issues:**
- Ensure files are in supported formats
- Check file permissions and paths
- Review logs for detailed error messages

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `pytest` or `python test_converter.py`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **python-docx** for Word document processing
- **PyMuPDF** for PDF handling
- **OpenAI** for AI vision capabilities
- **OLLAMA** for local AI processing
- **openpyxl** for Excel support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ChaosAIs/DocumentsToMarkdown/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ChaosAIs/DocumentsToMarkdown/discussions)
- **Documentation**: [Project Wiki](https://github.com/ChaosAIs/DocumentsToMarkdown/wiki)

---

**Made with ❤️ by [Felix](https://github.com/ChaosAIs)**
