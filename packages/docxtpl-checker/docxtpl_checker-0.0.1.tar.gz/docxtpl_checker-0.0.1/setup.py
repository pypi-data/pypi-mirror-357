#!/usr/bin/env python3
"""
Setup script for docxtpl_checker package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="docxtpl-checker",
    version="0.0.1",
    author="Docxtpl Template Checker",
    author_email="vic.wangyifan@gmail.com",
    description="A comprehensive validation tool for python-docx-template (docxtpl) Word templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VicBioDev/docxtpl_checker",
    packages=find_packages(),
    py_modules=["docxtpl_checker"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Text Processing :: Markup",
        "Topic :: Office/Business :: Office Suites",
    ],
    python_requires=">=3.6",
    install_requires=[
        "jinja2>=2.10",
    ],
    entry_points={
        "console_scripts": [
            "docxtpl-checker=docxtpl_checker:main",
        ],
    },
    keywords="docxtpl jinja2 template validation word document docx",
    project_urls={
        "Bug Reports": "https://github.com/VicBioDev/docxtpl_checker/issues",
        "Source": "https://github.com/VicBioDev/docxtpl_checker",
        "Documentation": "https://github.com/VicBioDev/docxtpl_checker#readme",
    },
    include_package_data=True,
    zip_safe=False,
)