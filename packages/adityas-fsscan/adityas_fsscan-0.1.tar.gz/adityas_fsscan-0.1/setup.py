from setuptools import setup, find_packages

setup(
    name="adityas-fsscan",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "fsscan=src.main:main",
        ],
    },
)
