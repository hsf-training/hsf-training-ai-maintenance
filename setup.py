"""Setup script for HSF Training AI Maintenance Agent."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README_AGENT.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="hsf-training-ai-agent",
    version="0.1.0",
    author="HSF Training Team",
    author_email="hsf-training@cern.ch",
    description="AI agent for maintaining HSF training repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hsf-training/hsf-training-ai-maintenance",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hsf-training-agent=hsf_training_agent.main:cli",
        ],
    },
    keywords="hsf training physics education ai maintenance",
    project_urls={
        "Documentation": "https://hsf-training.github.io/",
        "Source": "https://github.com/hsf-training/hsf-training-ai-maintenance",
        "Tracker": "https://github.com/hsf-training/hsf-training-ai-maintenance/issues",
    },
)