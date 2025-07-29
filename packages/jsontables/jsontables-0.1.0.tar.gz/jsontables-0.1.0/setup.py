#!/usr/bin/env python3
"""
Setup script for JSON-Tables package.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "JSON-Tables: A minimal format for representing tabular data in JSON"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['pandas>=1.0.0']

setup(
    name="jsontables",
    version="0.1.0",
    author="Mitch Haile",
    author_email="mitch.haile@gmail.com",
    description="A minimal format for representing tabular data in JSON",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/featrix/json-tables",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Filters",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "jsontables=jsontables.cli:main",
            "json-tables=jsontables.cli:main",
        ],
    },
    keywords="json tables dataframe pandas cli pretty-print tabular data",
    project_urls={
        "Bug Reports": "https://github.com/featrix/json-tables/issues",
        "Source": "https://github.com/featrix/json-tables",
        "Documentation": "https://github.com/featrix/json-tables",
    },
) 