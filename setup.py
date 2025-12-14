from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="book-creator-tool",
    version="0.1.0",
    author="Book Creator Team",
    description="A platform for crafting coding books with AI and LLM integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "markdown>=3.5",
        "PyPDF2>=3.0.0",
        "fpdf2>=2.7.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "ebooklib>=0.18",
        "Jinja2>=3.1.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "pygments>=2.17.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "langchain-anthropic>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "book-creator=book_creator.cli:main",
        ],
    },
)
