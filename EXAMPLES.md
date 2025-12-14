# Examples

This directory contains examples of using the Book Creator Tool.

## Example 1: Creating a Python Web Development Book

```bash
# Step 1: Create the outline
book-creator create \
  --topic "Modern Python Web Development with FastAPI" \
  --chapters 15 \
  --language Python \
  --audience "intermediate to advanced developers" \
  --output examples/fastapi-book.json

# Step 2: Generate content for all chapters
book-creator generate --input examples/fastapi-book.json

# Step 3: Check grammar and fix issues
book-creator check --input examples/fastapi-book.json --fix

# Step 4: Improve specific chapters
book-creator improve \
  --input examples/fastapi-book.json \
  --chapter 5 \
  --focus engagement

# Step 5: Export to multiple formats
book-creator export --input examples/fastapi-book.json --format html
book-creator export --input examples/fastapi-book.json --format pdf
book-creator export --input examples/fastapi-book.json --format epub
```

## Example 2: Generating Code Examples

```bash
# Generate an async/await example
book-creator code-example \
  --concept "asynchronous web scraping with aiohttp" \
  --language python \
  --difficulty advanced

# Generate a React hooks example
book-creator code-example \
  --concept "custom hooks in React" \
  --language javascript \
  --difficulty intermediate
```

## Example 3: Creating Exercises

```bash
# Create a beginner exercise
book-creator exercise \
  --topic "for loops and iteration" \
  --language python \
  --difficulty beginner

# Create an advanced exercise
book-creator exercise \
  --topic "implementing a binary search tree" \
  --language python \
  --difficulty advanced
```

## Example 4: Programmatic Usage

```python
from book_creator import (
    Book, Chapter, Section,
    OutlineGenerator, ContentGenerator, CodeGenerator,
    HTMLFormatter, PDFFormatter
)

# Create a book manually
book = Book(
    title="Learn Rust Programming",
    author="AI Book Creator",
    programming_language="Rust",
    target_audience="beginners"
)

# Add chapters
chapter1 = Chapter(
    title="Getting Started with Rust",
    number=1
)
chapter1.add_section(Section(title="Installing Rust"))
chapter1.add_section(Section(title="Your First Rust Program"))
book.add_chapter(chapter1)

# Generate content
content_gen = ContentGenerator()
content_gen.generate_complete_chapter(chapter1, programming_language="Rust")

# Add code examples
code_gen = CodeGenerator()
for section in chapter1.sections:
    example = code_gen.generate_code_with_explanation(
        section.title,
        language="rust"
    )
    section.add_code_example(
        example['code'],
        example['language'],
        example['explanation']
    )

# Export
html_formatter = HTMLFormatter()
html_formatter.format(book, "output/rust-book.html")

pdf_formatter = PDFFormatter()
pdf_formatter.format(book, "output/rust-book.pdf")

# Save the book structure
book.save("output/rust-book.json")
```

## Example 5: Custom Workflow

```python
from book_creator import (
    Book, OutlineGenerator, ContentGenerator,
    GrammarChecker, ContentImprover, HTMLFormatter
)
from book_creator.utils import LLMClient, LLMConfig, LLMProvider

# Configure LLM
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000
)
llm_client = LLMClient(config)

# Create outline
outline_gen = OutlineGenerator(llm_client)
book = outline_gen.generate_outline(
    topic="Machine Learning with PyTorch",
    num_chapters=12,
    programming_language="Python",
    target_audience="data scientists"
)

# Generate content for first 3 chapters
content_gen = ContentGenerator(llm_client)
for chapter in book.chapters[:3]:
    print(f"Generating Chapter {chapter.number}: {chapter.title}")
    content_gen.generate_complete_chapter(chapter)

# Check and improve quality
checker = GrammarChecker(llm_client)
improver = ContentImprover(llm_client)

for chapter in book.chapters[:3]:
    # Check grammar in introduction
    if chapter.introduction:
        result = checker.check_grammar(chapter.introduction)
        if result['issues']:
            chapter.introduction = checker.fix_grammar(chapter.introduction)
    
    # Improve sections
    for section in chapter.sections:
        if section.content:
            improver.improve_section(section, focus="clarity")

# Export
formatter = HTMLFormatter()
formatter.format(book, "output/pytorch-book.html")

print("Book created successfully!")
```

## Example 6: Batch Processing

