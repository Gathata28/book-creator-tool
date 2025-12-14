"""
Command-line interface for the book creator tool
"""

import click
import os
from typing import Optional

from .models.book import Book, Chapter, Section
from .generators.outline_generator import OutlineGenerator
from .generators.content_generator import ContentGenerator
from .generators.code_generator import CodeGenerator
from .editors.grammar_checker import GrammarChecker
from .editors.content_improver import ContentImprover
from .formatters.html_formatter import HTMLFormatter
from .formatters.pdf_formatter import PDFFormatter
from .formatters.epub_formatter import EPUBFormatter
from .formatters.markdown_formatter import MarkdownFormatter
from .utils.llm_client import LLMClient, LLMConfig, LLMProvider


@click.group()
@click.version_option(version='0.1.0')
def main():
    """Book Creator Tool - AI-Powered Coding Book Platform
    
    Create professional coding books with AI assistance.
    """
    pass


@main.command()
@click.option('--topic', '-t', required=True, help='Book topic')
@click.option('--chapters', '-c', default=10, help='Number of chapters')
@click.option('--language', '-l', default='Python', help='Programming language')
@click.option('--audience', '-a', default='intermediate developers', help='Target audience')
@click.option('--output', '-o', default='book.json', help='Output file path')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic']), default='openai', help='LLM provider')
def create(topic, chapters, language, audience, output, provider):
    """Create a new book outline"""
    click.echo(f"Creating book outline for: {topic}")
    
    # Configure LLM
    llm_provider = LLMProvider.OPENAI if provider == 'openai' else LLMProvider.ANTHROPIC
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    # Generate outline
    generator = OutlineGenerator(llm_client)
    book = generator.generate_outline(
        topic=topic,
        num_chapters=chapters,
        target_audience=audience,
        programming_language=language
    )
    
    # Save book
    book.save(output)
    click.echo(f"✓ Book outline created and saved to: {output}")
    click.echo(f"  Title: {book.title}")
    click.echo(f"  Chapters: {len(book.chapters)}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--chapter', '-c', type=int, help='Chapter number to generate (0 for all)')
@click.option('--output', '-o', help='Output file path')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic']), default='openai', help='LLM provider')
def generate(input, chapter, output, provider):
    """Generate content for book chapters"""
    
    # Load book
    book = Book.load(input)
    click.echo(f"Loaded book: {book.title}")
    
    # Configure LLM
    llm_provider = LLMProvider.OPENAI if provider == 'openai' else LLMProvider.ANTHROPIC
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    generator = ContentGenerator(llm_client)
    code_gen = CodeGenerator(llm_client)
    
    if chapter and chapter > 0:
        # Generate single chapter
        chap = book.get_chapter(chapter)
        if not chap:
            click.echo(f"✗ Chapter {chapter} not found", err=True)
            return
        
        click.echo(f"Generating content for Chapter {chapter}: {chap.title}")
        generator.generate_complete_chapter(
            chap,
            programming_language=book.programming_language,
            target_audience=book.target_audience
        )
        
        # Add code examples to sections
        for section in chap.sections:
            click.echo(f"  - Generating code examples for: {section.title}")
            example = code_gen.generate_code_with_explanation(
                section.title,
                language=book.programming_language
            )
            section.add_code_example(
                example['code'],
                example['language'],
                example['explanation']
            )
        
        click.echo(f"✓ Chapter {chapter} content generated")
    else:
        # Generate all chapters
        for chap in book.chapters:
            click.echo(f"Generating Chapter {chap.number}: {chap.title}")
            generator.generate_complete_chapter(
                chap,
                programming_language=book.programming_language,
                target_audience=book.target_audience
            )
            
            # Add code examples
            for section in chap.sections[:2]:  # Limit to first 2 sections per chapter
                click.echo(f"  - Generating code for: {section.title}")
                example = code_gen.generate_code_with_explanation(
                    section.title,
                    language=book.programming_language
                )
                section.add_code_example(
                    example['code'],
                    example['language'],
                    example['explanation']
                )
        
        click.echo(f"✓ All chapters generated")
    
    # Save updated book
    output_path = output or input
    book.save(output_path)
    click.echo(f"✓ Book saved to: {output_path}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--format', '-f', type=click.Choice(['html', 'pdf', 'epub', 'markdown']), 
              default='html', help='Output format')
@click.option('--output', '-o', help='Output file path')
def export(input, format, output):
    """Export book to various formats"""
    
    # Load book
    book = Book.load(input)
    click.echo(f"Loaded book: {book.title}")
    
    # Determine output path
    if not output:
        base_name = os.path.splitext(input)[0]
        extensions = {'html': '.html', 'pdf': '.pdf', 'epub': '.epub', 'markdown': '.md'}
        output = base_name + extensions[format]
    
    # Export based on format
    click.echo(f"Exporting to {format.upper()}...")
    
    if format == 'html':
        formatter = HTMLFormatter()
        formatter.format(book, output)
    elif format == 'pdf':
        formatter = PDFFormatter()
        formatter.format(book, output)
    elif format == 'epub':
        formatter = EPUBFormatter()
        formatter.format(book, output)
    elif format == 'markdown':
        formatter = MarkdownFormatter()
        formatter.format(book, output)
    
    click.echo(f"✓ Book exported to: {output}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--chapter', '-c', type=int, help='Chapter number to check')
@click.option('--fix', is_flag=True, help='Automatically fix issues')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic']), default='openai', help='LLM provider')
def check(input, chapter, fix, provider):
    """Check grammar and style"""
    
    # Load book
    book = Book.load(input)
    click.echo(f"Checking book: {book.title}")
    
    # Configure LLM
    llm_provider = LLMProvider.OPENAI if provider == 'openai' else LLMProvider.ANTHROPIC
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    checker = GrammarChecker(llm_client)
    
    chapters_to_check = [book.get_chapter(chapter)] if chapter else book.chapters
    
    for chap in chapters_to_check:
        if not chap:
            continue
            
        click.echo(f"\nChapter {chap.number}: {chap.title}")
        
        # Check introduction
        if chap.introduction:
            result = checker.check_grammar(chap.introduction)
            if result['issues']:
                click.echo(f"  Introduction - Issues found:")
                for issue in result['issues']:
                    click.echo(f"    • {issue}")
                
                if fix:
                    chap.introduction = checker.fix_grammar(chap.introduction)
                    click.echo(f"  ✓ Introduction fixed")
        
        # Check sections
        for section in chap.sections:
            if section.content:
                result = checker.check_grammar(section.content)
                if result['issues']:
                    click.echo(f"  {section.title} - Issues found:")
                    for issue in result['issues']:
                        click.echo(f"    • {issue}")
                    
                    if fix:
                        section.content = checker.fix_grammar(section.content)
                        click.echo(f"  ✓ {section.title} fixed")
    
    if fix:
        book.save(input)
        click.echo(f"\n✓ Fixed book saved to: {input}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--chapter', '-c', type=int, required=True, help='Chapter number')
@click.option('--focus', '-f', 
              type=click.Choice(['clarity', 'engagement', 'conciseness', 'detail', 'examples']),
              default='clarity', help='Improvement focus')
@click.option('--output', '-o', help='Output file path')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic']), default='openai', help='LLM provider')
def improve(input, chapter, focus, output, provider):
    """Improve content quality"""
    
    # Load book
    book = Book.load(input)
    chap = book.get_chapter(chapter)
    
    if not chap:
        click.echo(f"✗ Chapter {chapter} not found", err=True)
        return
    
    click.echo(f"Improving Chapter {chapter}: {chap.title}")
    click.echo(f"Focus: {focus}")
    
    # Configure LLM
    llm_provider = LLMProvider.OPENAI if provider == 'openai' else LLMProvider.ANTHROPIC
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    improver = ContentImprover(llm_client)
    
    # Improve each section
    for section in chap.sections:
        click.echo(f"  Improving: {section.title}")
        improver.improve_section(section, focus=focus)
    
    # Save updated book
    output_path = output or input
    book.save(output_path)
    click.echo(f"✓ Improved book saved to: {output_path}")


@main.command()
@click.option('--concept', '-c', required=True, help='Concept to demonstrate')
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--difficulty', '-d', 
              type=click.Choice(['beginner', 'intermediate', 'advanced']),
              default='intermediate', help='Difficulty level')
def code_example(concept, language, difficulty):
    """Generate a code example"""
    
    click.echo(f"Generating {difficulty} {language} example for: {concept}")
    
    code_gen = CodeGenerator()
    example = code_gen.generate_code_with_explanation(concept, language, difficulty)
    
    click.echo(f"\n{example['explanation']}\n")
    click.echo(f"```{example['language']}")
    click.echo(example['code'])
    click.echo("```")


@main.command()
@click.option('--topic', '-t', required=True, help='Exercise topic')
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--difficulty', '-d',
              type=click.Choice(['beginner', 'intermediate', 'advanced']),
              default='intermediate', help='Difficulty level')
def exercise(topic, language, difficulty):
    """Generate a coding exercise"""
    
    click.echo(f"Generating {difficulty} {language} exercise on: {topic}")
    
    code_gen = CodeGenerator()
    ex = code_gen.generate_exercise(topic, language, difficulty)
    
    click.echo(f"\n📝 Exercise:\n{ex['question']}\n")
    
    if ex['hints']:
        click.echo("💡 Hints:")
        for i, hint in enumerate(ex['hints'], 1):
            click.echo(f"  {i}. {hint}")
        click.echo()
    
    click.echo(f"✅ Solution:\n```{ex['language']}\n{ex['solution']}\n```\n")
    click.echo(f"📖 Explanation:\n{ex['explanation']}")


@main.command()
@click.argument('book_file')
def info(book_file):
    """Display book information"""
    
    try:
        book = Book.load(book_file)
        
        click.echo(f"\n📚 Book Information")
        click.echo("=" * 50)
        click.echo(f"Title:      {book.title}")
        click.echo(f"Author:     {book.author}")
        click.echo(f"Language:   {book.programming_language}")
        click.echo(f"Audience:   {book.target_audience}")
        click.echo(f"Chapters:   {len(book.chapters)}")
        click.echo(f"Created:    {book.created_at}")
        click.echo(f"Updated:    {book.updated_at}")
        
        if book.description:
            click.echo(f"\nDescription:\n{book.description}")
        
        click.echo("\n📑 Chapters:")
        for chapter in book.chapters:
            sections_count = len(chapter.sections)
            click.echo(f"  {chapter.number}. {chapter.title} ({sections_count} sections)")
        
    except Exception as e:
        click.echo(f"✗ Error loading book: {e}", err=True)


if __name__ == '__main__':
    main()
