# 📦 Pip Installation Guide - Documents to Markdown

This guide covers everything users need to know when installing and configuring the package via pip.

## 🚀 Quick Installation

```bash
pip install documents-to-markdown
```

That's it! The package is now installed and ready to use.

## 🎯 First-Time Setup

### Automatic Setup Wizard

When you first run the package, it will automatically detect that it's a new installation and offer to run a setup wizard:

```bash
# First time running any command will trigger setup
documents-to-markdown --help

# Or run setup explicitly
documents-to-markdown --config init
```

The setup wizard will:
1. ✅ **Check for available AI services** (OLLAMA, OpenAI)
2. ✅ **Guide you through AI service configuration**
3. ✅ **Set up general preferences** (section numbering, logging)
4. ✅ **Create configuration files** automatically
5. ✅ **Validate your settings**

### Manual Configuration

If you prefer manual setup:

```bash
# Show current configuration
documents-to-markdown --config show

# Set specific values
documents-to-markdown --config set ai_service openai
documents-to-markdown --config set openai.api_key your_key_here
documents-to-markdown --config set add_section_numbers true

# Validate configuration
documents-to-markdown --config validate
```

## 🤖 AI Services Setup

### Option 1: OLLAMA (Local AI - Recommended for Privacy)

**Benefits:**
- ✅ **Free** - No API costs
- ✅ **Private** - Data never leaves your computer
- ✅ **Offline** - Works without internet

**Setup:**
```bash
# 1. Install OLLAMA
# Download from: https://ollama.ai

# 2. Start OLLAMA service
ollama serve

# 3. Install vision model
ollama pull llava:latest

# 4. Configure in documents-to-markdown
documents-to-markdown --config set ai_service ollama
documents-to-markdown --config set ollama.base_url http://localhost:11434
documents-to-markdown --config set ollama.model llava:latest
```

### Option 2: OpenAI (Cloud AI - Easy Setup)

**Benefits:**
- ✅ **Easy Setup** - Just need API key
- ✅ **High Quality** - Consistently good results
- ❌ **Costs Money** - Pay per API call

**Setup:**
```bash
# 1. Get API key from https://platform.openai.com/api-keys

# 2. Set via environment variable (recommended)
export OPENAI_API_KEY=your_api_key_here  # Linux/macOS
set OPENAI_API_KEY=your_api_key_here     # Windows

# 3. Or configure directly
documents-to-markdown --config set ai_service openai
documents-to-markdown --config set openai.api_key your_api_key_here
```

### Option 3: Auto-Detection (Recommended)

```bash
# Let the system choose the best available service
documents-to-markdown --config set ai_service ""

# This will try OLLAMA first, then fallback to OpenAI
```

### Option 4: Disable AI Features

```bash
# Disable AI features completely
documents-to-markdown --config set ai_service none
```

## 📁 Configuration Files

The package automatically creates configuration files in the appropriate location for your OS:

### Windows
```
C:\Users\YourUsername\AppData\Roaming\documents-to-markdown\
├── config.json    # Main configuration
└── .env          # Environment variables
```

### macOS
```
~/Library/Application Support/documents-to-markdown/
├── config.json    # Main configuration
└── .env          # Environment variables
```

### Linux
```
~/.config/documents-to-markdown/
├── config.json    # Main configuration
└── .env          # Environment variables
```

### View Configuration Location
```bash
documents-to-markdown --config location
```

## ⚙️ Configuration Options

### Complete Configuration Example

```json
{
  "ai_service": "",
  "add_section_numbers": true,
  "verbose_logging": false,
  "openai": {
    "api_key": "your_key_here",
    "model": "gpt-4o",
    "max_tokens": 4096,
    "temperature": 0.1,
    "base_url": "https://api.openai.com/v1"
  },
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llava:latest",
    "timeout": 120,
    "temperature": 0.1
  },
  "image_processing": {
    "max_size_mb": 20,
    "quality_compression": 85,
    "max_size_pixels": 2048
  },
  "logging": {
    "level": "INFO",
    "file_logging": false,
    "log_file": "documents_to_markdown.log"
  }
}
```

### Setting Configuration Values

```bash
# General settings
documents-to-markdown --config set add_section_numbers true
documents-to-markdown --config set verbose_logging false

# OpenAI settings
documents-to-markdown --config set openai.api_key your_key
documents-to-markdown --config set openai.model gpt-4o
documents-to-markdown --config set openai.max_tokens 4096

# OLLAMA settings
documents-to-markdown --config set ollama.base_url http://localhost:11434
documents-to-markdown --config set ollama.model llava:latest
documents-to-markdown --config set ollama.timeout 120

# Image processing
documents-to-markdown --config set image_processing.max_size_mb 20
documents-to-markdown --config set image_processing.quality_compression 85

# Logging
documents-to-markdown --config set logging.level INFO
```

## 🔧 Configuration Commands

```bash
# Show current configuration
documents-to-markdown --config show

# Run interactive setup wizard
documents-to-markdown --config init

# Set a specific value
documents-to-markdown --config set key value

# Reset to defaults
documents-to-markdown --config reset

# Validate configuration
documents-to-markdown --config validate

# Show config file locations
documents-to-markdown --config location
```

## 🚀 Usage After Setup

### Library Usage
```python
from documents_to_markdown import DocumentConverter

# Uses your configured settings automatically
converter = DocumentConverter()
success = converter.convert_file("document.docx", "output.md")
```

### Command Line Usage
```bash
# Convert single file
documents-to-markdown --file document.docx output.md

# Convert all files in folder
documents-to-markdown --input docs --output markdown

# Show statistics
documents-to-markdown --stats
```

## 🔍 Troubleshooting

### Check Configuration Status
```bash
documents-to-markdown --config show
documents-to-markdown --config validate
```

### Common Issues

**1. AI Services Not Working**
```bash
# Check configuration
documents-to-markdown --config validate

# Test OLLAMA connection
curl http://localhost:11434/api/version

# Check OpenAI key
echo $OPENAI_API_KEY
```

**2. Configuration Not Found**
```bash
# Re-run setup
documents-to-markdown --config init

# Check file locations
documents-to-markdown --config location
```

**3. Permission Issues**
```bash
# Check config directory permissions
documents-to-markdown --config location
# Ensure you have write access to the config directory
```

## 🔄 Environment Variables

You can also use environment variables (they override config file):

```bash
# AI Service
export AI_SERVICE=openai

# OpenAI
export OPENAI_API_KEY=your_key_here
export OPENAI_MODEL=gpt-4o

# OLLAMA
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llava:latest

# Image Processing
export IMAGE_MAX_SIZE_MB=20
export IMAGE_QUALITY_COMPRESSION=85

# Logging
export LOG_LEVEL=INFO
```

## 📋 Quick Reference

### Essential Commands
```bash
# Install
pip install documents-to-markdown

# Setup
documents-to-markdown --config init

# Convert
documents-to-markdown --file input.docx output.md

# Help
documents-to-markdown --help
```

### Configuration Priority
1. **Command line arguments** (highest priority)
2. **Environment variables**
3. **Configuration file**
4. **Default values** (lowest priority)

## 🎉 You're Ready!

After following this guide, you'll have:
- ✅ Package installed via pip
- ✅ Configuration set up for your needs
- ✅ AI services configured (optional)
- ✅ Ready to convert documents

**Happy converting!** 🚀
