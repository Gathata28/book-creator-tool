"""
Tests for formatters
"""

import tempfile
import os

from book_creator.models.book import Book, Chapter, Section
from book_creator.formatters.html_formatter import HTMLFormatter
from book_creator.formatters.markdown_formatter import MarkdownFormatter


def create_test_book():
    """Create a test book for formatter tests"""
    book = Book(
        title="Test Book",
        author="Test Author",
        description="A test book"
    )
    
    chapter = Chapter(title="Test Chapter", number=1)
    chapter.introduction = "Chapter introduction"
    
    section = Section(title="Test Section")
    section.content = "Section content"
    section.add_code_example("print('hello')", "python", "Example")
    
    chapter.add_section(section)
    chapter.summary = "Chapter summary"
    book.add_chapter(chapter)
    
    return book


def test_html_formatter():
    """Test HTML formatter"""
    book = create_test_book()
    formatter = HTMLFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        temp_file = f.name
    
    try:
        formatter.format(book, temp_file)
        
        # Check file exists and has content
        assert os.path.exists(temp_file)
        with open(temp_file, 'r') as f:
            content = f.read()
            assert 'Test Book' in content
            assert 'Test Author' in content
            assert 'Test Chapter' in content
            assert 'Test Section' in content
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_markdown_formatter():
    """Test Markdown formatter"""
    book = create_test_book()
    formatter = MarkdownFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        temp_file = f.name
    
    try:
        formatter.format(book, temp_file)
        
        # Check file exists and has content
        assert os.path.exists(temp_file)
        with open(temp_file, 'r') as f:
            content = f.read()
            assert '# Test Book' in content
            assert '**Author:** Test Author' in content
            assert 'Chapter 1: Test Chapter' in content
            assert '### Test Section' in content
            assert '```python' in content
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_html_formatter_with_exercises():
    """Test HTML formatter with exercises"""
    book = create_test_book()
    book.chapters[0].sections[0].add_exercise(
        "What is 2+2?",
        "4",
        ["Think about math", "It's simple"]
    )
    
    formatter = HTMLFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        temp_file = f.name
    
    try:
        formatter.format(book, temp_file)
        
        with open(temp_file, 'r') as f:
            content = f.read()
            assert 'What is 2+2?' in content
            assert 'exercise' in content.lower()
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_markdown_formatter_with_code():
    """Test Markdown formatter with code examples"""
    book = Book(title="Code Book", author="Author")
    chapter = Chapter(title="Chapter 1", number=1)
    section = Section(title="Section 1")
    section.add_code_example(
        "def hello():\n    print('Hello World')",
        "python",
        "A simple function"
    )
    chapter.add_section(section)
    book.add_chapter(chapter)
    
    formatter = MarkdownFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        temp_file = f.name
    
    try:
        formatter.format(book, temp_file)
        
        with open(temp_file, 'r') as f:
            content = f.read()
            assert '```python' in content
            assert 'def hello():' in content
            assert "print('Hello World')" in content
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
