# Pandoc PDF Export - High-Quality PDF Generation

## Overview

The Book Creator Tool now supports **Pandoc-based PDF generation**, providing professional-quality PDFs with advanced features like syntax highlighting, proper typography, and strict Markdown validation.

## Why Pandoc PDF?

### Advantages over Basic PDF Export

1. **Superior Typography**: Uses XeLaTeX for professional typesetting
2. **Color-Coded Syntax Highlighting**: Beautiful code blocks with multiple themes
3. **Strict Markdown Validation**: Ensures standard-compliant Markdown
4. **Better Unicode Support**: Handles international characters correctly
5. **Professional Formatting**: Automatic table of contents, numbered sections, proper page breaks

### Comparison

| Feature | Basic PDF (FPDF) | Pandoc PDF |
|---------|-----------------|------------|
| Syntax Highlighting | Basic (monochrome) | **Advanced (color-coded)** |
| Typography | Simple | **Professional (XeLaTeX)** |
| Markdown Validation | None | **Strict validation** |
| Unicode Support | Limited | **Full Unicode** |
| Customization | Limited | **Highly customizable** |
| Setup Complexity | None | Requires Pandoc + XeLaTeX |

## Installation

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install pandoc texlive-xetex
```

### macOS

```bash
brew install pandoc
brew install --cask mactex
```

### Windows

1. Download Pandoc from [https://pandoc.org/installing.html](https://pandoc.org/installing.html)
2. Download MiKTeX from [https://miktex.org/](https://miktex.org/)
3. Install both packages
4. Add Pandoc to your PATH

### Verify Installation

```bash
pandoc --version
xelatex --version
```

## Usage

### Basic Usage

```bash
# Export with default settings (tango theme)
book-creator export --input my-book.json --format pdf-pandoc

# Specify output path
book-creator export \
  --input my-book.json \
  --format pdf-pandoc \
  --output my-book.pdf
```

### With Syntax Highlighting Themes

```bash
# Use pygments theme (Python-style highlighting)
book-creator export \
  --input my-book.json \
  --format pdf-pandoc \
  --theme pygments

# Use kate theme (KDE editor style)
book-creator export \
  --input my-book.json \
  --format pdf-pandoc \
  --theme kate

# Use monochrome (no colors, for printing)
book-creator export \
  --input my-book.json \
  --format pdf-pandoc \
  --theme monochrome
```

### With Strict Markdown Validation

```bash
# Enable strict validation (fails on Markdown errors)
book-creator export \
  --input my-book.json \
  --format pdf-pandoc \
  --strict
```

## Available Syntax Highlighting Themes

The Pandoc PDF formatter supports multiple syntax highlighting themes:

- **tango** (default) - Colorful, balanced theme
- **pygments** - Python-style syntax highlighting
- **kate** - KDE editor theme
- **monochrome** - Black and white for printing
- **espresso** - Dark coffee theme
- **zenburn** - Low-contrast dark theme
- **breezedark** - KDE Breeze dark theme
- **haddock** - Haskell documentation style

### Theme Preview

You can test different themes easily:

```bash
for theme in tango pygments kate monochrome; do
  book-creator export \
    --input my-book.json \
    --format pdf-pandoc \
    --theme $theme \
    --output book-$theme.pdf
done
```

## Markdown Validation

The Pandoc PDF formatter includes **strict Markdown validation** to ensure your book follows standard Markdown syntax.

### What is Validated?

1. **Balanced Code Fences**: Ensures every `` ``` `` has a closing fence
2. **Proper Heading Syntax**: Headings must have space after `#`
3. **Correct List Formatting**: List markers (`-`, `*`, `+`) must be followed by space
4. **Valid Link Syntax**: Links must use proper `[text](url)` format

### Validation Example

```bash
# With strict validation (recommended for production)
book-creator export \
  --input my-book.json \
  --format pdf-pandoc \
  --strict

# Without strict validation (allows warnings)
book-creator export \
  --input my-book.json \
  --format pdf-pandoc
```

### Common Validation Errors

#### Unbalanced Code Fences

```markdown
# Invalid
```python
def hello():
    print("Hello")
