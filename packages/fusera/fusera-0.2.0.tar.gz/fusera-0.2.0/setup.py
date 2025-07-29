# ABOUTME: Python package setup configuration for Fusera SDK
# ABOUTME: Enables pip installation of the fusera package for PyTorch model compilation

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fusera",
    version="0.2.0",  # Bump version
    author="Fusera Team",
    author_email="team@fusera.dev",
    description="Submit PyTorch models for cloud compilation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.5.0",
        "requests>=2.25.0",
    ],
)