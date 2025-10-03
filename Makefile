# Docker Installer TUI Makefile
# Provides targets for building, testing, and packaging the application

.PHONY: help install test clean dist package deb pip

# Default target
help:
	@echo "Docker Installer TUI Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install          Install dependencies"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests"
	@echo "  make test-practical   Run practical tests"
	@echo "  make test-system      Run system tests"
	@echo "  make clean            Clean build artifacts"
	@echo "  make dist             Create distribution package"
	@echo "  make deb              Create Debian package"
	@echo "  make pip              Create pip installable package"
	@echo "  make run              Run the TUI application"
	@echo "  make run-tui          Run the TUI with the convenience script"

# Install dependencies
install:
	pip3 install -r requirements.txt --break-system-packages

# Run all tests
test: test-unit test-practical test-system

test-unit:
	python3 test_suite.py

test-practical:
	python3 test_practical.py

test-system:
	python3 test_system.py

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf */__pycache__/

# Create distribution package
dist: clean
	python3 setup.py sdist bdist_wheel

# Create Debian package
deb:
	@echo "Creating Debian package..."
	mkdir -p deb_build/usr/local/bin
	cp -r . deb_build/usr/local/bin/docker-installer-tui
	cd deb_build && tar -czf docker-installer-tui.tar.gz usr
	@echo "Debian package creation is not fully automated in this makefile."
	@echo "Use 'make dist' to create Python package instead."

# Create pip installable package
pip: dist
	@echo "Pip installable package created in dist/ directory"
	ls -la dist/

# Run the TUI application
run:
	python3 DockerInstallerTUI.py

# Run the TUI with convenience script
run-tui:
	./run_tui.sh

# Install in development mode
develop:
	pip3 install -e . --break-system-packages

# Upload to PyPI (requires twine)
upload:
	twine upload dist/*

# Check package integrity
check:
	python3 -m pip check

# Verify all Python files
lint:
	python3 -m flake8 . --exclude=venv --ignore=E501,W503

# Create source distribution
sdist: dist
	@echo "Source distribution created in dist/ directory"
	ls -la dist/