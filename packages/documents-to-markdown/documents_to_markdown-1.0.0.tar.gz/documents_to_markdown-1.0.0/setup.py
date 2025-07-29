#!/usr/bin/env python3
"""
Setup script for Documents to Markdown Converter
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="documents-to-markdown",
    version="1.0.0",
    author="Felix",
    author_email="yangzhenwu@gmail.com",
    description="A comprehensive Python library for converting various document types to Markdown format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChaosAIs/DocumentsToMarkdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Office/Business :: Office Suites",
    ],
    license="MIT",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "documents-to-markdown=documents_to_markdown.cli:main",
            "doc2md=documents_to_markdown.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "documents_to_markdown": ["*.md", "*.txt"],
    },
    keywords="document conversion markdown word pdf excel image text converter",
    project_urls={
        "Bug Reports": "https://github.com/ChaosAIs/DocumentsToMarkdown/issues",
        "Source": "https://github.com/ChaosAIs/DocumentsToMarkdown",
        "Documentation": "https://github.com/ChaosAIs/DocumentsToMarkdown/blob/main/README.md",
    },
)
