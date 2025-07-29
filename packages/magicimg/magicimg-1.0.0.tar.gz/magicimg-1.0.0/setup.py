#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script cho package magicimg - Fixed version with proper module inclusion
"""

from setuptools import setup, find_packages
import codecs
import os
import subprocess
import sys
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

def check_gpu_available():
    """Kiểm tra xem có GPU không bằng cách thử import torch và kiểm tra CUDA"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        try:
            # Thử chạy nvidia-smi để kiểm tra GPU
            subprocess.check_output('nvidia-smi')
            return True
        except:
            return False

def read_requirements(gpu=False):
    """Đọc requirements từ file phù hợp"""
    try:
        with open('requirements-gpu.txt' if gpu else 'requirements.txt') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        if gpu:
            return [
                "numpy>=1.19.0",
                "opencv-python>=4.5.0",
                "matplotlib>=3.3.0",
                "pytesseract>=0.3.8",
                "Pillow>=8.0.0",
                "torch>=1.9.0",
                "torchvision>=0.10.0",
                "scikit-image>=0.18.0",
                "tqdm>=4.62.0"
            ]
        else:
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

# Kiểm tra GPU và chọn requirements phù hợp
has_gpu = check_gpu_available()
requirements = read_requirements(gpu=has_gpu)

setup(
    name="magicimg",
    version="1.0.0",
    description="Thư viện xử lý ảnh thông minh với hỗ trợ GPU tự động",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="MagicImg Team",
    author_email="contact@magicimg.com",
    url="https://github.com/magicimg/magicimg",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2"
        ],
        "gpu": [
            "torch>=1.9.0",
            "torchvision>=0.10.0"
        ] if not has_gpu else []
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