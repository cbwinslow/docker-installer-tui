# Docker Installer TUI Makefile
# Provides targets for building, testing, and packaging the application

.PHONY: help install test clean dist package deb pip all

# Default target
all: install test

# Help target
help:
	@echo "Docker Installer TUI Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make all              Install dependencies and run all tests (default)"
	@echo "  make install          Install dependencies"
	@echo "  make test             Run all tests"
	@echo "  make test-all         Run all test suites including comprehensive"
	@echo "  make test-unit        Run unit tests"
	@echo "  make test-practical   Run practical tests"
	@echo "  make test-system      Run system tests"
	@echo "  make test-comprehensive Run comprehensive tests"
	@echo "  make test-tui         Run TUI tests"
	@echo "  make test-installation Run installation tests"
	@echo "  make test-installer-comprehensive Run comprehensive installer tests"
	@echo "  make validate         Run syntax validation on all Python files"
	@echo "  make clean            Clean build artifacts"
	@echo "  make dist             Create distribution package"
	@echo "  make pip              Create pip installable package"
	@echo "  make run              Run the TUI application"
	@echo "  make run-tui          Run the TUI with the convenience script"
	@echo "  make develop          Install in development mode"
	@echo "  make check            Check package integrity"
	@echo "  make lint             Run linter on Python files"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt --break-system-packages

# Run all core tests
test: test-unit test-practical test-system

# Run all tests including comprehensive
test-all: test-unit test-practical test-system test-comprehensive test-tui test-installation test-installer-comprehensive
	@echo ""
	@echo "✓ All test suites completed!"

test-unit:
	@echo "Running unit tests..."
	python3 test_suite.py

test-practical:
	@echo "Running practical tests..."
	python3 test_practical.py

test-system:
	@echo "Running system tests..."
	python3 test_system.py

test-comprehensive:
	@echo "Running comprehensive tests..."
	python3 test_comprehensive.py

test-tui:
	@echo "Running TUI tests..."
	python3 test_tui.py

test-installation:
	@echo "Running installation tests..."
	python3 test_installation.py

test-installer-comprehensive:
	@echo "Running comprehensive installer tests..."
	python3 test_installer_comprehensive.py

# Validate Python syntax
validate:
	@echo "Validating Python syntax..."
	@python3 -m py_compile DockerInstaller.py
	@python3 -m py_compile DockerInstallerTUI.py
	@python3 -m py_compile OctopusMascot.py
	@python3 -m py_compile test_*.py
	@echo "✓ All Python files have valid syntax"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf .pytest_cache/
	rm -rf .eggs/
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean complete"

# Create distribution package
dist: clean validate
	@echo "Creating distribution packages..."
	python3 setup.py sdist bdist_wheel
	@echo "✓ Distribution packages created in dist/ directory"
	@ls -lh dist/ 2>/dev/null || true

# Create pip installable package (alias for dist)
pip: dist
	@echo "✓ Pip installable package created in dist/ directory"

# Run the TUI application
run:
	@echo "Starting Docker Installer TUI..."
	python3 DockerInstallerTUI.py

# Run the TUI with convenience script
run-tui:
	@echo "Starting Docker Installer TUI with convenience script..."
	bash ./run_tui.sh

# Install in development mode
develop:
	@echo "Installing in development mode..."
	pip3 install -e . --break-system-packages
	@echo "✓ Development installation complete"

# Upload to PyPI (requires twine)
upload: dist
	@echo "Uploading to PyPI..."
	@command -v twine >/dev/null 2>&1 || { echo "Error: twine is not installed. Install with: pip3 install twine"; exit 1; }
	twine upload dist/*

# Check package integrity
check:
	@echo "Checking package integrity..."
	python3 -m pip check
	@echo "✓ Package check complete"

# Verify all Python files with flake8
lint:
	@echo "Running linter..."
	@command -v flake8 >/dev/null 2>&1 || { echo "Warning: flake8 is not installed. Install with: pip3 install flake8"; exit 0; }
	python3 -m flake8 . --exclude=venv,build,dist --ignore=E501,W503 || true
	@echo "✓ Lint complete"