"""
Setup file for Docker Installer TUI
This package provides a Terminal User Interface for Docker installation and management.
"""
import os
from setuptools import setup, find_packages


def read_long_description():
    """Read the long description from README.md."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read the requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = []
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
        return requirements


setup(
    name="docker-installer-tui",
    version="1.0.0",
    author="Community",
    author_email="docker-installer-tui@example.com",
    description="A Terminal User Interface for Docker installation, management, and exploration",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/cbwinslow/docker-installer-tui",
    project_urls={
        "Bug Reports": "https://github.com/cbwinslow/docker-installer-tui/issues",
        "Source": "https://github.com/cbwinslow/docker-installer-tui",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "docker-installer-tui=DockerInstallerTUI:main",
            "docker-installer=DockerInstaller:main",
        ],
    },
    package_data={
        "": ["*.tcss", "*.json", "*.md", "*.sh"],
    },
    include_package_data=True,
    keywords="docker, installer, tui, terminal, ui, container, containers, management",
    license="MIT",
)