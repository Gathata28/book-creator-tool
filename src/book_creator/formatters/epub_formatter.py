"""
EPUB formatter for exporting books to EPUB format
"""

import os
from ebooklib import epub
from ..models.book import Book


class EPUBFormatter:
    """Format books as EPUB"""
    
    def format(self, book: Book, output_path: str):
        """Format book as EPUB file"""
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Create EPUB book
        ebook = epub.EpubBook()
        
        # Set metadata
        ebook.set_identifier(f'book-{book.title.lower().replace(" ", "-")}')
        ebook.set_title(book.title)
        ebook.set_language('en')
        ebook.add_author(book.author)
        
        if book.description:
            ebook.add_metadata('DC', 'description', book.description)
        
        # Create chapters
        epub_chapters = []
        spine = ['nav']
        
        # Add preface if exists
        if book.preface:
            preface = epub.EpubHtml(
                title='Preface',
                file_name='preface.xhtml',
                lang='en'
            )
            preface.content = f'<h1>Preface</h1>{self._format_text(book.preface)}'
            ebook.add_item(preface)
            epub_chapters.append(preface)
            spine.append(preface)
        
        # Add each chapter
        for chapter in book.chapters:
            epub_chapter = self._create_epub_chapter(chapter)
            ebook.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
            spine.append(epub_chapter)
        
        # Add table of contents
        ebook.toc = tuple(epub_chapters)
        
        # Add navigation files
        ebook.add_item(epub.EpubNcx())
        ebook.add_item(epub.EpubNav())
        
        # Define spine
        ebook.spine = spine
        
        # Add CSS
        css = self._default_css()
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=css
        )
        ebook.add_item(nav_css)
        
        # Write EPUB file
        epub.write_epub(output_path, ebook, {})

    def _create_epub_chapter(self, chapter) -> epub.EpubHtml:
        """Create an EPUB chapter from a Chapter object"""
        
        epub_chapter = epub.EpubHtml(
            title=f'Chapter {chapter.number}: {chapter.title}',
            file_name=f'chapter_{chapter.number}.xhtml',
            lang='en'
        )
        
        content = f'<h1>Chapter {chapter.number}: {chapter.title}</h1>\n'
        
        # Add introduction
        if chapter.introduction:
            content += f'<div class="introduction">{self._format_text(chapter.introduction)}</div>\n'
        
        # Add sections
        for section in chapter.sections:
            content += self._format_section(section)
        
        # Add summary
        if chapter.summary:
            content += f'<div class="summary"><h2>Summary</h2>{self._format_text(chapter.summary)}</div>\n'
        
        epub_chapter.content = content
        epub_chapter.add_item(epub.EpubItem(
            uid="style_default",
            file_name="style/nav.css",
            media_type="text/css",
            content=self._default_css()
        ))
        
        return epub_chapter

    def _format_section(self, section) -> str:
        """Format a section as HTML"""
        
        html = f'<div class="section">\n'
        html += f'<h2>{section.title}</h2>\n'
        
        if section.content:
            html += self._format_text(section.content)
        
        # Add code examples
        for example in section.code_examples:
            html += self._format_code_example(example)
        
        # Add exercises
        for exercise in section.exercises:
            html += self._format_exercise(exercise)
        
        html += '</div>\n'
        return html

    def _format_code_example(self, example) -> str:
        """Format a code example"""
        
        html = '<div class="code-example">\n'
        
        if example.get('explanation'):
            html += f'<p class="explanation">{example["explanation"]}</p>\n'
        
        code = example.get('code', '').replace('<', '&lt;').replace('>', '&gt;')
        html += f'<pre><code>{code}</code></pre>\n'
        html += '</div>\n'
        
        return html

    def _format_exercise(self, exercise) -> str:
        """Format an exercise"""
        
        html = '<div class="exercise">\n'
        html += '<h4>Exercise</h4>\n'
        html += f'<p>{exercise.get("question", "")}</p>\n'
        
        if exercise.get('hints'):
            html += '<div class="hints"><h5>Hints:</h5><ul>\n'
            for hint in exercise['hints']:
                html += f'<li>{hint}</li>\n'
            html += '</ul></div>\n'
        
        html += '</div>\n'
        return html

    def _format_text(self, text: str) -> str:
        """Format plain text as HTML paragraphs"""
        if not text:
            return ""
        
        paragraphs = text.split('\n\n')
        return '\n'.join([f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()])

    def _default_css(self) -> str:
        """Default CSS for EPUB"""
        return """
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            color: #333;
            margin: 1em;
        }

        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.5em;
        }

        h2 {
            color: #34495e;
            margin-top: 1.5em;
        }

        .introduction, .summary {
            background-color: #e8f4f8;
            padding: 1em;
            border-left: 4px solid #3498db;
            margin: 1em 0;
        }

        .code-example {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 1em 0;
            padding: 1em;
        }

        .code-example pre {
            margin: 0;
            overflow-x: auto;
        }

        .code-example code {
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .exercise {
            background-color: #fff9e6;
            border: 1px solid #f39c12;
            border-radius: 5px;
            padding: 1em;
            margin: 1em 0;
        }

        .exercise h4 {
            color: #f39c12;
            margin-top: 0;
        }

        .hints {
            background-color: #fff;
            padding: 0.5em;
            border-radius: 3px;
            margin-top: 0.5em;
        }
        """
