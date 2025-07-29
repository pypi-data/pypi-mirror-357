# 🚀 Publishing to PyPI - Complete Guide

This guide will walk you through publishing your `documents-to-markdown` package to PyPI so the community can install it with `pip install documents-to-markdown`.

## 📋 Prerequisites

### 1. Create PyPI Accounts

You'll need accounts on both TestPyPI (for testing) and PyPI (for production):

**TestPyPI (Testing):**
1. Go to https://test.pypi.org/account/register/
2. Create an account with your email
3. Verify your email address

**PyPI (Production):**
1. Go to https://pypi.org/account/register/
2. Create an account with your email
3. Verify your email address

### 2. Enable Two-Factor Authentication (Recommended)

For security, enable 2FA on both accounts:
1. Go to Account Settings
2. Enable Two-factor authentication
3. Use an authenticator app like Google Authenticator

### 3. Create API Tokens

Instead of using passwords, create API tokens:

**For TestPyPI:**
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "documents-to-markdown-test"
4. Scope: "Entire account" (or specific project after first upload)
5. Copy the token (starts with `pypi-`)

**For PyPI:**
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "documents-to-markdown"
4. Scope: "Entire account" (or specific project after first upload)
5. Copy the token (starts with `pypi-`)

## 🛠️ Install Publishing Tools

```bash
# Install twine for uploading packages
pip install twine

# Install build tools (if not already installed)
pip install build

# Optional: Install keyring for secure token storage
pip install keyring
```

## 🔧 Configure Credentials

### Option 1: Using .pypirc file (Recommended)

Create a `.pypirc` file in your home directory:

**Windows:** `C:\Users\YourUsername\.pypirc`
**macOS/Linux:** `~/.pypirc`

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

### Option 2: Using Environment Variables

```bash
# For TestPyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TESTPYPI_TOKEN_HERE

# For PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_PYPI_TOKEN_HERE
```

## 📦 Prepare Your Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info/
```

### 2. Update Version (if needed)

Edit version in both files:
- `setup.py`: `version="1.0.0"`
- `pyproject.toml`: `version = "1.0.0"`
- `documents_to_markdown/__init__.py`: `__version__ = "1.0.0"`

### 3. Verify Package Contents

```bash
# Check what files will be included
python -m build --sdist
tar -tzf dist/documents-to-markdown-1.0.0.tar.gz
```

### 4. Build the Package

```bash
# Build both wheel and source distribution
python -m build
```

This creates:
- `dist/documents_to_markdown-1.0.0-py3-none-any.whl` (wheel)
- `dist/documents_to_markdown-1.0.0.tar.gz` (source)

## 🧪 Test on TestPyPI First

### 1. Upload to TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

### 2. Test Installation from TestPyPI

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ documents-to-markdown

# Test the installation
python -c "from documents_to_markdown import DocumentConverter; print('Success!')"
documents-to-markdown --help
```

### 3. Verify Everything Works

Test both library and CLI functionality:

```bash
# Test library usage
python -c "
from documents_to_markdown import convert_document
print('Library import successful!')
"

# Test CLI
documents-to-markdown --stats
doc2md --version
```

## 🚀 Publish to PyPI

Once testing is successful:

### 1. Upload to PyPI

```bash
# Upload to the main PyPI
twine upload dist/*
```

### 2. Verify on PyPI

1. Go to https://pypi.org/project/documents-to-markdown/
2. Check that your package appears correctly
3. Verify the description, links, and metadata

### 3. Test Installation from PyPI

```bash
# Create fresh environment
python -m venv pypi_test
source pypi_test/bin/activate  # On Windows: pypi_test\Scripts\activate

# Install from PyPI
pip install documents-to-markdown

# Test functionality
documents-to-markdown --help
python -c "from documents_to_markdown import DocumentConverter; print('PyPI installation successful!')"
```

## 📢 Share with Community

### 1. Update GitHub Repository

```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0

# Create a GitHub release
# Go to https://github.com/ChaosAIs/DocumentsToMarkdown/releases
# Click "Create a new release"
# Use tag v1.0.0 and add release notes
```

### 2. Update README

Add installation instructions:

```markdown
## Installation

```bash
pip install documents-to-markdown
```

### 3. Announce Your Package

- **Reddit**: Post in r/Python, r/programming
- **Twitter/X**: Share with #Python #OpenSource hashtags
- **LinkedIn**: Professional announcement
- **Python Discord/Slack**: Share in relevant channels
- **Dev.to**: Write a blog post about your package

## 🔄 Future Updates

### Updating Your Package

1. **Update version numbers** in setup.py, pyproject.toml, and __init__.py
2. **Update CHANGELOG.md** with new features/fixes
3. **Build and test** on TestPyPI first
4. **Upload to PyPI** when ready
5. **Create GitHub release** with tag

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **1.0.1**: Bug fixes (patch)
- **1.1.0**: New features (minor)
- **2.0.0**: Breaking changes (major)

## 🛡️ Security Best Practices

1. **Never commit API tokens** to version control
2. **Use API tokens** instead of passwords
3. **Enable 2FA** on PyPI accounts
4. **Regularly rotate tokens**
5. **Use project-scoped tokens** when possible

## 📊 Monitor Your Package

### PyPI Statistics
- View download statistics on your PyPI project page
- Monitor for issues or user feedback

### GitHub
- Watch for issues and pull requests
- Respond to community feedback
- Maintain documentation

## 🎉 Success!

Once published, users worldwide can install your package with:

```bash
pip install documents-to-markdown
```

Your package will be available at:
- **PyPI**: https://pypi.org/project/documents-to-markdown/
- **Documentation**: Your GitHub repository
- **Issues**: GitHub Issues page

Congratulations on contributing to the Python ecosystem! 🐍✨
