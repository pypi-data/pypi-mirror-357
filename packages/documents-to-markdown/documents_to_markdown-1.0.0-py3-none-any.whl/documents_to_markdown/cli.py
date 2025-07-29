#!/usr/bin/env python3
"""
Documents to Markdown Converter - Command Line Interface

This module provides the command-line interface for the document converter.
It can be used as a standalone script or as an entry point when installed as a package.
"""

import sys
import argparse
from pathlib import Path
import logging
import json

from .api import DocumentConverter
from .config import config_manager, get_config, save_config
from .setup_wizard import check_and_run_setup


def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("Documents to Markdown Converter")
    print("=" * 60)
    print("Supported formats: Word, PDF, Excel, Images, Plain Text")
    print("Features: Section numbering, batch processing, AI image extraction")
    print("=" * 60)


def print_statistics(converter):
    """Print converter statistics."""
    stats = converter.get_conversion_statistics()

    print(f"\nAvailable Converters: {stats['total_converters']}")
    print(f"Supported Extensions: {', '.join(stats['supported_extensions'])}")

    print("\nConverter Details:")
    for converter_info in stats['converters']:
        name = converter_info['name']
        extensions = ', '.join(converter_info['supported_extensions'])
        numbering = "✓" if converter_info['section_numbering_enabled'] else "✗"
        print(f"  • {name}: {extensions} (Section numbering: {numbering})")


def print_conversion_results(results):
    """Print conversion results summary."""
    print(f"\nConversion Results:")
    print(f"  Total files: {results['total_files']}")
    print(f"  Successful: {results['successful_conversions']}")
    print(f"  Failed: {results['failed_conversions']}")

    if results['results']:
        print(f"\nDetailed Results:")
        for result in results['results']:
            status_icon = "✓" if result['status'] == 'success' else "✗"
            print(f"  {status_icon} {result['file']} ({result['converter']})")


def handle_config_command(args):
    """Handle configuration-related commands."""
    if args.config_action == 'show':
        show_config()
    elif args.config_action == 'init':
        init_config()
    elif args.config_action == 'set':
        set_config_value(args.config_key, args.config_value)
    elif args.config_action == 'reset':
        reset_config()
    elif args.config_action == 'validate':
        validate_config()
    elif args.config_action == 'test':
        test_ai_services()
    elif args.config_action == 'location':
        show_config_location()


def show_config():
    """Show current configuration."""
    print("=" * 60)
    print("Current Configuration")
    print("=" * 60)

    config = get_config()
    config_info = config_manager.get_config_info()

    print(f"Configuration file: {config_info['config_file']}")
    print(f"Environment file: {config_info['env_file']}")
    print(f"Config exists: {'✓' if config_info['config_exists'] else '✗'}")
    print(f"Env file exists: {'✓' if config_info['env_exists'] else '✗'}")

    print("\nSettings:")
    print(f"  AI Service: {config.get('ai_service', 'auto-detect')}")
    print(f"  Section Numbers: {'✓' if config.get('add_section_numbers', True) else '✗'}")
    print(f"  Verbose Logging: {'✓' if config.get('verbose_logging', False) else '✗'}")

    # OpenAI settings
    openai_config = config.get('openai', {})
    print(f"\nOpenAI Configuration:")
    print(f"  API Key: {'✓ Set' if openai_config.get('api_key') else '✗ Not set'}")
    print(f"  Model: {openai_config.get('model', 'gpt-4o')}")
    print(f"  Max Tokens: {openai_config.get('max_tokens', 4096)}")

    # OLLAMA settings
    ollama_config = config.get('ollama', {})
    print(f"\nOLLAMA Configuration:")
    print(f"  Base URL: {ollama_config.get('base_url', 'http://localhost:11434')}")
    print(f"  Model: {ollama_config.get('model', 'llava:latest')}")
    print(f"  Timeout: {ollama_config.get('timeout', 120)}s")


