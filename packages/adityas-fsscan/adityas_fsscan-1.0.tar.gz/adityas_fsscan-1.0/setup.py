from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="adityas-fsscan",
    version="1.0",
    packages=find_packages(),
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "fsscan=src.main:main",
        ],
    },
)
