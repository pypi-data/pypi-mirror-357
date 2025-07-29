# Plain Text to Markdown Converter Guide

This guide explains how to use the new Plain Text to Markdown converter feature that handles various plain text file formats including CSV, TSV, TXT, LOG, and other text-based files.

## Overview

The PlainTextConverter is a new service that converts plain text files to well-structured markdown format. It provides:

- **CSV/TSV to Table Conversion**: Automatically converts CSV and TSV files to properly formatted markdown tables
- **AI-Enhanced Text Analysis**: Uses AI services (OpenAI/OLLAMA) to improve text structure and readability when available
- **Fallback Processing**: Provides basic text-to-markdown conversion when AI services are not available
- **Multiple Format Support**: Handles .txt, .csv, .tsv, .log, .md, .text files

## Features

### CSV/TSV Table Conversion
- Automatically detects CSV and TSV formats
- Creates properly formatted markdown tables with headers
- Handles different delimiters (comma for CSV, tab for TSV)
- Maintains data integrity and structure

### AI-Enhanced Text Analysis
When AI services are enabled, the converter:
- Analyzes text content and suggests better structure
- Adds appropriate headings and sections
- Improves readability and organization
- Preserves all original information
- Creates summaries when appropriate

### Fallback Text Processing
When AI is not available:
- Converts plain text to basic markdown format
- Identifies potential headings based on formatting patterns
- Maintains paragraph structure
- Wraps content in code blocks when needed

## Supported File Types

| Extension | Description | Processing Method |
|-----------|-------------|-------------------|
| `.csv` | Comma-separated values | Table conversion with AI enhancement |
| `.tsv` | Tab-separated values | Table conversion with AI enhancement |
| `.txt` | Plain text files | AI analysis or basic formatting |
| `.log` | Log files | AI analysis for structured output |
| `.md` | Markdown files | AI analysis for improvement |
| `.text` | Text files | AI analysis or basic formatting |

## Configuration

### AI Service Setup

The converter uses the same AI configuration as the image converter. Set up your environment variables:

```bash
# For OpenAI (recommended)
AI_SERVICE=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o

# For OLLAMA (local AI)
AI_SERVICE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest

# Auto-detection (tries OLLAMA first, then OpenAI)
# Leave AI_SERVICE empty for auto-detection
```

### Environment Variables

```bash
# AI Service Selection (optional)
AI_SERVICE=openai  # or 'ollama' or leave empty for auto-detection

# OpenAI Configuration
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1

# OLLAMA Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest
OLLAMA_TIMEOUT=120
OLLAMA_TEMPERATURE=0.1
```

## Usage Examples

### Using DocumentConverterManager (Recommended)

```python
from services.document_converter_manager import DocumentConverterManager

# Initialize converter manager
manager = DocumentConverterManager()

# Convert all files in input directory
results = manager.convert_all()
print(f"Converted {results['successful_conversions']} files")

# Convert a specific file
input_file = Path("data.csv")
success = manager.convert_file(input_file)
```

### Using PlainTextConverter Directly

```python
from services.plain_text_converter import PlainTextConverter

# Initialize converter (auto-detects AI service)
converter = PlainTextConverter()

# Convert a file
input_file = Path("report.txt")
output_file = Path("report.md")
success = converter.convert_file(input_file, output_file)

# Check converter capabilities
info = converter.get_converter_info()
print(f"AI enabled: {info['ai_enabled']}")
print(f"Supported extensions: {info['supported_extensions']}")
```

### Forcing Specific AI Service

```python
# Force OpenAI
converter = PlainTextConverter(ai_service_type='openai')

# Force OLLAMA
converter = PlainTextConverter(ai_service_type='ollama')

# Auto-detection (default)
converter = PlainTextConverter()
```

## Example Conversions

### CSV to Markdown Table

**Input (employees.csv):**
```csv
Name,Department,Salary
John Doe,Engineering,75000
Jane Smith,Marketing,65000
```

**Output (employees.md):**
```markdown
# Employee Information

| Name      | Department  | Salary |
|:----------|:------------|-------:|
| John Doe  | Engineering | 75,000 |
| Jane Smith| Marketing   | 65,000 |
```

### Plain Text to Structured Markdown

**Input (report.txt):**
```
Project Status Report

The project is on track. Key achievements include completing the design phase.

Next Steps
- Begin implementation
- Set up testing environment
```

**Output (report.md):**
```markdown
# Project Status Report

## Executive Summary
The project is on track. Key achievements include completing the design phase.

## Next Steps
- Begin implementation
- Set up testing environment
```

## Testing

Run the test suite to verify functionality:

```bash
# Test the converter functionality
python test_plain_text_converter.py

# Test integration with DocumentConverterManager
python test_plain_text_integration.py

# Run the demo
python demo_plain_text_converter.py
```

## Error Handling

The converter handles various error conditions gracefully:

- **Empty files**: Creates a markdown file indicating the file is empty
- **Invalid CSV**: Falls back to plain text processing
- **AI service unavailable**: Uses fallback text processing
- **File read errors**: Returns error message in markdown format
- **Encoding issues**: Attempts UTF-8 decoding with error handling

## Performance Considerations

- **AI Processing**: AI analysis adds processing time but significantly improves output quality
- **Large Files**: Very large files may hit AI service token limits
- **Batch Processing**: Use DocumentConverterManager for efficient batch processing
- **Local AI**: OLLAMA provides privacy but may be slower than cloud APIs

## Troubleshooting

### AI Service Not Available
```
AI enabled: False
Using fallback text processing
```
**Solution**: Check your AI service configuration and API keys.

### CSV Not Detected as Table
**Issue**: CSV file processed as plain text instead of table.
**Solution**: Ensure proper CSV format with consistent delimiters.

### Poor Text Structure
**Issue**: AI analysis doesn't improve text structure significantly.
**Solution**: The original text may already be well-structured, or try a different AI model.

## Integration

The PlainTextConverter is automatically integrated with:
- **DocumentConverterManager**: Handles plain text files in batch operations
- **AI Services**: Uses the same AI infrastructure as image conversion
- **Logging System**: Provides detailed conversion logs
- **Error Handling**: Consistent error handling across all converters

## Future Enhancements

Planned improvements include:
- Support for additional delimited formats (pipe-separated, etc.)
- Custom AI prompts for specific text types
- Batch processing optimizations
- Advanced table formatting options
- Integration with more AI services
