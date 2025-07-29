# AI Services Documentation

The DocumentsToMarkdown converter supports multiple AI services for image-to-text conversion. This document explains the architecture and configuration options.

## Supported AI Services

### 1. OpenAI (Cloud-based)
- **Models**: GPT-4 Vision (gpt-4o, gpt-4-vision-preview)
- **Pros**: High quality, fast, reliable
- **Cons**: Requires API key, costs money, data sent to OpenAI
- **Best for**: Production use, highest quality results

### 2. OLLAMA (Local)
- **Models**: LLaVA variants (llava:latest, llava:7b, llava:13b, llava:34b)
- **Pros**: Free, private, offline capable
- **Cons**: Requires local setup, hardware dependent
- **Best for**: Privacy-sensitive data, cost-conscious users

## Architecture

The AI service system uses a pluggable architecture:

```
ImageDocumentConverter
    ↓
AIServiceFactory
    ↓
BaseAIService (Interface)
    ↓
├── OpenAIService
└── OllamaService
```

### Key Components

1. **BaseAIService**: Abstract interface defining common methods
2. **AIServiceFactory**: Creates and manages service instances
3. **Service Implementations**: OpenAI and OLLAMA specific implementations
4. **Auto-detection**: Automatically selects best available service

## Configuration

### Environment Variables

```bash
# Service Selection
AI_SERVICE=ollama|openai  # Optional: auto-detect if not set

# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional

# OLLAMA Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest
OLLAMA_TIMEOUT=120
OLLAMA_TEMPERATURE=0.1

# Image Processing
IMAGE_MAX_SIZE_PIXELS=2048
IMAGE_QUALITY_COMPRESSION=85
```

### Service Selection Priority

1. **Explicit**: If `AI_SERVICE` is set, use that service
2. **Auto-detect**: Try OLLAMA first (local preference), then OpenAI
3. **Fallback**: Default to OpenAI if nothing else works

## Usage Examples

### Basic Usage (Auto-detection)

```python
from services.image_converter import ImageDocumentConverter

# Auto-detect best available service
converter = ImageDocumentConverter()
result = converter.convert_document('image.jpg')
```

### Explicit Service Selection

```python
from services.image_converter import ImageDocumentConverter

# Force OpenAI
converter = ImageDocumentConverter(ai_service_type='openai')

# Force OLLAMA
converter = ImageDocumentConverter(ai_service_type='ollama')
```

### Service Factory Usage

```python
from services.ai_services import ai_service_factory

# Create specific service
service = ai_service_factory.create_service('ollama')

# Check availability
available = ai_service_factory.list_available_services()
print(available)  # {'openai': True, 'ollama': False}

# Extract text from image
result = service.extract_text_from_image(image_path, prompt)
```

### Error Handling

```python
from services.ai_services import AIServiceUnavailableError

try:
    converter = ImageDocumentConverter(ai_service_type='ollama')
    result = converter.convert_document('image.jpg')
except AIServiceUnavailableError as e:
    print(f"AI service not available: {e}")
    # Fallback to different service or manual processing
```

## Adding New AI Services

To add support for a new AI service:

### 1. Create Service Implementation

```python
from services.ai_services.base_ai_service import BaseAIService

class MyAIService(BaseAIService):
    def is_available(self) -> bool:
        # Check if service is configured and accessible
        pass
    
    def extract_text_from_image(self, image_path: Path, prompt: str) -> str:
        # Implement image-to-text conversion
        pass
    
    def get_service_name(self) -> str:
        return "MyAI"
    
    def get_model_name(self) -> str:
        return self.config.get('model', 'default-model')
```

### 2. Register in Factory

```python
# In ai_service_factory.py
from .my_ai_service import MyAIService

class AIServiceFactory:
    def __init__(self):
        self._services = {
            'openai': OpenAIService,
            'ollama': OllamaService,
            'myai': MyAIService,  # Add new service
        }
```

### 3. Add Configuration

```python
# In _get_service_config method
elif service_type == 'myai':
    return {
        'api_key': os.getenv('MYAI_API_KEY'),
        'model': os.getenv('MYAI_MODEL', 'default'),
        # ... other config
    }
```

## Performance Considerations

### OpenAI
- **Latency**: ~2-5 seconds per image
- **Rate Limits**: Varies by plan (typically 500 requests/minute)
- **Cost**: ~$0.01-0.03 per image depending on size and model

### OLLAMA
- **Latency**: 10-60 seconds per image (hardware dependent)
- **Memory**: 4-32GB RAM depending on model
- **Throughput**: 1 image at a time (no parallel processing)

### Optimization Tips

1. **Image Preprocessing**: Resize images to optimal size (1024x1024)
2. **Model Selection**: Choose appropriate model for quality vs speed
3. **Caching**: Consider caching results for repeated conversions
4. **Batch Processing**: Process multiple images in sequence

## Troubleshooting

### Common Issues

#### Service Not Available
```python
# Check service status
from services.ai_services import ai_service_factory

status = ai_service_factory.list_available_services()
print(f"OpenAI: {status['openai']}")
print(f"OLLAMA: {status['ollama']}")
```

#### Configuration Problems
```bash
# Verify environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('AI_SERVICE:', os.getenv('AI_SERVICE'))
print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
print('OLLAMA_BASE_URL:', os.getenv('OLLAMA_BASE_URL'))
"
```

#### Performance Issues
- **Slow responses**: Use smaller models or increase timeouts
- **Out of memory**: Reduce image size or use smaller models
- **Poor quality**: Use larger models or adjust temperature

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all AI service operations will be logged
converter = ImageDocumentConverter()
```

## Security Considerations

### OpenAI
- Images are sent to OpenAI servers
- Data may be used for model training (unless opted out)
- Use OpenAI's data usage controls for sensitive content

### OLLAMA
- All processing happens locally
- No data leaves your machine
- Suitable for confidential documents

### Best Practices
1. **Sensitive Data**: Use OLLAMA for confidential content
2. **API Keys**: Store in environment variables, never in code
3. **Rate Limiting**: Implement backoff for API services
4. **Error Handling**: Don't expose API keys in error messages

## Future Enhancements

Planned features:
- **Azure Cognitive Services** support
- **Google Vision API** integration
- **Anthropic Claude Vision** support
- **Parallel processing** for batch operations
- **Result caching** system
- **Custom model fine-tuning** support
