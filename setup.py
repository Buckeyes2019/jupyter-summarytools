from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="summarytools",
    version="0.3.1",
    description="Summarytools for Jupyter notebooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/6chaoran/jupyter-summarytools",
    author="Liu Chaoran",
    author_email="6chaoran@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="data analysis, summary statistics, jupyter",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=[
        "pandas>=1.4.0",
        "ipython>=7.20.0",
        "numpy>=1.18.5",
        "matplotlib>=3.3.0"
    ],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["pytest", "coverage"],
    },
    project_urls={
        "Bug Reports": "https://github.com/6chaoran/jupyter-summarytools/issues",
        "Source": "https://github.com/6chaoran/jupyter-summarytools",
    },
)
