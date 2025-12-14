"""
Markdown formatter for exporting books to Markdown
"""

import os
from ..models.book import Book


class MarkdownFormatter:
    """Format books as Markdown"""
    
    def format(self, book: Book, output_path: str):
        """Format book as Markdown file"""
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        markdown = self._generate_markdown(book)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

    def _generate_markdown(self, book: Book) -> str:
        """Generate Markdown content for the book"""
        
        md = f"# {book.title}\n\n"
        md += f"**Author:** {book.author}\n\n"
        
        if book.description:
            md += f"## Description\n\n{book.description}\n\n"
        
        if book.preface:
            md += f"## Preface\n\n{book.preface}\n\n"
        
        # Table of contents
        md += "## Table of Contents\n\n"
        for chapter in book.chapters:
            md += f"{chapter.number}. [{chapter.title}](#chapter-{chapter.number})\n"
        md += "\n---\n\n"
        
        # Chapters
        for chapter in book.chapters:
            md += self._format_chapter(chapter)
        
        return md

    def _format_chapter(self, chapter) -> str:
        """Format a chapter as Markdown"""
        
        md = f"## Chapter {chapter.number}: {chapter.title} {{#chapter-{chapter.number}}}\n\n"
        
        if chapter.introduction:
            md += f"### Introduction\n\n{chapter.introduction}\n\n"
        
        for section in chapter.sections:
            md += self._format_section(section)
        
        if chapter.summary:
            md += f"### Summary\n\n{chapter.summary}\n\n"
        
        md += "---\n\n"
        return md

    def _format_section(self, section) -> str:
        """Format a section as Markdown"""
        
        md = f"### {section.title}\n\n"
        
        if section.content:
            md += f"{section.content}\n\n"
        
        # Code examples
        for example in section.code_examples:
            md += self._format_code_example(example)
        
        # Exercises
        for exercise in section.exercises:
            md += self._format_exercise(exercise)
        
        return md

    def _format_code_example(self, example) -> str:
        """Format a code example"""
        
        md = ""
        
        if example.get('explanation'):
            md += f"**Example:** {example['explanation']}\n\n"
        
        language = example.get('language', 'python')
        code = example.get('code', '')
        md += f"```{language}\n{code}\n```\n\n"
        
        return md

    def _format_exercise(self, exercise) -> str:
        """Format an exercise"""
        
        md = "**Exercise:**\n\n"
        md += f"{exercise.get('question', '')}\n\n"
        
        if exercise.get('hints'):
            md += "**Hints:**\n\n"
            for hint in exercise['hints']:
                md += f"- {hint}\n"
            md += "\n"
        
        if exercise.get('answer'):
            md += f"**Answer:** {exercise['answer']}\n\n"
        
        return md
