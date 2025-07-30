"""
Setup script for OmniParser MCP Server.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        "mcp>=1.0.0",
        "torch",
        "torchvision", 
        "transformers",
        "ultralytics==8.3.70",
        "opencv-python",
        "pillow",
        "numpy",
        "pyautogui",
        "screeninfo",
        "easyocr",
        "supervision==0.18.0",
        "timm",
        "einops==0.8.0",
        "accelerate",
        "pydantic>=2.0.0",
        "typing-extensions",
    ]

setup(
    name="omniparser-mcp-server",
    version="0.1.0",
    description="MCP Server for UI automation using OmniParser model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/omniparser-mcp-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio", 
            "black",
            "isort",
            "mypy",
            "pre-commit",
        ],
        "windows": [
            "pywin32",
            "psutil",
        ]
    },
    entry_points={
        "console_scripts": [
            "omniparser-mcp-server=omniparser_mcp.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Desktop Environment",
    ],
    keywords="mcp, ui automation, screen parsing, omniparser, computer vision",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/omniparser-mcp-server/issues",
        "Source": "https://github.com/yourusername/omniparser-mcp-server",
        "Documentation": "https://github.com/yourusername/omniparser-mcp-server/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)
