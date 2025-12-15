"""
Book Creator Tool - AI-Powered Coding Book Platform

A comprehensive platform for creating coding books with AI and LLM integration.
Features include automated content generation, LLM-powered code examples,
interactive learning modules, AI-assisted editing, and customizable publishing.

Supports two modes of operation:
1. Guided (User-Led) Mode - step-by-step book creation with user input
2. Agentic-First Mode - autonomous book generation from a single prompt
"""

__version__ = "0.1.0"

from .models.book import Book, Chapter, Section
from .models.agentic import (
    LifecycleState,
    ComplexityLevel,
    UserPrompt,
    BookBlueprint,
    ChapterBlueprint,
    AgenticState
)
from .generators.content_generator import ContentGenerator
from .generators.outline_generator import OutlineGenerator
from .generators.code_generator import CodeGenerator
from .editors.grammar_checker import GrammarChecker
from .editors.content_improver import ContentImprover
from .editors.book_editor import BookEditor
from .formatters.pdf_formatter import PDFFormatter
from .formatters.pandoc_pdf_formatter import PandocPDFFormatter
from .formatters.epub_formatter import EPUBFormatter
from .formatters.html_formatter import HTMLFormatter
from .agentic import AgenticBookGenerator, generate_book_from_prompt

__all__ = [
    # Book models
    "Book",
    "Chapter",
    "Section",
    # Agentic-First Mode
    "AgenticBookGenerator",
    "generate_book_from_prompt",
    "LifecycleState",
    "ComplexityLevel",
    "UserPrompt",
    "BookBlueprint",
    "ChapterBlueprint",
    "AgenticState",
    # Generators
    "ContentGenerator",
    "OutlineGenerator",
    "CodeGenerator",
    # Editors
    "GrammarChecker",
    "ContentImprover",
    "BookEditor",
    # Formatters
    "PDFFormatter",
    "PandocPDFFormatter",
    "EPUBFormatter",
    "HTMLFormatter",
]
