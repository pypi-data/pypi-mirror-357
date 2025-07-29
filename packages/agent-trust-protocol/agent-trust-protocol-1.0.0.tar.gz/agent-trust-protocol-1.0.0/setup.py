"""
Setup script for Agent Trust Protocol Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Agent Trust Protocol - Python Implementation"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="agent-trust-protocol",
    version="1.0.0",
    author="Agent Trust Protocol Team",
    author_email="team@agent-trust-protocol.org",
    description="A comprehensive security and provenance framework for secure, trustworthy communication between autonomous AI agents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/agent-trust-protocol/agent-trust-protocol",
    project_urls={
        "Bug Reports": "https://github.com/agent-trust-protocol/agent-trust-protocol/issues",
        "Source": "https://github.com/agent-trust-protocol/agent-trust-protocol",
        "Documentation": "https://github.com/agent-trust-protocol/agent-trust-protocol/docs",
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
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "crypto": [
            "pycryptodome>=3.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "atp-demo=atp.examples.async_demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "agent",
        "trust",
        "protocol",
        "security",
        "cryptography",
        "async",
        "communication",
        "autonomous",
        "ai",
        "distributed",
    ],
) 