# Missing closing ```

# Valid
```python
def hello():
    print("Hello")
```
```

#### Invalid Heading Syntax

```markdown
# Invalid
#No space after hash

# Valid
# Space after hash
```

#### Invalid List Syntax

```markdown
# Invalid
-Item without space

# Valid
- Item with space
```

## Programmatic Usage

You can also use the Pandoc PDF formatter programmatically:

```python
from book_creator import Book, PandocPDFFormatter

# Load or create book
book = Book.load("my-book.json")

# Create formatter
formatter = PandocPDFFormatter()

# Generate PDF with custom theme
formatter.format(
    book,
    "output.pdf",
    strict_validation=True,
    syntax_highlighting=True,
    theme="pygments"
)

# Get list of supported themes
themes = formatter.get_supported_themes()
print(f"Available themes: {', '.join(themes)}")

# Validate Markdown before generating
is_valid, errors = formatter.validate_markdown(markdown_content)
if not is_valid:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

## Advanced Features

### Custom Pandoc Options

For advanced users, the formatter uses the following Pandoc options:

- `--from markdown`: Source format
- `--to pdf`: Target format
- `--pdf-engine=xelatex`: Use XeLaTeX for better Unicode support
- `--toc`: Include table of contents
- `--toc-depth=3`: Three-level TOC
- `--number-sections`: Numbered sections
- `-V geometry:margin=1in`: 1-inch margins
- `-V fontsize=11pt`: 11-point font
- `-V documentclass=report`: Report document class

### Output Quality Features

1. **Syntax Highlighting**: Code blocks are beautifully formatted with proper indentation and colors
2. **Proper Line Breaks**: Paragraphs and sections are well-spaced
3. **Table of Contents**: Automatically generated with clickable links
4. **Numbered Sections**: All chapters and sections are numbered
5. **Professional Typography**: Proper font selection, kerning, and spacing

## Troubleshooting

### Pandoc Not Found

```
RuntimeError: Pandoc is not installed or not found at 'pandoc'
```

**Solution**: Install Pandoc following the installation instructions above.

### XeLaTeX Not Found

```
Error producing PDF.
! LaTeX Error: File `xelatex' not found.
```

**Solution**: Install XeLaTeX (part of TeX Live or MiKTeX).

### Markdown Validation Errors

```
ValueError: Markdown validation failed:
  - Line 42: Unbalanced code fences
```

**Solution**: Fix the Markdown syntax errors or disable strict validation with `--strict` flag removed.

### Unicode Characters Not Rendering

If you see missing characters in the PDF, ensure you're using Pandoc PDF (not basic PDF), as it has better Unicode support via XeLaTeX.

## Best Practices

1. **Use Strict Validation**: Always use `--strict` for production books to catch errors early
2. **Choose Appropriate Theme**: 
   - `tango` for general use
   - `pygments` for Python-heavy books
   - `monochrome` for print editions
3. **Test Different Themes**: Generate samples with different themes to find the best look
4. **Validate Before Publishing**: Run validation before final export
5. **Keep Markdown Clean**: Follow standard Markdown syntax for best results

## Performance

- **Generation Time**: Pandoc PDF takes longer than basic PDF (typically 2-5 seconds per book)
- **File Size**: PDFs are slightly larger due to embedded fonts and better quality
- **Quality**: Significantly higher quality output worth the extra time

## Comparison Example

Generate both PDF types to compare:

```bash
# Basic PDF
book-creator export --input my-book.json --format pdf --output basic.pdf

# Pandoc PDF
book-creator export --input my-book.json --format pdf-pandoc --output pandoc.pdf --theme tango

# Compare file sizes and quality
ls -lh basic.pdf pandoc.pdf
```

## Conclusion

Pandoc PDF export provides **professional-quality** PDF generation with:
- ✅ Beautiful syntax-highlighted code blocks
- ✅ Proper typography and formatting
- ✅ Strict Markdown validation
- ✅ Full Unicode support
- ✅ Customizable themes

For production books and professional publishing, use `pdf-pandoc` format. For quick previews or when Pandoc is unavailable, the basic `pdf` format is a good fallback.
