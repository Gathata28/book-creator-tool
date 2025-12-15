"""
Formatter Agent for Agentic-First Mode.

The Formatter Agent is responsible for:
- Generating front matter and back matter
- Applying layout and typography rules
- Producing export-ready files

Input: Approved manuscript
Output: Final formatted assets

Based on PRD Section 5.0.4
"""

import os
from typing import Optional, Dict, Any

from ..models.agentic import BookBlueprint
from ..models.book import Book
from ..formatters.html_formatter import HTMLFormatter
from ..formatters.pdf_formatter import PDFFormatter
from ..formatters.epub_formatter import EPUBFormatter
from ..formatters.markdown_formatter import MarkdownFormatter
from ..utils.llm_client import LLMClient, LLMConfig


class FormatterAgent:
    """
    Formatter Agent for generating final book outputs.
    
    This agent handles front/back matter generation and produces
    export-ready files in various formats.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())
        
        # Initialize formatters
        self._formatters = {
            "html": HTMLFormatter(),
            "pdf": PDFFormatter(),
            "epub": EPUBFormatter(),
            "markdown": MarkdownFormatter()
        }
        
        # Try to initialize Pandoc PDF formatter
        try:
            from ..formatters.pandoc_pdf_formatter import PandocPDFFormatter
            self._formatters["pdf-pandoc"] = PandocPDFFormatter()
        except Exception:
            pass
    
    def format_book(
        self,
        book: Book,
        blueprint: BookBlueprint,
        output_path: str,
        output_format: Optional[str] = None
    ) -> str:
        """
        Format and export the book.
        
        Returns the path to the exported file.
        """
        # Determine format
        format_type = output_format or blueprint.output_format or "pdf"
        
        # Generate front matter if not present
        if not book.preface:
            book.preface = self._generate_preface(book, blueprint)
        
        # Add table of contents metadata
        book.metadata["table_of_contents"] = self._generate_toc(book)
        
        # Add glossary if technical book
        if blueprint.programming_language or "technical" in blueprint.tone.lower():
            book.metadata["glossary"] = self._generate_glossary(book, blueprint)
        
        # Generate index
        book.metadata["index"] = self._generate_index(book)
        
        # Determine output path with correct extension
        output_path = self._ensure_extension(output_path, format_type)
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Export using appropriate formatter
        self._export(book, output_path, format_type, blueprint)
        
        return output_path
    
    def _generate_preface(self, book: Book, blueprint: BookBlueprint) -> str:
        """Generate book preface if not already present."""
        system_prompt = f"""You are writing the preface for a {blueprint.tone} book.
Keep it engaging and set clear expectations for readers."""

        objectives_text = ""
        if blueprint.learning_objectives:
            objectives_text = "\n\nLearning Objectives:\n" + "\n".join(
                f"- {obj.description}" for obj in blueprint.learning_objectives
            )

        prompt = f"""Write a preface for this book:

Title: {book.title}
Author: {book.author}
Description: {book.description}
Target Audience: {blueprint.target_audience}
{objectives_text}

Chapters:
{chr(10).join(f'- {ch.title}' for ch in book.chapters)}

The preface should:
1. Welcome the reader
2. Explain who this book is for
3. Describe what they will learn
4. Guide them on how to use the book
5. Be 200-300 words

Write the preface:"""

        return self.llm_client.generate_text(prompt, system_prompt).strip()
    
    def _generate_toc(self, book: Book) -> Dict[str, Any]:
        """Generate table of contents structure."""
        toc = {
            "title": "Table of Contents",
            "entries": []
        }
        
        for chapter in book.chapters:
            entry = {
                "number": chapter.number,
                "title": chapter.title,
                "sections": [
                    {"title": section.title}
                    for section in chapter.sections
                ]
            }
            toc["entries"].append(entry)
        
        return toc
    
    def _generate_glossary(self, book: Book, blueprint: BookBlueprint) -> Dict[str, str]:
        """Generate glossary of technical terms."""
        # Collect all content
        all_content = []
        
        for chapter in book.chapters:
            if chapter.introduction:
                all_content.append(chapter.introduction)
            for section in chapter.sections:
                if section.content:
                    all_content.append(section.content)
        
        full_content = "\n\n".join(all_content)
        
        if not full_content:
            return {}
        
        system_prompt = """You are creating a glossary for an educational book.
Identify key technical terms and provide clear definitions.
Return as JSON object: {"term1": "definition1", "term2": "definition2"}"""

        lang_context = ""
        if blueprint.programming_language:
            lang_context = f"\nProgramming Language: {blueprint.programming_language}"

        prompt = f"""Create a glossary of key terms from this book content:

Topic: {book.title}
Target Audience: {blueprint.target_audience}
{lang_context}

Content sample:
{full_content[:5000]}

Identify 10-20 key terms and provide clear definitions.
Return as JSON object:"""

        try:
            import json
            import re
            response = self.llm_client.generate_text(prompt, system_prompt)
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                glossary = json.loads(json_match.group())
                if isinstance(glossary, dict):
                    return glossary
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return {}
    
    def _generate_index(self, book: Book) -> list:
        """Generate index of key terms and their locations."""
        index = []
        
        for chapter in book.chapters:
            # Get key concepts from metadata
            if "key_concepts" in chapter.metadata:
                for concept in chapter.metadata["key_concepts"]:
                    # Check if concept already in index
                    existing = next((i for i in index if i["term"] == concept), None)
                    if existing:
                        existing["locations"].append(f"Chapter {chapter.number}")
                    else:
                        index.append({
                            "term": concept,
                            "locations": [f"Chapter {chapter.number}"]
                        })
        
        # Sort alphabetically
        index.sort(key=lambda x: x["term"].lower())
        
        return index
    
    def _ensure_extension(self, path: str, format_type: str) -> str:
        """Ensure output path has correct extension."""
        extensions = {
            "html": ".html",
            "pdf": ".pdf",
            "pdf-pandoc": ".pdf",
            "epub": ".epub",
            "markdown": ".md"
        }
        
        expected_ext = extensions.get(format_type, ".pdf")
        
        if not path.endswith(expected_ext):
            # Remove any existing extension
            base = os.path.splitext(path)[0]
            return base + expected_ext
        
        return path
    
    def _export(
        self,
        book: Book,
        output_path: str,
        format_type: str,
        blueprint: BookBlueprint
    ):
        """Export book using appropriate formatter."""
        # Handle pdf-pandoc specially
        if format_type == "pdf-pandoc":
            if "pdf-pandoc" in self._formatters:
                formatter = self._formatters["pdf-pandoc"]
                formatter.format(book, output_path)
            else:
                # Fall back to basic PDF
                formatter = self._formatters.get("pdf")
                if formatter:
                    formatter.format(book, output_path)
                else:
                    raise RuntimeError("No PDF formatter available")
            return
        
        # Get formatter
        formatter = self._formatters.get(format_type)
        
        if not formatter:
            # Default to HTML if format not supported
            formatter = self._formatters.get("html")
            if formatter:
                # Adjust output path
                output_path = os.path.splitext(output_path)[0] + ".html"
        
        if formatter:
            formatter.format(book, output_path)
        else:
            raise RuntimeError(f"No formatter available for format: {format_type}")
    
    def get_supported_formats(self) -> list:
        """Get list of supported output formats."""
        return list(self._formatters.keys())