```python
import os
from book_creator import Book, ContentGenerator, PDFFormatter

# Process multiple book files
book_files = [
    "books/python-basics.json",
    "books/web-development.json",
    "books/data-structures.json"
]

content_gen = ContentGenerator()
pdf_formatter = PDFFormatter()

for book_file in book_files:
    print(f"Processing: {book_file}")
    
    # Load book
    book = Book.load(book_file)
    
    # Generate missing content
    for chapter in book.chapters:
        for section in chapter.sections:
            if not section.content:
                content_gen.generate_section_content(section)
    
    # Export to PDF
    pdf_name = os.path.basename(book_file).replace('.json', '.pdf')
    pdf_formatter.format(book, f"output/{pdf_name}")
    
    # Save updated book
    book.save(book_file)
    
    print(f"✓ Completed: {book.title}")
```

## Example 7: Using Different LLM Providers (NEW!)

```bash
# Create a book using OpenAI GPT-4
book-creator create \
  --topic "Machine Learning Fundamentals" \
  --provider openai \
  --output ml-book-openai.json

# Create a book using Anthropic Claude
book-creator create \
  --topic "Data Science with Python" \
  --provider anthropic \
  --output ds-book-claude.json

# Create a book using Google Gemini
book-creator create \
  --topic "Web Development with React" \
  --provider google \
  --output react-book-gemini.json

# Create a book using Cohere
book-creator create \
  --topic "Natural Language Processing" \
  --provider cohere \
  --output nlp-book-cohere.json

# Create a book using Mistral AI
book-creator create \
  --topic "Deep Learning Basics" \
  --provider mistral \
  --output dl-book-mistral.json

# Create a book using local Ollama models (no API key needed!)
book-creator create \
  --topic "JavaScript Fundamentals" \
  --provider ollama \
  --output js-book-local.json

# Generate content with a specific provider
book-creator generate \
  --input my-book.json \
  --provider google \
  --chapter 3
```

## Example 8: Automated Book Editing (NEW!)

```bash
# Validate all cross-references in your book
book-creator validate-references --input my-book.json

# Check for content consistency issues
book-creator check-consistency --input my-book.json

# Generate an index of important terms
book-creator generate-index \
  --input my-book.json \
  --provider openai

# Generate a glossary with AI-powered definitions
book-creator generate-glossary \
  --input my-book.json \
  --provider anthropic

# Add learning objectives to all chapters
book-creator add-objectives \
  --input my-book.json \
  --provider google

# Format all code examples to follow PEP 8
book-creator format-code \
  --input python-book.json \
  --style "PEP 8" \
  --provider openai

# Format JavaScript code to follow Airbnb style guide
book-creator format-code \
  --input js-book.json \
  --style "Airbnb" \
  --provider openai
```

## Example 9: Complete Workflow with New Features

```bash
# Step 1: Create book with Google Gemini
book-creator create \
  --topic "Rust Programming Guide" \
  --chapters 12 \
  --language Rust \
  --provider google \
  --output rust-book.json

# Step 2: Generate content for all chapters
book-creator generate \
  --input rust-book.json \
  --provider google

# Step 3: Add learning objectives
book-creator add-objectives \
  --input rust-book.json \
  --provider google

# Step 4: Generate glossary
book-creator generate-glossary \
  --input rust-book.json \
  --provider google

# Step 5: Generate index
book-creator generate-index \
  --input rust-book.json \
  --provider google

# Step 6: Check consistency
book-creator check-consistency --input rust-book.json

# Step 7: Validate references
book-creator validate-references --input rust-book.json

# Step 8: Check and fix grammar
book-creator check --input rust-book.json --fix --provider google

# Step 9: Format code examples
book-creator format-code \
  --input rust-book.json \
  --style "Rust standard" \
  --provider google

# Step 10: Export to all formats
book-creator export --input rust-book.json --format html
book-creator export --input rust-book.json --format pdf
book-creator export --input rust-book.json --format epub
book-creator export --input rust-book.json --format markdown
```

## Example 10: Using Local Models with Ollama

```bash
# Install Ollama first: https://ollama.ai
# Pull a model: ollama pull llama2

# Create a book entirely with local models (no API costs!)
book-creator create \
  --topic "Python for Beginners" \
  --chapters 10 \
  --provider ollama \
  --output python-beginner.json

# Generate content locally
book-creator generate \
  --input python-beginner.json \
  --provider ollama

# Add learning objectives locally
book-creator add-objectives \
  --input python-beginner.json \
  --provider ollama

# Generate glossary locally
book-creator generate-glossary \
  --input python-beginner.json \
  --provider ollama

# This works completely offline and has no API costs!
```
