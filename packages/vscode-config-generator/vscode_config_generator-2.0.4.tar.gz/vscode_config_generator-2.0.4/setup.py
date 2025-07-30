#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="vscode_config_generator",
    version="2.0.4",
    description="Generate VS Code configurations for projects",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'generate-vscode-config=vscode_config_generator.cli:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)