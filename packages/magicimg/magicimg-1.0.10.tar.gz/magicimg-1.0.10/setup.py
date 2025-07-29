#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script cho package magicimg - Fixed version with proper module inclusion
"""

from setuptools import setup, find_packages
import codecs
import os
import io

here = os.path.abspath(os.path.dirname(__file__))

# Lấy phiên bản từ __init__.py
def get_version():
    try:
        with open(os.path.join(here, "magicimg", "__init__.py"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
        return "0.1.3"
    except:
        return "0.1.3"

# Đọc README
def read_readme():
    try:
        with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
            return f.read()
    except:
        return "Advanced image preprocessing package for OCR and computer vision"

def read_requirements():
    """Đọc requirements từ file"""
    try:
        with open('requirements.txt') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        return [
            "numpy>=1.19.0",
            "opencv-python>=4.5.0",
            "matplotlib>=3.3.0",
            "pytesseract>=0.3.8",
            "Pillow>=8.0.0",
            "scikit-image>=0.18.0",
            "tqdm>=4.62.0"
        ]

def read_file(filename):
    """Đọc file với encoding UTF-8"""
    with io.open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Đọc requirements
requirements = read_requirements()

setup(
    name="magicimg",
    version="1.0.10",
    description="Thư viện xử lý và tiền xử lý ảnh cho OCR",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="MagicImg Team",
    author_email="contact@magicimg.com",
    url="https://github.com/magicimg/magicimg",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "Pillow>=8.0.0",
        "pytesseract>=0.3.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2"
        ]
    },
    entry_points={
        "console_scripts": [
            "magicimg=magicimg.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False
) 