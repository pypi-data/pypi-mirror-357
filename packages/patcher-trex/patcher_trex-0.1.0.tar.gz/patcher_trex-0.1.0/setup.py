from setuptools import setup, find_packages

# Read the contents of your README file for long description
# Uncomment and modify this if you have a README.md file:
# with open("README.md", "r", encoding="utf-8") as fh:
# long_description = fh.read()

setup(
    # PACKAGE IDENTIFICATION
    name="patcher-trex",  # Changed to unique name - must be unique on PyPI
    version="0.1.0",  # Update this for each release (e.g., 0.1.1, 0.2.0)

    # PACKAGE DISCOVERY
    packages=find_packages(),  # Automatically finds all packages in your project
    # Alternative: packages=["your_package_name"] if you want to specify manually

    # DEPENDENCIES
    install_requires=[
        # Add your project dependencies here, for example:
        "typer",           # For CLI functionality
        "google-generativeai",  # For Gemini AI integration
        "requests",        # For HTTP requests (Stack Overflow API)
        "rich",           # For beautiful terminal output (if using)
        # "beautifulsoup4", # For web scraping (if needed)
        # "openai",         # If using OpenAI instead of Gemini
    ],

    # ENTRY POINTS - This creates the CLI commands
    entry_points={
        "console_scripts": [
            # Format: "command-name=package.module:function"
            "patchtool=patchtool:app",  # Adjust according to your project structure
            # Example: if your main CLI function is in patchtool/cli.py as main():
            # "patchtool=patchtool.cli:main",
        ],
    },

    # METADATA
    author="Aayushman Katariya",  # Your name
    author_email="erenyeager545w@gmail.com",  # Your email

    # DESCRIPTION
    description="An AI-powered CLI tool to enhance your coding workflow by fixing errors, modifying code, adding comments, and generating files.",
    
    # LONG DESCRIPTION (shows on PyPI page)
    long_description="""# AI Patch Tool 🛠️✨

An AI-powered CLI tool to enhance your coding workflow by fixing errors, modifying code, adding comments, and even generating full files — all powered by Python, Typer, and Google's Gemini API.

## 🔍 Features

- 📌 `searcherr`: Finds errors in your code and searches Stack Overflow for relevant solutions
- 🔧 `fix`: Automatically detects and corrects errors in your script using AI
- ✏️ `modify`: Take user input and modify code behavior accordingly
- 💡 `query`: Generate code files based on user intent and desired filetype
- 💬 `addComments`: Automatically add meaningful comments to code without changing its functionality

## 📦 Installation

```bash
pip install ai-patch-tool
```

## 🚀 Usage

```bash
# Fix errors in your code
patchtool fix script.py

# Search for error solutions
patchtool searcherr script.py

# Modify code behavior
patchtool modify script.py "add error handling"

# Generate new code files
patchtool query "create a web scraper" --filetype py

# Add comments to existing code
patchtool addComments script.py
```

## 🔧 Setup

Before using, make sure to set your Google Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```
""",
    long_description_content_type="text/markdown",  # Specify that long_description is in Markdown

    # PROJECT URLS
    url="https://github.com/aayush00700/Patcher",  # Main project URL
    project_urls={  # Additional URLs
        "Bug Reports": "https://github.com/aayush00700/Patcher/issues",
        "Source": "https://github.com/aayush00700/Patcher",
        "Documentation": "https://github.com/aayush00700/Patcher#readme",
    },

    # CLASSIFIERS - Help users find your project
    classifiers=[
        "Development Status :: 3 - Alpha",  # Change based on your project maturity
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    
    # PYTHON VERSION REQUIREMENT
    python_requires=">=3.7",
    
    # KEYWORDS - Help with discoverability
    keywords="ai, cli, code-fix, debugging, patch, automation, gemini, stack-overflow",
    
    # LICENSE
    license="MIT",  # Make sure you have a LICENSE file in your project
    
    # INCLUDE ADDITIONAL FILES
    include_package_data=True,  # Include files specified in MANIFEST.in
    
    # OPTIONAL: Development dependencies
    extras_require={
        "dev": [
            "pytest",     # For testing
            "black",      # For code formatting
            "flake8",     # For linting
            "mypy",       # For type checking
        ],
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },
)