def init_config():
    """Initialize configuration with interactive setup."""
    print("=" * 60)
    print("Documents to Markdown - Configuration Setup")
    print("=" * 60)

    config = config_manager.get_default_config()

    print("\n🤖 AI Service Configuration")
    print("Choose your AI service for image processing:")
    print("1. Auto-detect (recommended) - Try OLLAMA first, fallback to OpenAI")
    print("2. OpenAI (cloud-based, requires API key)")
    print("3. OLLAMA (local, private)")
    print("4. None (disable AI features)")

    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice == "1":
            config["ai_service"] = ""
            break
        elif choice == "2":
            config["ai_service"] = "openai"
            api_key = input("Enter your OpenAI API key: ").strip()
            if api_key:
                config["openai"]["api_key"] = api_key
            break
        elif choice == "3":
            config["ai_service"] = "ollama"
            base_url = input(f"OLLAMA base URL [{config['ollama']['base_url']}]: ").strip()
            if base_url:
                config["ollama"]["base_url"] = base_url
            break
        elif choice == "4":
            config["ai_service"] = "none"
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

    print("\n⚙️ General Settings")
    section_numbers = input("Enable automatic section numbering? (Y/n): ").strip().lower()
    config["add_section_numbers"] = section_numbers != "n"

    verbose = input("Enable verbose logging? (y/N): ").strip().lower()
    config["verbose_logging"] = verbose == "y"

    # Save configuration
    if save_config(config):
        config_manager.create_env_file(config)
        print("\n✅ Configuration saved successfully!")

        config_info = config_manager.get_config_info()
        print(f"Configuration file: {config_info['config_file']}")
        print(f"Environment file: {config_info['env_file']}")

        # Validate configuration
        issues = config_manager.validate_config(config)
        if issues:
            print("\n⚠️  Configuration Issues:")
            for issue in issues:
                print(f"  • {issue}")
        else:
            print("\n✅ Configuration is valid!")
    else:
        print("\n❌ Failed to save configuration!")


def set_config_value(key, value):
    """Set a specific configuration value."""
    if not key or not value:
        print("Error: Both key and value are required for --config set")
        return

    config = get_config()

    # Handle nested keys (e.g., "openai.api_key")
    keys = key.split('.')
    current = config

    # Navigate to the parent of the target key
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    # Set the value
    final_key = keys[-1]

    # Convert value to appropriate type
    if value.lower() in ('true', 'false'):
        current[final_key] = value.lower() == 'true'
    elif value.isdigit():
        current[final_key] = int(value)
    elif value.replace('.', '').isdigit():
        current[final_key] = float(value)
    else:
        current[final_key] = value

    if save_config(config):
        config_manager.create_env_file(config)
        print(f"✅ Set {key} = {value}")
    else:
        print(f"❌ Failed to save configuration")


def reset_config():
    """Reset configuration to defaults."""
    print("⚠️  This will reset all configuration to default values.")
    confirm = input("Are you sure? (y/N): ").strip().lower()

    if confirm == 'y':
        if config_manager.reset_to_defaults():
            print("✅ Configuration reset to defaults")
        else:
            print("❌ Failed to reset configuration")
    else:
        print("Configuration reset cancelled")


def validate_config():
    """Validate current configuration."""
    print("🔍 Validating configuration...")

    config = get_config()
    issues = config_manager.validate_config(config)

    if not issues:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"  • {issue}")


def test_ai_services():
    """Test AI service connectivity."""
    print("🔍 Testing AI service connectivity...")

    config = get_config()
    results = config_manager.test_ai_services(config)

    print("\n🤖 AI Service Status:")

    # OLLAMA results
    ollama = results["ollama"]
    if ollama["available"]:
        print("✅ OLLAMA: Available")
        if "model" in ollama:
            print(f"   Model: {ollama['model']}")
    else:
        print("❌ OLLAMA: Not available")
        if ollama["error"]:
            print(f"   Error: {ollama['error']}")

    # OpenAI results
    openai = results["openai"]
    if openai["available"]:
        print("✅ OpenAI: Available")
        if "model" in openai:
            print(f"   Model: {openai['model']}")
    else:
        print("❌ OpenAI: Not available")
        if openai["error"]:
            print(f"   Error: {openai['error']}")

    # Recommendations
    print("\n💡 Recommendations:")
    if not ollama["available"] and not openai["available"]:
        print("  • No AI services available - AI features will be disabled")
        print("  • Install OLLAMA (https://ollama.ai) for local AI")
        print("  • Or set up OpenAI API key for cloud AI")
    elif ollama["available"] and not openai["available"]:
        print("  • OLLAMA is available - great for privacy!")
        print("  • Consider setting up OpenAI as backup")
    elif not ollama["available"] and openai["available"]:
        print("  • OpenAI is available - good for high quality results")
        print("  • Consider installing OLLAMA for local processing")
    else:
        print("  • Both services available - excellent setup!")
        print("  • Auto-detection will use OLLAMA first, then OpenAI")


def show_config_location():
    """Show configuration file locations."""
    config_info = config_manager.get_config_info()

    print("📁 Configuration Locations:")
    print(f"  Directory: {config_info['config_directory']}")
    print(f"  Config file: {config_info['config_file']}")
    print(f"  Environment file: {config_info['env_file']}")
    print(f"\nFile Status:")
    print(f"  Config exists: {'✓' if config_info['config_exists'] else '✗'}")
    print(f"  Env file exists: {'✓' if config_info['env_exists'] else '✗'}")
    print(f"  Directory exists: {'✓' if config_info['config_directory_exists'] else '✗'}")


