#!/usr/bin/env python3
"""Setup script for selenium-auto-refresh package."""

import os
import sys
from pathlib import Path

from setuptools import find_packages, setup

# Ensure we're in the right directory
here = Path(__file__).parent.absolute()
sys.path.insert(0, str(here / "selenium_auto_refresh"))

# Read version from __init__.py
def get_version():
    """Get version from __init__.py file."""
    version_file = here / "selenium_auto_refresh" / "__init__.py"
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

# Read long description from README
def get_long_description():
    """Get long description from README file."""
    readme_file = here / "README.md"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return "Automatically refresh Chrome tabs using Selenium WebDriver"

# Read requirements
def get_requirements():
    """Get requirements from requirements.txt file."""
    requirements_file = here / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["selenium>=4.0.0"]

setup(
    name="selenium-auto-refresh",
    version=get_version(),
    author="Lalit2206",
    author_email="happytaak8@gmail.com",  
    description="Automatically refresh Chrome tabs using Selenium WebDriver with support for multiple URLs and async operations",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Lalit2206/selenium-auto-refresh",
    project_urls={
        "Bug Reports": "https://github.com/Lalit2206/selenium-auto-refresh/issues",
        "Source": "https://github.com/Lalit2206/selenium-auto-refresh",
        "Documentation": "https://github.com/Lalit2206/selenium-auto-refresh#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
    ],
    keywords="selenium webdriver chrome refresh automation testing browser",
    python_requires=">=3.7",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "selenium-auto-refresh=selenium_auto_refresh.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)