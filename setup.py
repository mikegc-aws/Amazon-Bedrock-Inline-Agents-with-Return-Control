from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bedrock-agents-sdk",
    version="0.1.0",
    author="Amazon Web Services",
    author_email="aws@amazon.com",
    description="A Python SDK for Amazon Bedrock Agents with Return Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aws-samples/bedrock-agents-sdk",
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
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black",
            "isort",
            "flake8",
        ],
    },
) 