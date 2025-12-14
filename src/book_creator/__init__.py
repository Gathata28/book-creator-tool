"""
Book Creator Tool - AI-Powered Coding Book Platform

A comprehensive platform for creating coding books with AI and LLM integration.
Features include automated content generation, LLM-powered code examples,
interactive learning modules, AI-assisted editing, and customizable publishing.
"""

__version__ = "0.1.0"

from .models.book import Book, Chapter, Section
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

__all__ = [
    "Book",
    "Chapter",
    "Section",
    "ContentGenerator",
    "OutlineGenerator",
    "CodeGenerator",
    "GrammarChecker",
    "ContentImprover",
    "BookEditor",
    "PDFFormatter",
    "PandocPDFFormatter",
    "EPUBFormatter",
    "HTMLFormatter",
]
