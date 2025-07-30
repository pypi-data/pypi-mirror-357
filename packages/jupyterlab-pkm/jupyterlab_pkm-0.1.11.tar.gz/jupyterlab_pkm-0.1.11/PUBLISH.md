what?
# Publishing Guide for JupyterLab PKM Extension

This document outlines how to publish the extension to various distribution channels.

## 📦 Package Structure

The extension is built as a Python package that contains:
- **Source code**: TypeScript files in `src/`
- **Compiled JavaScript**: Built extension in `jupyterlab_pkm/labextension/`
- **Python metadata**: Package info in `pyproject.toml`
- **Documentation**: README.md and inline help

## 🚀 Publishing to PyPI

### Prerequisites

1. **PyPI Account**: Create accounts on both [TestPyPI](https://test.pypi.org/) and [PyPI](https://pypi.org/)
2. **API Tokens**: Generate API tokens for authentication
3. **Build Tools**: Install required tools

```bash
pip install build twine
```

### Step 1: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/

# Build production version
npm run build:prod

# Build Python package
python -m build
```

This creates:
- `dist/jupyterlab_pkm-0.1.1.tar.gz` (source distribution)
- `dist/jupyterlab_pkm-0.1.1-py3-none-any.whl` (wheel)

### Step 2: Test on TestPyPI

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ jupyterlab-pkm
```

### Step 3: Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

### Step 4: Verify Installation

```bash
# Install from PyPI
pip install jupyterlab-pkm

# Verify extension is loaded
jupyter labextension list
```

## 📋 Pre-Publication Checklist

- [ ] Version number updated in `package.json`
- [ ] README.md is comprehensive and accurate
- [ ] LICENSE file is present
- [ ] All tests pass: `npm test`
- [ ] Production build completes: `npm run build:prod`
- [ ] Package builds successfully: `python -m build`
- [ ] Installation works in clean environment
- [ ] All features tested in fresh JupyterLab instance

## 🔍 Testing Installation

### Create Test Environment

```bash
# Create fresh conda environment
conda create -n test-pkm python=3.11 jupyterlab=4
conda activate test-pkm

# Install from local build
pip install dist/jupyterlab_pkm-0.1.0-py3-none-any.whl

# Or install from PyPI
pip install jupyterlab-pkm

# Start JupyterLab
jupyter lab
```

### Test Features

1. **Extension Loading**: Check that extension appears in Extensions panel
2. **Welcome Documentation**: Verify `PKM-Extension-Guide.md` is created
3. **Wikilinks**: Test `[[note]]` linking and navigation
4. **Search**: Use Alt+F for global search
5. **Backlinks**: Use Alt+B for backlinks panel
6. **Preview Toggle**: Use Alt+M to toggle markdown preview
7. **Notebook Embedding**: Test `![[notebook.ipynb#cell-id]]`

## 🏷️ Version Management

### Semantic Versioning

Follow [SemVer](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

### Release Process

1. **Update Version**: Change version in `package.json`
2. **Update Changelog**: Document changes in README.md
3. **Build and Test**: Run full test suite
4. **Tag Release**: Create git tag for version
5. **Publish**: Upload to PyPI
6. **Create GitHub Release**: Document release notes

```bash
# Example version bump
npm version patch  # or minor, major
git push --tags
```

## 🌐 Alternative Distribution

### GitHub Releases

1. **Create Release**: Use GitHub's release interface
2. **Attach Assets**: Include built wheel and tarball
3. **Installation**: Users can install directly from GitHub

```bash
pip install https://github.com/XLabCU/jupyterlab-desktop-pkm/releases/download/v0.1.0/jupyterlab_pkm-0.1.0-py3-none-any.whl
```

### conda-forge

After successful PyPI publication:

1. **Create Recipe**: Fork [conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes)
2. **Add Recipe**: Create recipe in `recipes/jupyterlab-pkm/meta.yaml`
3. **Submit PR**: Submit pull request to conda-forge
4. **Review Process**: Wait for review and approval

## 🔧 Maintenance

### Regular Updates

- **JupyterLab Compatibility**: Test with new JupyterLab versions
- **Dependency Updates**: Keep dependencies current
- **Bug Fixes**: Address issues reported by users
- **Feature Requests**: Consider new functionality

### Support Channels

- **GitHub Issues**: Primary support channel
- **Documentation**: Keep README and in-app help current
- **Community**: Engage with JupyterLab community

## 📊 Monitoring

### Package Statistics

- **PyPI Downloads**: Monitor download statistics
- **GitHub Stars**: Track repository popularity  
- **Issues**: Respond to bug reports and feature requests

### Usage Analytics

- **Extension Telemetry**: Consider optional usage analytics
- **User Feedback**: Collect feedback for improvements

## 🔒 Security

### Package Security

- **Dependency Scanning**: Regular security audits
- **Code Review**: Review all contributions
- **Version Pinning**: Pin critical dependencies

### Distribution Security

- **GPG Signing**: Consider signing releases
- **Checksum Verification**: Provide checksums for releases
- **Secure Upload**: Use API tokens, not passwords

---

## 📝 Current Status

- ✅ **Package Built**: Ready for distribution
- ✅ **Documentation**: Complete and accurate
- ✅ **Testing**: Features verified
- ⏳ **PyPI Upload**: Ready for publication
- ⏳ **conda-forge**: Pending PyPI publication

**Next Steps**: Upload to TestPyPI, then PyPI after verification.