#!/usr/bin/env python3
"""
Setup script for Chrome Custom Devices Manager
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chrome-custom-devices",
    version="1.0.9",
    author="Hatim Makki",
    author_email="hatim.makki@gmail.com",
    description="A comprehensive tool to add custom device presets to Chrome DevTools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hatimmakki/chrome-custom-devices",
    py_modules=["chrome_devices_manager", "devices"],
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "chrome-devices=chrome_devices_manager:main",
        ],
    },
    keywords="chrome devtools devices emulation responsive web development",
    project_urls={
        "Bug Reports": "https://github.com/hatimmakki/chrome-custom-devices/issues",
        "Source": "https://github.com/hatimmakki/chrome-custom-devices",
    },
)
