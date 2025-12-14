"""
Tests for Pandoc PDF formatter and Markdown validation
"""

import pytest
import tempfile
import os
import subprocess

from book_creator.models.book import Book, Chapter, Section
from book_creator.formatters.pandoc_pdf_formatter import PandocPDFFormatter


def check_pandoc_available():
    """Check if Pandoc is available"""
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# Skip all tests if Pandoc is not available
pytestmark = pytest.mark.skipif(not check_pandoc_available(), reason="Pandoc not installed")


def create_test_book():
    """Create a test book for formatter tests"""
    book = Book(
        title="Test Book for Pandoc",
        author="Test Author",
        description="A test book with proper Markdown"
    )
    
    chapter = Chapter(title="Introduction to Testing", number=1)
    chapter.introduction = "This chapter covers testing basics."
    
    section = Section(title="Getting Started")
    section.content = "Testing is important for software quality."
    section.add_code_example(
        "def test_example():\n    assert True\n    print('Test passed')",
        "python",
        "A simple test example"
    )
    
    chapter.add_section(section)
    chapter.summary = "We learned about testing fundamentals."
    book.add_chapter(chapter)
    
    return book


def test_pandoc_formatter_initialization():
    """Test PandocPDFFormatter initialization"""
    formatter = PandocPDFFormatter()
    assert formatter.pandoc_path == "pandoc"


def test_pandoc_not_found():
    """Test error when Pandoc is not found"""
    with pytest.raises(RuntimeError, match="Pandoc is not installed"):
        PandocPDFFormatter(pandoc_path="/nonexistent/pandoc")


def test_markdown_validation_valid():
    """Test Markdown validation with valid content"""
    formatter = PandocPDFFormatter()
    
    valid_markdown = """# Heading 1

## Heading 2

This is a paragraph with **bold** and *italic* text.

### Code Example

```python
def hello():
    print("Hello, World!")
```

- List item 1
- List item 2

[Link text](https://example.com)
"""
    
    is_valid, errors = formatter.validate_markdown(valid_markdown)
    assert is_valid
    assert len(errors) == 0


def test_markdown_validation_unbalanced_code_fences():
    """Test detection of unbalanced code fences"""
    formatter = PandocPDFFormatter()
    
    invalid_markdown = """# Test

```python
def test():
    pass
# Missing closing fence
"""
    
    is_valid, errors = formatter.validate_markdown(invalid_markdown)
    assert not is_valid
    assert any("code fences" in err.lower() for err in errors)


def test_markdown_validation_invalid_heading():
    """Test detection of invalid heading syntax"""
    formatter = PandocPDFFormatter()
    
    invalid_markdown = """#Invalid Heading
This should have a space after #
"""
    
    is_valid, errors = formatter.validate_markdown(invalid_markdown)
    assert not is_valid
    assert any("heading" in err.lower() for err in errors)


def test_markdown_validation_invalid_list():
    """Test detection of invalid list syntax"""
    formatter = PandocPDFFormatter()
    
    invalid_markdown = """# Test

-Item without space
* Another item
"""
    
    is_valid, errors = formatter.validate_markdown(invalid_markdown)
    assert not is_valid
    assert any("list" in err.lower() for err in errors)


def test_pandoc_pdf_generation():
    """Test PDF generation from book"""
    book = create_test_book()
    formatter = PandocPDFFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as f:
        temp_pdf = f.name
    
    try:
        # Generate PDF
        formatter.format(book, temp_pdf, strict_validation=True)
        
        # Check file exists and has content
        assert os.path.exists(temp_pdf)
        assert os.path.getsize(temp_pdf) > 0
        
        # Verify it's a PDF file (starts with %PDF)
        with open(temp_pdf, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF'
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_pandoc_pdf_with_code_highlighting():
    """Test PDF generation with syntax highlighting"""
    book = create_test_book()
    formatter = PandocPDFFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as f:
        temp_pdf = f.name
    
    try:
        # Generate PDF with specific theme
        formatter.format(book, temp_pdf, syntax_highlighting=True, theme='pygments')
        
        assert os.path.exists(temp_pdf)
        assert os.path.getsize(temp_pdf) > 0
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_pandoc_pdf_strict_validation_fail():
    """Test that strict validation catches errors"""
    book = Book(title="Invalid Book", author="Test")
    chapter = Chapter(title="Test", number=1)
    
    # Create section with invalid Markdown (we'll inject it via content)
    section = Section(title="Test Section")
    # This will create unbalanced code fences in the final markdown
    section.content = "Some text\n```python\ncode here"
    chapter.add_section(section)
    book.add_chapter(chapter)
    
    formatter = PandocPDFFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as f:
        temp_pdf = f.name
    
    try:
        # Should raise ValueError due to validation
        with pytest.raises(ValueError, match="Markdown validation failed"):
            formatter.format(book, temp_pdf, strict_validation=True)
    finally:
        # Clean up if file was created
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_pandoc_pdf_non_strict_validation():
    """Test that non-strict validation allows warnings"""
    book = create_test_book()
    formatter = PandocPDFFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as f:
        temp_pdf = f.name
    
    try:
        # Should succeed even with minor issues when strict=False
        formatter.format(book, temp_pdf, strict_validation=False)
        assert os.path.exists(temp_pdf)
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_get_supported_themes():
    """Test getting list of supported themes"""
    formatter = PandocPDFFormatter()
    themes = formatter.get_supported_themes()
    
    assert isinstance(themes, list)
    assert len(themes) > 0
    assert 'tango' in themes
    assert 'pygments' in themes
    assert 'kate' in themes


def test_markdown_validation_with_multiple_code_blocks():
    """Test validation with multiple code blocks"""
    formatter = PandocPDFFormatter()
    
    markdown = """# Test

First code block:

```python
def test1():
    pass
```

Second code block:

```javascript
function test2() {
    return true;
}
```

Done.
"""
    
    is_valid, errors = formatter.validate_markdown(markdown)
    assert is_valid


def test_markdown_validation_with_inline_code():
    """Test validation doesn't break with inline code"""
    formatter = PandocPDFFormatter()
    
    markdown = """# Test

Use `inline code` like this.

More text with `another inline` example.
"""
    
    is_valid, errors = formatter.validate_markdown(markdown)
    assert is_valid


def test_book_with_exercises():
    """Test PDF generation with exercises"""
    book = Book(title="Exercise Book", author="Test")
    chapter = Chapter(title="Chapter 1", number=1)
    section = Section(title="Section 1")
    
    section.content = "Learn by doing."
    section.add_exercise(
        question="What is 2+2?",
        answer="4",
        hints=["Think about addition", "It's a small number"]
    )
    
    chapter.add_section(section)
    book.add_chapter(chapter)
    
    formatter = PandocPDFFormatter()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as f:
        temp_pdf = f.name
    
    try:
        formatter.format(book, temp_pdf)
        assert os.path.exists(temp_pdf)
        assert os.path.getsize(temp_pdf) > 0
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_pandoc_pdf_creates_output_directory():
    """Test that formatter creates output directory if it doesn't exist"""
    book = create_test_book()
    formatter = PandocPDFFormatter()
    
    # Create a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "subdir", "test.pdf")
        
        # Directory subdir doesn't exist yet
        assert not os.path.exists(os.path.dirname(output_path))
        
        formatter.format(book, output_path)
        
        # Should create directory and file
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
