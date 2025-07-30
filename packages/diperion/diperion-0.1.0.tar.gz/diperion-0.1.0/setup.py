"""
Setup configuration for the Diperion Python SDK
"""

from setuptools import setup, find_packages
import os

# Read the README file
current_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="diperion",
    version="0.1.0",
    author="Diperion Team",
    author_email="contact@diperion.com",
    description="Python SDK for the Diperion Semantic Engine - Build powerful semantic applications with ease",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diperion/diperion-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/diperion/diperion-python-sdk/issues",
        "Documentation": "https://api.diperion.com/docs",
        "Source Code": "https://github.com/diperion/diperion-python-sdk",
        "Homepage": "https://diperion.com",
        "API Reference": "https://api.diperion.com/health"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
            "twine>=4.0.0",
            "build>=0.8.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords=[
        "semantic",
        "engine", 
        "graph",
        "knowledge",
        "ai",
        "machine-learning",
        "nlp",
        "database",
        "query",
        "api",
        "sdk",
        "diperion",
        "business-intelligence",
        "semantic-search"
    ],
    include_package_data=True,
    zip_safe=False,
) 