#!/usr/bin/env python3
from setuptools import setup, find_packages
from wl_version_manager import VersionManager


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="wl_config_manager",
    version=VersionManager.get_version(),
    author="Chris Watkins",
    author_email="chris@watkinslabs.com",
    description="A flexible configuration manager for Python applications with .env support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/watkinslabs/config_manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyyaml>=5.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.9",
        ],
    },
    entry_points={
        'console_scripts': [
            'wl_config_manager=wl_config_manager.cli:main',
        ],
    },
    keywords="configuration config yaml json ini environment variables dotenv env settings",
    project_urls={
        "Bug Tracker": "https://github.com/watkinslabs/config_manager/issues",
        "Documentation": "https://github.com/watkinslabs/config_manager",
        "Source Code": "https://github.com/watkinslabs/config_manager",
        "Changelog": "https://github.com/watkinslabs/config_manager/blob/main/CHANGELOG.md",
    },
    license="MIT",
)