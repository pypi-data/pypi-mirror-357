# OLLAMA Setup Guide for DocumentsToMarkdown

This guide explains how to set up and use OLLAMA (local AI) with the DocumentsToMarkdown converter for image-to-text conversion.

## What is OLLAMA?

OLLAMA is a local AI inference server that allows you to run large language models on your own machine. This provides:

- **Privacy**: Your images never leave your computer
- **Cost**: No API fees after initial setup
- **Speed**: No network latency (after model loading)
- **Offline**: Works without internet connection

## Prerequisites

- **System Requirements**: 
  - At least 8GB RAM (16GB+ recommended for better performance)
  - Modern CPU (Apple Silicon, Intel, or AMD)
  - Optional: NVIDIA GPU with CUDA support for faster inference

## Installation Steps

### 1. Install OLLAMA

#### Windows
```bash
# Download and install from: https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama
```

#### macOS
```bash
# Download from: https://ollama.ai/download
# Or use Homebrew:
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Start OLLAMA Server

```bash
# Start the OLLAMA server (runs on http://localhost:11434 by default)
ollama serve
```

Keep this terminal open - OLLAMA needs to be running for the DocumentsToMarkdown converter to work.

### 3. Install Vision Model

```bash
# Install LLaVA model for vision tasks (this will download ~4GB)
ollama pull llava:latest

# Alternative: Install a smaller model (if you have limited resources)
ollama pull llava:7b

# Alternative: Install a larger, more capable model (if you have 16GB+ RAM)
ollama pull llava:13b
```

### 4. Verify Installation

```bash
# List installed models
ollama list

# Test the model with a simple prompt
ollama run llava:latest "Hello, can you see images?"
```

## Configuration

### 1. Update Environment Variables

Copy `.env.template` to `.env` and configure:

```bash
# AI Service Selection
AI_SERVICE=ollama

# OLLAMA Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:latest
OLLAMA_TIMEOUT=120
OLLAMA_TEMPERATURE=0.1
```

### 2. Test the Setup

```python
from services.ai_services import ai_service_factory

# Test OLLAMA availability
try:
    service = ai_service_factory.create_service('ollama')
    print(f"✅ OLLAMA service available: {service.get_model_name()}")
except Exception as e:
    print(f"❌ OLLAMA not available: {e}")
```

## Usage Examples

### Basic Image Conversion

```python
from services.image_converter import ImageDocumentConverter

# Create converter with OLLAMA
converter = ImageDocumentConverter(ai_service_type='ollama')

# Convert an image
result = converter.convert_document('path/to/image.jpg')
print(result)
```

### Auto-Detection (Prefers OLLAMA)

```python
from services.image_converter import ImageDocumentConverter

# Auto-detect AI service (will use OLLAMA if available)
converter = ImageDocumentConverter()

# Convert an image
result = converter.convert_document('path/to/image.jpg')
print(result)
```

## Performance Tips

### 1. Model Selection

- **llava:7b**: Fastest, good for simple images
- **llava:latest** (13b): Balanced performance and quality
- **llava:34b**: Best quality, requires 32GB+ RAM

### 2. Hardware Optimization

```bash
# For NVIDIA GPU users, install CUDA support
# This can significantly speed up inference
# Follow OLLAMA's GPU setup guide: https://ollama.ai/blog/nvidia-gpu-support
```

### 3. Memory Management

```bash
# If you run out of memory, try a smaller model
ollama pull llava:7b

# Or adjust the context window
export OLLAMA_NUM_CTX=2048
```

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to OLLAMA server"
```bash
# Make sure OLLAMA is running
ollama serve

# Check if the service is accessible
curl http://localhost:11434/api/tags
```

#### 2. "Model not found"
```bash
# Install the required model
ollama pull llava:latest

# Verify it's installed
ollama list
```

#### 3. "Request timeout"
```bash
# Increase timeout in .env
OLLAMA_TIMEOUT=300

# Or use a smaller model
OLLAMA_MODEL=llava:7b
```

#### 4. Out of Memory
```bash
# Use a smaller model
ollama pull llava:7b

# Or close other applications to free up RAM
```

### Performance Issues

#### Slow Response Times
- Use a smaller model (llava:7b)
- Ensure OLLAMA has enough RAM allocated
- Consider using GPU acceleration if available

#### Poor Quality Results
- Use a larger model (llava:13b or llava:34b)
- Adjust temperature settings
- Ensure images are clear and high-resolution

## Comparison: OLLAMA vs OpenAI

| Feature | OLLAMA (Local) | OpenAI (Cloud) |
|---------|----------------|----------------|
| **Privacy** | ✅ Complete | ❌ Data sent to OpenAI |
| **Cost** | ✅ Free after setup | ❌ Pay per API call |
| **Speed** | ⚠️ Depends on hardware | ✅ Generally fast |
| **Quality** | ⚠️ Model dependent | ✅ Consistently high |
| **Setup** | ❌ Requires installation | ✅ Just API key |
| **Offline** | ✅ Works offline | ❌ Requires internet |

## Next Steps

1. **Test with Sample Images**: Try converting different types of images to see quality
2. **Optimize Settings**: Adjust model and parameters based on your needs
3. **Monitor Performance**: Check memory usage and response times
4. **Fallback Setup**: Configure OpenAI as backup for critical workflows

For more advanced configuration options, see the [AI Services Documentation](AI_SERVICES.md).
