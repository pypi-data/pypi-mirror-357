from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = Path("README.md").read_text(encoding="utf-8")
setup(
    name="contextdict",
    version="0.1.1",
    author="Yerram Mahendra Reddy",
    author_email="yerram.mahi@gmail.com",
    description="A context-aware in-memory dictionary with Redis support, TTLs, and versioning.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "redis>=4.0.0",
    ],
)
