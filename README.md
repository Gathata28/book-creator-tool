# Book Creator Tool 📚

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive platform for crafting professional coding books with AI and Large Language Model (LLM) integration. This tool streamlines the entire book creation process from outline to publication.

## ✨ Features

### 🤖 AI-Powered Content Generation
- **Automated Outline Generation**: Create comprehensive book structures with AI-generated chapter and section outlines
- **Intelligent Content Writing**: Generate high-quality technical content for chapters and sections
- **Smart Code Examples**: LLM-powered code generation with detailed explanations
- **Exercise Creation**: Automatically create coding exercises with hints and solutions

### 📝 AI-Assisted Editing
- **Grammar and Style Checking**: Advanced grammar and style analysis using LLM
- **Content Improvement**: AI-powered suggestions to enhance clarity, engagement, and readability
- **Technical Accuracy Review**: Verify technical correctness and identify outdated practices
- **Automatic Fixing**: One-click grammar and style corrections

### 🎓 Interactive Learning Modules
- **Code Playgrounds**: Interactive code examples with syntax highlighting
- **Exercises with Solutions**: Step-by-step exercises with hints and complete solutions
- **Quiz Generation**: Create engaging quizzes and assessments

### 📤 Customizable Publishing
- **Multiple Export Formats**: 
  - HTML (with beautiful, responsive design)
  - PDF (professional book layout)
  - EPUB (e-reader compatible)
  - Markdown (portable and editable)
- **Custom Templates**: Fully customizable formatting and styling
- **Syntax Highlighting**: Beautiful code presentation across all formats

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key or Anthropic API key for LLM features

### Install from Source

```bash
# Clone the repository
git clone https://github.com/Gathata28/book-creator-tool.git
cd book-creator-tool

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Environment Setup

Set up your API keys:

```bash
# For OpenAI
export OPENAI_API_KEY='your-api-key-here'

# OR for Anthropic Claude
export ANTHROPIC_API_KEY='your-api-key-here'
```

## 📖 Quick Start

### 1. Create a Book Outline

```bash
book-creator create \
  --topic "Python Web Development" \
  --chapters 12 \
  --language Python \
  --audience "intermediate developers" \
  --output my-book.json
```

### 2. Generate Content

```bash
# Generate all chapters
book-creator generate --input my-book.json

# Or generate a specific chapter
book-creator generate --input my-book.json --chapter 3
```

### 3. Check and Improve

```bash
# Check grammar and style
book-creator check --input my-book.json

# Auto-fix issues
book-creator check --input my-book.json --fix

# Improve content quality
book-creator improve \
  --input my-book.json \
  --chapter 5 \
  --focus clarity
```

### 4. Export Your Book

```bash
# Export to HTML
book-creator export --input my-book.json --format html

# Export to PDF
book-creator export --input my-book.json --format pdf

# Export to EPUB
book-creator export --input my-book.json --format epub

# Export to Markdown
book-creator export --input my-book.json --format markdown
```

## 💡 Usage Examples

### Generate a Code Example

```bash
book-creator code-example \
  --concept "async/await in Python" \
  --language python \
  --difficulty intermediate
```

### Create a Coding Exercise

```bash
book-creator exercise \
  --topic "List Comprehensions" \
  --language python \
  --difficulty beginner
```

### View Book Information

```bash
book-creator info my-book.json
```

## 🏗️ Architecture

```
book-creator-tool/
├── src/book_creator/
│   ├── models/           # Data models (Book, Chapter, Section)
│   ├── generators/       # Content generation modules
│   │   ├── outline_generator.py
│   │   ├── content_generator.py
│   │   └── code_generator.py
│   ├── editors/          # Editing and improvement tools
│   │   ├── grammar_checker.py
│   │   └── content_improver.py
│   ├── formatters/       # Export formatters
│   │   ├── html_formatter.py
│   │   ├── pdf_formatter.py
│   │   ├── epub_formatter.py
│   │   └── markdown_formatter.py
│   ├── utils/            # Utilities (LLM client, helpers)
│   └── cli.py           # Command-line interface
```

## 🎯 Use Cases

1. **Technical Authors**: Create comprehensive programming books with AI assistance
2. **Educators**: Generate course materials and textbooks for programming courses
3. **Documentation Teams**: Produce high-quality technical documentation
4. **Online Course Creators**: Build structured learning content
5. **Open Source Projects**: Create professional documentation and guides

## 🔧 Configuration

### LLM Provider Selection

You can choose between OpenAI and Anthropic:

```bash
# Use OpenAI (default)
book-creator create --provider openai --topic "Your Topic"

# Use Anthropic Claude
book-creator create --provider anthropic --topic "Your Topic"
```

### Customization

The tool supports customization through:
- Custom templates for different export formats
- Configurable content generation parameters
- Adjustable difficulty levels and target audiences
- Multiple programming language support

## 📚 API Usage

You can also use the Book Creator Tool programmatically:

```python
from book_creator.models.book import Book, Chapter, Section
from book_creator.generators.outline_generator import OutlineGenerator
from book_creator.generators.content_generator import ContentGenerator
from book_creator.formatters.html_formatter import HTMLFormatter

# Create outline
generator = OutlineGenerator()
book = generator.generate_outline(
    topic="Python Data Science",
    num_chapters=10,
    programming_language="Python"
)

# Generate content
content_gen = ContentGenerator()
for chapter in book.chapters:
    content_gen.generate_complete_chapter(chapter)

# Export to HTML
formatter = HTMLFormatter()
formatter.format(book, "output/my-book.html")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI and Anthropic for providing excellent LLM APIs
- The Python community for amazing libraries and tools

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Happy Book Creating! 📖✨**
