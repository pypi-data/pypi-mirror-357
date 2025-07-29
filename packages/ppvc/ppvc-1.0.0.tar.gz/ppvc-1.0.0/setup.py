import pathlib
import os

from setuptools import setup, find_packages

PATH = pathlib.Path(__file__).parent

# The text of the README file
README = open(os.path.join(PATH, "README.md")).read()

setup(
    name="ppvc",
    version="1.0.0",
    author="Rapid Rabbit Software",
    author_email="python@rapidrabbit.software",
    license="BSD-2",
    description="A command-line utility for listing Python package versions from PyPI",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rapidrabbitsoft/ppvc",
    packages=find_packages(),
    install_requires=[
        "packaging>=23.0",
        "rich>=13.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "ppvc=ppvc.ppvc:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/rapidrabbitsoft/ppvc/issues",
        "Source": "https://github.com/rapidrabbitsoft/ppvc",
    },
)