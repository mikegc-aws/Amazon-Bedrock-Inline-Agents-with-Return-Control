from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bedrock-agents-sdk",
    version="0.1.0",
    author="Mike Chambers",
    author_email="mikegc@amazon.com",
    description="A Python SDK for Amazon Bedrock Agents with Return Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mikegc-aws/Amazon-Bedrock-Inline-Agents-with-Return-Control",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.37.0",
        "botocore>=1.37.0",
        "pydantic==2.10.6",
        "pydantic_core==2.27.2",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black",
            "isort",
            "flake8",
        ],
        "docs": [
            "sphinx>=8.2.0",
            "sphinx-rtd-theme>=3.0.0",
        ],
    },
) 