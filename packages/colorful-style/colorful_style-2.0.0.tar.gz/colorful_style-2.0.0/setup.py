from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="colorful-style",
    version="2.0.0",
    author="QuangThangCoder",
    author_email="quangthangcoder@gmail.com",
    description="A beautiful and advanced Python library for creating stunning TUI designs with enhanced colors and effects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/giakietdev/colorful-style",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Text Processing :: Fonts",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "colorama>=0.4.6",
        "termcolor>=2.3.0",
        "rich>=13.0.0",
        "pyfiglet>=1.0.0",
        "art>=6.1",
        "blessed>=1.20.0",
        "cursor>=1.3.5",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "colorful-style=demo:main",
        ],
    },
    keywords="terminal, colors, animations, effects, tui, cli, ascii-art, banners, boxes, interactive",
    project_urls={
        "Bug Reports": "https://github.com/giakietdev/colorful-style/issues",
        "Source": "https://github.com/giakietdev/colorful-style",
        "Documentation": "https://github.com/giakietdev/colorful-style#readme",
    },
) 