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

### ✏️ Automated Book Editing (NEW!)
- **Content Consistency Checking**: Detect and fix inconsistent terminology and formatting across chapters
- **Cross-Reference Validation**: Automatically validate internal references and links
- **Index Generation**: Create comprehensive indexes of important terms and concepts
- **Glossary Generation**: AI-powered glossary creation for technical terms
- **Learning Objectives**: Automatically generate learning objectives for each chapter
- **Code Formatting**: Batch format all code examples to follow style guides (PEP 8, Google, Airbnb, etc.)
- **Enhanced Code Comments**: Improve code examples with AI-generated helpful comments

### 🌐 Extended LLM Support (NEW!)
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Google**: Gemini Pro
- **Cohere**: Command models
- **Mistral AI**: Mistral Medium and other models
- **HuggingFace**: Access to thousands of open-source models
- **Ollama**: Support for local LLM models (llama2, mistral, etc.)

### 🎓 Interactive Learning Modules
- **Code Playgrounds**: Interactive code examples with syntax highlighting
- **Exercises with Solutions**: Step-by-step exercises with hints and complete solutions
- **Quiz Generation**: Create engaging quizzes and assessments

### 📤 Customizable Publishing
- **Multiple Export Formats**: 
  - HTML (with beautiful, responsive design)
  - PDF (professional book layout via FPDF)
  - **PDF-Pandoc (NEW!)**: High-quality PDF with Pandoc
    - Strict Markdown validation
    - Color-coded syntax highlighting
    - Multiple themes (tango, pygments, kate, etc.)
    - Professional typography with XeLaTeX
  - EPUB (e-reader compatible)
  - Markdown (portable and editable)
- **Custom Templates**: Fully customizable formatting and styling
- **Syntax Highlighting**: Beautiful code presentation across all formats

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- **Pandoc** (for high-quality PDF generation) - [Install Guide](https://pandoc.org/installing.html)
- **XeLaTeX** (for Pandoc PDF generation) - Usually included with TeX Live
- API key for at least one LLM provider:
  - OpenAI API key
  - Anthropic API key
  - Google API key (for Gemini)
  - Cohere API key
  - Mistral API key
  - HuggingFace API key
  - Or use Ollama for local models (no API key needed)

### Install Pandoc (Required for PDF-Pandoc export)

```bash
# Ubuntu/Debian
sudo apt-get install pandoc texlive-xetex

# macOS
brew install pandoc
brew install --cask mactex

# Windows
# Download from https://pandoc.org/installing.html
# Download MiKTeX from https://miktex.org/
```

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

Set up your API keys (choose one or more):

```bash
# For OpenAI
export OPENAI_API_KEY='your-api-key-here'

# For Anthropic Claude
export ANTHROPIC_API_KEY='your-api-key-here'

# For Google Gemini
export GOOGLE_API_KEY='your-api-key-here'

# For Cohere
export COHERE_API_KEY='your-api-key-here'

# For Mistral AI
export MISTRAL_API_KEY='your-api-key-here'

# For HuggingFace
export HUGGINGFACE_API_KEY='your-api-key-here'

# For Ollama (local models) - no API key needed, just install Ollama
# Visit https://ollama.ai to install
```

## 📖 Quick Start

### 1. Create a Book Outline

```bash
book-creator create \
  --topic "Python Web Development" \
  --chapters 12 \
  --language Python \
  --audience "intermediate developers" \
  --provider openai \
  --output my-book.json

# Or use a different LLM provider
book-creator create \
  --topic "Rust Programming" \
  --provider google \
  --output rust-book.json

# Or use local models with Ollama
book-creator create \
  --topic "JavaScript Fundamentals" \
  --provider ollama \
  --output js-book.json
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

### 4. Automated Book Editing (NEW!)

```bash
# Validate cross-references
book-creator validate-references --input my-book.json

# Check content consistency
book-creator check-consistency --input my-book.json

# Generate an index
book-creator generate-index --input my-book.json

# Generate a glossary of technical terms
book-creator generate-glossary --input my-book.json --provider openai

# Add learning objectives to chapters
book-creator add-objectives --input my-book.json --provider openai

# Format all code to follow a style guide
book-creator format-code \
  --input my-book.json \
  --style "PEP 8" \
  --provider openai
```

### 5. Export Your Book

```bash
# Export to HTML
book-creator export --input my-book.json --format html

# Export to PDF (basic)
book-creator export --input my-book.json --format pdf

# Export to PDF with Pandoc (high-quality, syntax highlighting) 🆕
book-creator export --input my-book.json --format pdf-pandoc --theme tango

# Export to PDF with Pandoc (strict validation)
book-creator export --input my-book.json --format pdf-pandoc --strict --theme pygments

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
