#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="vscode_workspace_config_generator",
    version="1.1.0",
    description="Generate VS Code workspace files for multi-package projects",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'generate-vscode-workspace-config=workspace_generator.cli:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)