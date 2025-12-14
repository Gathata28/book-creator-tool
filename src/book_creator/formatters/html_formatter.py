"""
HTML formatter for exporting books to HTML
"""

import os
from typing import Optional
from jinja2 import Template
from ..models.book import Book
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class HTMLFormatter:
    """Format books as HTML"""
    
    def __init__(self, template_path: Optional[str] = None):
        self.template_path = template_path
        self.css_style = self._default_css()

    def format(self, book: Book, output_path: str):
        """Format book as HTML file"""
        
        html_content = self._generate_html(book)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html(self, book: Book) -> str:
        """Generate HTML content for the book"""
        
        template = Template(self._default_template())
        
        # Process chapters and sections
        chapters_html = []
        for chapter in book.chapters:
            chapter_html = self._format_chapter(chapter)
            chapters_html.append(chapter_html)

        html_content = template.render(
            book=book,
            chapters_html=chapters_html,
            css_style=self.css_style
        )

        return html_content

    def _format_chapter(self, chapter) -> str:
        """Format a single chapter"""
        
        html = f"""
        <div class="chapter" id="chapter-{chapter.number}">
            <h1>Chapter {chapter.number}: {chapter.title}</h1>
            
            {f'<div class="introduction">{self._format_text(chapter.introduction)}</div>' if chapter.introduction else ''}
            
            <div class="sections">
        """

        for section in chapter.sections:
            html += self._format_section(section)

        html += """
            </div>
        """

        if chapter.summary:
            html += f"""
            <div class="summary">
                <h3>Summary</h3>
                {self._format_text(chapter.summary)}
            </div>
            """

        html += "</div>"
        return html

    def _format_section(self, section) -> str:
        """Format a single section"""
        
        html = f"""
        <div class="section">
            <h2>{section.title}</h2>
            <div class="content">
                {self._format_text(section.content)}
            </div>
        """

        # Add code examples
        if section.code_examples:
            html += '<div class="code-examples">'
            for example in section.code_examples:
                html += self._format_code_example(example)
            html += '</div>'

        # Add exercises
        if section.exercises:
            html += '<div class="exercises">'
            for exercise in section.exercises:
                html += self._format_exercise(exercise)
            html += '</div>'

        html += "</div>"
        return html

    def _format_code_example(self, example) -> str:
        """Format a code example with syntax highlighting"""
        
        code = example.get('code', '')
        language = example.get('language', 'python')
        explanation = example.get('explanation', '')

        try:
            lexer = get_lexer_by_name(language, stripall=True)
            formatter = HtmlFormatter(style='colorful', noclasses=True)
            highlighted = highlight(code, lexer, formatter)
        except Exception:
            highlighted = f'<pre><code>{code}</code></pre>'

        html = f"""
        <div class="code-example">
            {f'<p class="explanation">{explanation}</p>' if explanation else ''}
            {highlighted}
        </div>
        """
        return html

    def _format_exercise(self, exercise) -> str:
        """Format an exercise"""
        
        html = f"""
        <div class="exercise">
            <h4>Exercise</h4>
            <p class="question">{exercise.get('question', '')}</p>
        """

        if exercise.get('hints'):
            html += '<div class="hints"><h5>Hints:</h5><ul>'
            for hint in exercise['hints']:
                html += f'<li>{hint}</li>'
            html += '</ul></div>'

        if exercise.get('answer'):
            html += f'<div class="answer"><h5>Answer:</h5><p>{exercise["answer"]}</p></div>'

        html += '</div>'
        return html

    def _format_text(self, text: str) -> str:
        """Format text with basic HTML"""
        if not text:
            return ""
        
        # Simple paragraph splitting
        paragraphs = text.split('\n\n')
        return '\n'.join([f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()])

    def _default_template(self) -> str:
        """Default HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ book.title }}</title>
    <style>
        {{ css_style }}
    </style>
</head>
<body>
    <div class="book">
        <header>
            <h1 class="book-title">{{ book.title }}</h1>
            <p class="book-author">by {{ book.author }}</p>
            {% if book.description %}
            <p class="book-description">{{ book.description }}</p>
            {% endif %}
        </header>

        {% if book.preface %}
        <div class="preface">
            <h2>Preface</h2>
            {{ book.preface }}
        </div>
        {% endif %}

        <div class="table-of-contents">
            <h2>Table of Contents</h2>
            <ul>
            {% for chapter in book.chapters %}
                <li><a href="#chapter-{{ chapter.number }}">Chapter {{ chapter.number }}: {{ chapter.title }}</a></li>
            {% endfor %}
            </ul>
        </div>

        <div class="content">
            {% for chapter_html in chapters_html %}
            {{ chapter_html|safe }}
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

    def _default_css(self) -> str:
        """Default CSS styling"""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }

        .book {
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }

        header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 40px;
        }

        .book-title {
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .book-author {
            font-size: 1.2em;
            color: #7f8c8d;
            font-style: italic;
        }

        .table-of-contents {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 40px;
        }

        .table-of-contents h2 {
            color: #2c3e50;
            margin-top: 0;
        }

        .table-of-contents ul {
            list-style-type: none;
            padding-left: 0;
        }

        .table-of-contents li {
            margin-bottom: 8px;
        }

        .table-of-contents a {
            color: #3498db;
            text-decoration: none;
        }

        .table-of-contents a:hover {
            text-decoration: underline;
        }

        .chapter {
            margin-bottom: 60px;
            page-break-after: always;
        }

        .chapter h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }

        .introduction, .summary {
            background-color: #e8f4f8;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }

        .section {
            margin: 30px 0;
        }

        .section h2 {
            color: #34495e;
            margin-top: 30px;
        }

        .code-example {
            margin: 20px 0;
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }

        .code-example .explanation {
            background-color: #e8f4f8;
            padding: 10px;
            margin: 0;
            border-bottom: 1px solid #ddd;
        }

        .code-example pre {
            margin: 0;
            padding: 15px;
            overflow-x: auto;
        }

        .exercise {
            background-color: #fff9e6;
            border: 1px solid #f39c12;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }

        .exercise h4 {
            color: #f39c12;
            margin-top: 0;
        }

        .hints {
            background-color: #fff;
            padding: 10px;
            border-radius: 3px;
            margin-top: 10px;
        }

        .answer {
            background-color: #e8f8e8;
            padding: 10px;
            border-radius: 3px;
            margin-top: 10px;
        }

        @media print {
            body {
                background-color: white;
            }
            
            .book {
                box-shadow: none;
            }
        }
        """
