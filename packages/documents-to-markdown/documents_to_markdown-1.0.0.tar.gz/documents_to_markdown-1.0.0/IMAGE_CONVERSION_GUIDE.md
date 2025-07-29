# Image to Markdown Conversion Guide

## AI Service Options

The DocumentsToMarkdown converter supports two AI services for image-to-text conversion:

### Option 1: OLLAMA (Local AI) - **Recommended for Privacy**
- ✅ **Free**: No API costs after setup
- ✅ **Private**: Images never leave your computer
- ✅ **Offline**: Works without internet
- ⚠️ **Setup Required**: Needs local installation

### Option 2: OpenAI (Cloud AI) - **Recommended for Ease of Use**
- ✅ **Easy Setup**: Just need API key
- ✅ **High Quality**: Consistently good results
- ❌ **Costs Money**: Pay per API call
- ❌ **Privacy**: Images sent to OpenAI

## Setup Instructions

### Quick Start (Auto-Detection)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Choose Your AI Service**:
   - **For OLLAMA**: Follow the [OLLAMA Setup Guide](OLLAMA_SETUP_GUIDE.md)
   - **For OpenAI**: Get API key from https://platform.openai.com/api-keys

3. **Configure Environment**:
   - Copy `.env.template` to `.env`
   - Add your configuration (see examples below)

4. **Add Image Files**:
   - Place your image files in the `input` folder
   - Supported formats: JPG, PNG, GIF, BMP, TIFF, WebP

5. **Run Conversion**:
   ```bash
   python document_converter_v2.py
   ```

### Configuration Examples

#### OLLAMA Configuration (Local AI)
```bash
# .env file
AI_SERVICE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest
```

#### OpenAI Configuration (Cloud AI)
```bash
# .env file
AI_SERVICE=openai
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4o
```

#### Auto-Detection (Tries OLLAMA first, then OpenAI)
```bash
# .env file - leave AI_SERVICE empty for auto-detection
# Configure both services, system will use the first available one
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest
OPENAI_API_KEY=your_actual_api_key_here
```

## Example Usage

### Basic Usage (Auto-Detection)
```python
from services.document_converter_manager import DocumentConverterManager

# Initialize converter manager (auto-detects best AI service)
manager = DocumentConverterManager()

# Convert all documents (including images)
results = manager.convert_all()

print(f"Converted {results['successful_conversions']} files")
```

### Specific AI Service
```python
from services.image_converter import ImageDocumentConverter

# Force OLLAMA (local AI)
converter = ImageDocumentConverter(ai_service_type='ollama')
result = converter.convert_document('path/to/image.jpg')

# Force OpenAI (cloud AI)
converter = ImageDocumentConverter(ai_service_type='openai')
result = converter.convert_document('path/to/image.jpg')
```

### Check AI Service Status
```python
from services.ai_services import ai_service_factory

# Check which services are available
status = ai_service_factory.list_available_services()
print(f"OLLAMA available: {status['ollama']}")
print(f"OpenAI available: {status['openai']}")
```

## Features

- **Multiple AI Services**: Choose between local (OLLAMA) and cloud (OpenAI) AI
- **Auto-Detection**: Automatically selects the best available AI service
- **Smart Formatting**: Preserves document structure and formatting
- **Multiple Formats**: Supports all common image formats
- **Automatic Optimization**: Resizes large images for optimal processing
- **Batch Processing**: Convert multiple images at once
- **Privacy Options**: Keep data local with OLLAMA or use cloud with OpenAI

## Tips for Best Results

1. **High Quality Images**: Use clear, high-resolution images
2. **Good Lighting**: Ensure text is clearly visible
3. **Proper Orientation**: Make sure images are right-side up
4. **Clean Background**: Avoid cluttered backgrounds around text
5. **Standard Fonts**: Common fonts work better than decorative ones
6. **Choose Right AI Service**:
   - Use **OLLAMA** for privacy-sensitive content
   - Use **OpenAI** for highest quality results

## Troubleshooting

### General Issues
- **Large Images**: Images are automatically resized if too large
- **Poor Quality**: Try enhancing image quality before conversion
- **Complex Layouts**: Simple layouts work better than complex designs

### OLLAMA Issues
- **"Cannot connect to OLLAMA server"**: Make sure OLLAMA is running (`ollama serve`)
- **"Model not found"**: Install the model (`ollama pull llava:latest`)
- **Slow performance**: Use a smaller model (`ollama pull llava:7b`)
- **Out of memory**: Close other applications or use smaller model

### OpenAI Issues
- **API Key Issues**: Make sure your OpenAI API key is valid and has credits
- **Rate limits**: Wait a moment and try again
- **Network errors**: Check your internet connection

### Getting Help
- **OLLAMA Setup**: See [OLLAMA Setup Guide](OLLAMA_SETUP_GUIDE.md)
- **AI Services**: See [AI Services Documentation](AI_SERVICES.md)
- **General Issues**: Check the main project README
