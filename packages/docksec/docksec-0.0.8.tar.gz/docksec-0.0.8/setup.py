from setuptools import setup,find_packages

setup(
    name="docksec",
    version="0.0.8",
    description="AI-Powered Docker Security Analyzer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Advait Patel",
    url="https://github.com/advaitpatel/DockSec",
    packages=find_packages(),
    package_data={
        'docksec': ['*.py'],  # Include all Python files
    },
    py_modules=["docksec", "main", "docker_scanner", "utils", "config", "setup_external_tools"],
    entry_points={
        "console_scripts": [
            "docksec=docksec.docksec:main",
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
)