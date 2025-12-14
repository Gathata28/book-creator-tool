"""
PDF formatter for exporting books to PDF
"""

import os
from typing import Optional
from fpdf import FPDF
from ..models.book import Book


class PDFFormatter:
    """Format books as PDF"""
    
    def __init__(self):
        self.pdf = None

    def format(self, book: Book, output_path: str):
        """Format book as PDF file"""
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add title page
        self._add_title_page(book)
        
        # Add table of contents
        self._add_toc(book)
        
        # Add chapters
        for chapter in book.chapters:
            self._add_chapter(chapter)
        
        # Save PDF
        self.pdf.output(output_path)

    def _add_title_page(self, book: Book):
        """Add title page to PDF"""
        self.pdf.add_page()
        
        # Title
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.cell(0, 60, '', 0, 1)  # Spacing
        self.pdf.cell(0, 10, book.title, 0, 1, 'C')
        
        # Author
        self.pdf.set_font('Arial', 'I', 16)
        self.pdf.cell(0, 10, f'by {book.author}', 0, 1, 'C')
        
        # Description
        if book.description:
            self.pdf.cell(0, 20, '', 0, 1)  # Spacing
            self.pdf.set_font('Arial', '', 12)
            self.pdf.multi_cell(0, 10, book.description, 0, 'C')

    def _add_toc(self, book: Book):
        """Add table of contents"""
        self.pdf.add_page()
        
        self.pdf.set_font('Arial', 'B', 18)
        self.pdf.cell(0, 10, 'Table of Contents', 0, 1)
        self.pdf.ln(5)
        
        self.pdf.set_font('Arial', '', 12)
        for chapter in book.chapters:
            toc_line = f"Chapter {chapter.number}: {chapter.title}"
            self.pdf.cell(0, 8, toc_line, 0, 1)

    def _add_chapter(self, chapter):
        """Add a chapter to PDF"""
        self.pdf.add_page()
        
        # Chapter title
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, f'Chapter {chapter.number}: {chapter.title}', 0, 1)
        self.pdf.ln(5)
        
        # Introduction
        if chapter.introduction:
            self.pdf.set_font('Arial', 'I', 11)
            self.pdf.multi_cell(0, 6, chapter.introduction)
            self.pdf.ln(5)
        
        # Sections
        for section in chapter.sections:
            self._add_section(section)
        
        # Summary
        if chapter.summary:
            self.pdf.set_font('Arial', 'B', 12)
            self.pdf.cell(0, 10, 'Summary', 0, 1)
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 6, chapter.summary)

    def _add_section(self, section):
        """Add a section to PDF"""
        
        # Section title
        self.pdf.set_font('Arial', 'B', 13)
        self.pdf.cell(0, 8, section.title, 0, 1)
        self.pdf.ln(2)
        
        # Section content
        if section.content:
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 6, section.content)
            self.pdf.ln(3)
        
        # Code examples
        for example in section.code_examples:
            self._add_code_example(example)
        
        # Exercises
        for exercise in section.exercises:
            self._add_exercise(exercise)

    def _add_code_example(self, example):
        """Add a code example to PDF"""
        
        if example.get('explanation'):
            self.pdf.set_font('Arial', 'I', 10)
            self.pdf.multi_cell(0, 5, example['explanation'])
        
        self.pdf.set_font('Courier', '', 9)
        self.pdf.set_fill_color(240, 240, 240)
        
        code_lines = example.get('code', '').split('\n')
        for line in code_lines:
            # Handle long lines
            if len(line) > 90:
                line = line[:90] + '...'
            self.pdf.cell(0, 5, line, 0, 1, fill=True)
        
        self.pdf.ln(3)

    def _add_exercise(self, exercise):
        """Add an exercise to PDF"""
        
        self.pdf.set_fill_color(255, 249, 230)
        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 6, 'Exercise:', 0, 1, fill=True)
        
        self.pdf.set_font('Arial', '', 10)
        self.pdf.multi_cell(0, 5, exercise.get('question', ''), 0, fill=True)
        
        if exercise.get('hints'):
            self.pdf.set_font('Arial', 'I', 9)
            for hint in exercise['hints']:
                self.pdf.cell(10, 5, '', 0, 0)
                self.pdf.multi_cell(0, 5, f'• {hint}', 0, fill=True)
        
        self.pdf.ln(3)
