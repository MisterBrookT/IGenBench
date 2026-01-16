"""
Minimal setup.py for backward compatibility.

Modern configuration is in pyproject.toml.
This file is kept for legacy tools that don't support PEP 517/518.
"""

from setuptools import setup

# All configuration is in pyproject.toml
# This file just ensures compatibility with older pip/setuptools versions
setup()
