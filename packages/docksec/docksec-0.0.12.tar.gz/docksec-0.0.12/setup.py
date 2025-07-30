from setuptools import setup
import os

# Get all Python files in the current directory
py_modules = []
for file in os.listdir('.'):
    if file.endswith('.py') and file != 'setup.py':
        py_modules.append(file[:-3])  # Remove .py extension

setup(
    name="docksec",
    version="0.0.12",  # Increment version
    description="AI-Powered Docker Security Analyzer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Advait Patel",
    url="https://github.com/advaitpatel/DockSec",
    py_modules=py_modules,  # Include all Python files
    entry_points={
        "console_scripts": [
            "docksec=docksec:main",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/advaitpatel/DockSec/issues",
        "Documentation": "https://github.com/advaitpatel/DockSec/blob/main/README.md",
        "Source Code": "https://github.com/advaitpatel/DockSec",
    },
    python_requires=">=3.12",
    install_requires=[
        "langchain",
        "langchain-openai",
        "python-dotenv",
        "pandas",
        "tqdm",
        "colorama",
        "rich",
        "fpdf",
        "setuptools",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    # Ensure all Python files are included in the distribution
    package_data={
        '': ['*.py'],
    },
)