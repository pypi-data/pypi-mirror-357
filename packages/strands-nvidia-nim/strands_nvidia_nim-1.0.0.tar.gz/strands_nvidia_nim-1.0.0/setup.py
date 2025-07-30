"""Setup script for strands-nvidia-nim package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="strands-nvidia-nim",
    version="1.0.0",
    author="Thiago S Shimada Ramos",
    author_email="tech@nikkei.one",
    description="Nvidia NIM provider for Strands Agents SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiago4go/strands-nvidia-nim",
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
    ],
    python_requires=">=3.8",
    install_requires=[
        "strands>=0.1.0",
        "litellm>=1.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
    },
    keywords="strands, nvidia, nim, llm, ai, agents",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/strands-nvidia-nim/issues",
        "Source": "https://github.com/yourusername/strands-nvidia-nim",
        "Documentation": "https://github.com/yourusername/strands-nvidia-nim#readme",
    },
)
