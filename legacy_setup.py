# setup.py - Package setup for PyLatro
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = (
    readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
)

setup(
    name="pylatro",
    version="0.1.0",
    author="Huy Tran(Hakunok) & Aekn Admal(aekn)",
    author_email="huytran8392@gmail.com",
    description="A Balatro-inspired poker roguelite game in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hakunok/pylatro",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pylatro=pylatro.ui_cli:main",
            "pylatro-gui=pylatro.ui_gui:main",
        ],
        "gui_scripts": [
            "pylatro-gui=pylatro.ui_gui:main",
        ],
    },
    install_requires=[
        # No external dependencies needed!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
)
