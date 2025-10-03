# Publishing Guide

This guide explains how to publish the Docker Installer TUI package to PyPI.

## Prerequisites

1. PyPI account with API token
2. `twine` installed: `pip3 install twine --break-system-packages`
3. `build` installed: `pip3 install build --break-system-packages`

## Steps to Publish

### 1. Prepare the Release

```bash
# Update version in setup.py and pyproject.toml
# Run all tests
make test

# Create distribution packages
make dist
```

### 2. Test the Package

```bash
# Check the package
python3 -m pip check

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip3 install --index-url https://test.pypi.org/simple/ docker-installer-tui
```

### 3. Upload to PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

## Configuration Files

### .pypirc
Create `~/.pypirc` with your credentials:

```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository: https://upload.pypi.org/legacy/
username: __token__
password: your-pypi-api-token-here

[testpypi]
repository: https://test.pypi.org/legacy/
username: __token__
password: your-testpypi-api-token-here
```

## Package Information

- **Name**: docker-installer-tui
- **Entry Points**:
  - `docker-installer-tui`: Main TUI application
  - `docker-installer`: CLI installer
- **Dependencies**: Textual, Requests, Docker
- **Python Version**: 3.8+

## Versioning

Follow semantic versioning:
- MAJOR.MINOR.PATCH (e.g., 1.0.0)
- Increment MAJOR for incompatible API changes
- Increment MINOR for functionality additions
- Increment PATCH for bug fixes

## Release Process

1. Update version number in setup.py and pyproject.toml
2. Update CHANGELOG.md and RELEASE_NOTES.md
3. Run tests: `make test`
4. Create distribution: `make dist`
5. Upload to TestPyPI and test
6. Upload to PyPI
7. Create GitHub release

## Post-Publish Steps

1. Create a git tag: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. Create a GitHub release
4. Update documentation to point to new version

## Troubleshooting

### Common Issues:

- **Invalid API token**: Ensure you're using the correct PyPI API token
- **Package already exists**: Increment version number before uploading
- **Dependencies not found**: Check that all dependencies are correctly specified
- **Permission errors**: Ensure you have proper permissions for the package name

### Verification:

After publishing, verify the package:
```bash
pip3 install docker-installer-tui
docker-installer-tui --help
```