def main():
    """Main function to run the document converter CLI."""
    parser = argparse.ArgumentParser(
        description="Convert documents to Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  documents-to-markdown                           # Convert all files in input/ folder
  documents-to-markdown --no-numbering           # Convert without section numbering
  documents-to-markdown -i docs -o markdown      # Custom input/output folders
  documents-to-markdown --stats                  # Show converter statistics only
  documents-to-markdown --file doc.docx out.md   # Convert single file
  documents-to-markdown --config init            # Setup configuration interactively
  documents-to-markdown --config show            # Show current configuration
  doc2md --help                                  # Show help (alternative command)
        """
    )

    parser.add_argument(
        '--input', '-i',
        default='input',
        help='Input folder containing documents to convert (default: input)'
    )

    parser.add_argument(
        '--output', '-o',
        default='output',
        help='Output folder for converted Markdown files (default: output)'
    )

    parser.add_argument(
        '--file', '-f',
        nargs=2,
        metavar=('INPUT_FILE', 'OUTPUT_FILE'),
        help='Convert a single file: --file input.docx output.md'
    )

    parser.add_argument(
        '--no-numbering',
        action='store_true',
        help='Disable automatic section numbering'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show converter statistics and exit'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    # Configuration commands
    parser.add_argument(
        '--config',
        dest='config_action',
        choices=['show', 'init', 'set', 'reset', 'validate', 'test', 'location'],
        help='Configuration management: show current config, init setup, set values, reset to defaults, validate config, test AI services, or show file locations'
    )

    parser.add_argument(
        '--config-key',
        help='Configuration key to set (use with --config set)'
    )

    parser.add_argument(
        '--config-value',
        help='Configuration value to set (use with --config set)'
    )

    args = parser.parse_args()

    # Handle configuration commands first
    if args.config_action:
        handle_config_command(args)
        return 0

    # Check for first-time setup (skip for stats command)
    if not args.stats:
        setup_ran = check_and_run_setup()
        if setup_ran:
            # Setup wizard ran, ask if user wants to continue
            print("\n" + "=" * 60)
            continue_choice = input("Would you like to continue with document conversion? (Y/n): ").strip().lower()
            if continue_choice == 'n':
                print("Setup complete! You can run document conversion anytime.")
                return 0

    # Print banner
    print_banner()

    # Initialize converter
    try:
        converter = DocumentConverter(
            add_section_numbers=not args.no_numbering,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"Error initializing converter: {e}")
        return 1

    # Show statistics if requested
    if args.stats:
        print_statistics(converter)
        return 0

    # Handle single file conversion
    if args.file:
        input_file, output_file = args.file
        print(f"\nConverting single file: {input_file} -> {output_file}")
        
        # Check if input file exists
        if not Path(input_file).exists():
            print(f"Error: Input file '{input_file}' does not exist.")
            return 1
        
        # Check if file can be converted
        if not converter.can_convert(input_file):
            print(f"Error: File type not supported: {Path(input_file).suffix}")
            supported = converter.get_supported_formats()
            print(f"Supported formats: {', '.join(supported)}")
            return 1
        
        # Perform conversion
        try:
            success = converter.convert_file(input_file, output_file)
            if success:
                print(f"✓ Conversion completed successfully!")
                print(f"Output saved to: {output_file}")
                return 0
            else:
                print(f"✗ Conversion failed. Check the logs for details.")
                return 1
        except Exception as e:
            print(f"Error during conversion: {e}")
            return 1

    # Handle batch conversion
    print_statistics(converter)

    # Check for files to convert
    convertible_files = converter.get_convertible_files(args.input)
    if not convertible_files:
        print(f"\nNo convertible files found in '{args.input}' folder.")
        supported = converter.get_supported_formats()
        print(f"Supported formats: {', '.join(supported)}")
        print("\nPlease add some documents to the input folder and try again.")
        return 0

    print(f"\nFound {len(convertible_files)} file(s) to convert:")
    for file_path in convertible_files:
        print(f"  • {file_path.name}")

    # Perform batch conversion
    print(f"\nStarting conversion...")
    try:
        results = converter.convert_all(args.input, args.output)
        print_conversion_results(results)

        if results['successful_conversions'] > 0:
            print(f"\n✓ Conversion completed successfully!")
            print(f"Check the '{args.output}' folder for converted Markdown files.")

        if results['failed_conversions'] > 0:
            print(f"\n⚠ Some conversions failed. Check the logs for details.")
            return 1

        return 0

    except Exception as e:
        print(f"\nError during conversion: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
