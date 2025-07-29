#!/usr/bin/env python3
"""
Setup Wizard for Documents to Markdown

This module provides an interactive setup wizard that runs when users
first install and use the package via pip.
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any

from .config import config_manager, save_config


def check_ai_services() -> Dict[str, bool]:
    """Check which AI services are available."""
    services = {
        'ollama': False,
        'openai_key': False
    }
    
    # Check OLLAMA
    try:
        import requests
        response = requests.get('http://localhost:11434/api/version', timeout=5)
        if response.status_code == 200:
            services['ollama'] = True
    except:
        pass
    
    # Check for OpenAI key in environment
    import os
    if os.environ.get('OPENAI_API_KEY'):
        services['openai_key'] = True
    
    return services


def run_first_time_setup() -> bool:
    """Run the first-time setup wizard."""
    print("🎉 Welcome to Documents to Markdown!")
    print("=" * 60)
    print("This appears to be your first time using the package.")
    print("Let's set up your configuration for the best experience.")
    print()
    
    # Check if user wants to run setup
    response = input("Would you like to run the setup wizard now? (Y/n): ").strip().lower()
    if response == 'n':
        print("Setup skipped. You can run it later with: documents-to-markdown --config init")
        return False
    
    print("\n🔍 Checking available AI services...")
    services = check_ai_services()
    
    config = config_manager.get_default_config()
    
    # AI Service Configuration
    print("\n🤖 AI Service Setup")
    print("AI services enable advanced features like:")
    print("  • Text extraction from images")
    print("  • Processing embedded images in documents")
    print("  • Enhanced text formatting")
    print()
    
    if services['ollama']:
        print("✅ OLLAMA detected and running locally")
    else:
        print("❌ OLLAMA not detected")
        print("   Install from: https://ollama.ai")
        print("   Then run: ollama pull llava:latest")
    
    if services['openai_key']:
        print("✅ OpenAI API key found in environment")
    else:
        print("❌ OpenAI API key not found")
        print("   Get one from: https://platform.openai.com/api-keys")
    
    print("\nChoose your AI service:")
    print("1. Auto-detect (recommended) - Use OLLAMA if available, fallback to OpenAI")
    print("2. OpenAI only (cloud-based)")
    print("3. OLLAMA only (local, private)")
    print("4. Disable AI features")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice == "1":
            config["ai_service"] = ""
            print("✅ Auto-detection enabled")
            break
        elif choice == "2":
            config["ai_service"] = "openai"
            if not services['openai_key']:
                api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
                if api_key:
                    config["openai"]["api_key"] = api_key
                    print("✅ OpenAI configured")
                else:
                    print("⚠️  You can set the API key later with environment variable OPENAI_API_KEY")
            break
        elif choice == "3":
            config["ai_service"] = "ollama"
            if not services['ollama']:
                print("⚠️  OLLAMA not detected. Please install and start OLLAMA first.")
                base_url = input(f"OLLAMA base URL [{config['ollama']['base_url']}]: ").strip()
                if base_url:
                    config["ollama"]["base_url"] = base_url
            print("✅ OLLAMA configured")
            break
        elif choice == "4":
            config["ai_service"] = "none"
            print("✅ AI features disabled")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    # General Settings
    print("\n⚙️ General Settings")
    
    section_numbers = input("Enable automatic section numbering? (Y/n): ").strip().lower()
    config["add_section_numbers"] = section_numbers != "n"
    
    verbose = input("Enable verbose logging for troubleshooting? (y/N): ").strip().lower()
    config["verbose_logging"] = verbose == "y"
    
    # Save configuration
    print("\n💾 Saving configuration...")
    if save_config(config):
        config_manager.create_env_file(config)
        print("✅ Configuration saved successfully!")
        
        config_info = config_manager.get_config_info()
        print(f"\nConfiguration saved to:")
        print(f"  📁 {config_info['config_file']}")
        print(f"  📄 {config_info['env_file']}")
        
        # Validate configuration
        issues = config_manager.validate_config(config)
        if issues:
            print("\n⚠️  Configuration warnings:")
            for issue in issues:
                print(f"  • {issue}")
            print("\nYou can fix these later with: documents-to-markdown --config init")
        else:
            print("\n✅ Configuration is valid and ready to use!")
        
        return True
    else:
        print("❌ Failed to save configuration!")
        return False


def show_quick_start():
    """Show quick start information after setup."""
    print("\n🚀 Quick Start Guide")
    print("=" * 60)
    print("Your Documents to Markdown converter is ready!")
    print()
    print("📚 Library Usage:")
    print("  from documents_to_markdown import DocumentConverter")
    print("  converter = DocumentConverter()")
    print("  converter.convert_file('document.docx', 'output.md')")
    print()
    print("🖥️  Command Line Usage:")
    print("  documents-to-markdown --file document.docx output.md")
    print("  documents-to-markdown --input docs --output markdown")
    print("  documents-to-markdown --help")
    print()
    print("🔧 Configuration:")
    print("  documents-to-markdown --config show     # View current settings")
    print("  documents-to-markdown --config init     # Re-run setup wizard")
    print("  documents-to-markdown --config validate # Check configuration")
    print()
    print("📖 Supported Formats:")
    print("  • Word documents (.docx, .doc)")
    print("  • PDF documents (.pdf)")
    print("  • Excel spreadsheets (.xlsx, .xlsm, .xls)")
    print("  • Images (.png, .jpg, .jpeg, .gif, .bmp, .tiff)")
    print("  • Plain text (.txt, .csv, .tsv, .log)")
    print()
    print("🆘 Need Help?")
    print("  • GitHub: https://github.com/ChaosAIs/DocumentsToMarkdown")
    print("  • Issues: https://github.com/ChaosAIs/DocumentsToMarkdown/issues")
    print("  • Documentation: See README.md")


def check_and_run_setup() -> bool:
    """Check if setup is needed and run it if necessary."""
    config_info = config_manager.get_config_info()
    
    # If config doesn't exist, run first-time setup
    if not config_info['config_exists']:
        if run_first_time_setup():
            show_quick_start()
            return True
        else:
            # User skipped setup, create minimal config
            config = config_manager.get_default_config()
            save_config(config)
            return False
    
    return False


def install_ai_dependencies():
    """Help user install AI service dependencies."""
    print("\n🔧 AI Service Installation Help")
    print("=" * 60)
    
    print("\n🏠 OLLAMA (Local AI - Recommended for Privacy)")
    print("1. Download and install OLLAMA from: https://ollama.ai")
    print("2. Start OLLAMA: ollama serve")
    print("3. Install vision model: ollama pull llava:latest")
    print("4. Test: curl http://localhost:11434/api/version")
    
    print("\n☁️  OpenAI (Cloud AI - Easy Setup)")
    print("1. Sign up at: https://platform.openai.com")
    print("2. Get API key from: https://platform.openai.com/api-keys")
    print("3. Set environment variable: OPENAI_API_KEY=your_key_here")
    print("4. Or use: documents-to-markdown --config set openai.api_key your_key_here")
    
    print("\n🔄 Auto-Detection (Recommended)")
    print("Configure both services and let the system choose the best available one.")
    print("The system will try OLLAMA first (private), then fallback to OpenAI.")


if __name__ == "__main__":
    # Run setup wizard directly
    run_first_time_setup()
    show_quick_start()
