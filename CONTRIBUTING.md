# Contributing to Book Creator Tool

Thank you for your interest in contributing to the Book Creator Tool! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/book-creator-tool.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests (when available)
6. Commit your changes: `git commit -m "Add your message"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Formatting

We use `black` for code formatting:

```bash
black src/book_creator
```

### Linting

We use `flake8` for linting:

```bash
flake8 src/book_creator
```

## Project Structure

```
book-creator-tool/
├── src/book_creator/
│   ├── models/           # Data models
│   ├── generators/       # Content generation
│   ├── editors/          # Editing tools
│   ├── formatters/       # Export formatters
│   ├── utils/            # Utilities
│   └── cli.py           # CLI interface
├── tests/               # Test files
├── examples/            # Example files
└── docs/               # Documentation
```

## Adding New Features

### Adding a New Generator

1. Create a new file in `src/book_creator/generators/`
2. Implement the generator class
3. Add it to `src/book_creator/generators/__init__.py`
4. Update `src/book_creator/__init__.py`
5. Add CLI commands if needed in `cli.py`
6. Write tests
7. Update documentation

### Adding a New Formatter

1. Create a new file in `src/book_creator/formatters/`
2. Implement the formatter class with a `format()` method
3. Add it to `src/book_creator/formatters/__init__.py`
4. Add export option in CLI
5. Write tests
6. Update documentation

### Adding a New LLM Provider

1. Update `utils/llm_client.py`
2. Add new provider to `LLMProvider` enum
3. Implement provider-specific methods in `LLMClient`
4. Update configuration handling
5. Test integration
6. Update documentation

## Testing

We use `pytest` for testing:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=book_creator tests/
```

### Writing Tests

- Write tests for all new features
- Aim for high test coverage
- Use meaningful test names
- Test edge cases and error conditions
- Mock external API calls

Example test:

```python
import pytest
from book_creator.models.book import Book, Chapter, Section

def test_book_creation():
    book = Book(title="Test Book", author="Test Author")
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert len(book.chapters) == 0

def test_add_chapter():
    book = Book(title="Test", author="Author")
    chapter = Chapter(title="Chapter 1", number=1)
    book.add_chapter(chapter)
    assert len(book.chapters) == 1
    assert book.get_chapter(1) == chapter
```

## Documentation

- Update README.md for user-facing changes
- Update EXAMPLES.md with usage examples
- Add docstrings to all public APIs
- Include type hints
- Provide clear examples

## Pull Request Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what changes you made and why
3. **Testing**: Describe how you tested your changes
4. **Documentation**: Update relevant documentation
5. **Breaking Changes**: Clearly mark any breaking changes

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commits are clear and well-organized

## Feature Requests

To request a new feature:

1. Check if it's already requested in Issues
2. Open a new issue with the "enhancement" label
3. Describe the feature and use case
4. Explain why it would be valuable

## Bug Reports

To report a bug:

1. Check if it's already reported
2. Open a new issue with the "bug" label
3. Provide a clear description
4. Include steps to reproduce
5. Share relevant error messages
6. Mention your environment (OS, Python version, etc.)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help create a welcoming environment

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to Book Creator Tool! 🎉
