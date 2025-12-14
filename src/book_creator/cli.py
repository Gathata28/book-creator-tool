"""
Command-line interface for the book creator tool
"""

import click
import os

from .models.book import Book
from .generators.outline_generator import OutlineGenerator
from .generators.content_generator import ContentGenerator
from .generators.code_generator import CodeGenerator
from .editors.grammar_checker import GrammarChecker
from .editors.content_improver import ContentImprover
from .editors.book_editor import BookEditor
from .formatters.html_formatter import HTMLFormatter
from .formatters.pdf_formatter import PDFFormatter
from .formatters.pandoc_pdf_formatter import PandocPDFFormatter
from .formatters.epub_formatter import EPUBFormatter
from .formatters.markdown_formatter import MarkdownFormatter
from .utils.llm_client import LLMClient, LLMConfig, LLMProvider


# Helper function to map string provider names to enum values
def get_provider_enum(provider_str: str) -> LLMProvider:
    """Convert provider string to LLMProvider enum"""
    provider_map = {
        'openai': LLMProvider.OPENAI,
        'anthropic': LLMProvider.ANTHROPIC,
        'google': LLMProvider.GOOGLE,
        'cohere': LLMProvider.COHERE,
        'mistral': LLMProvider.MISTRAL,
        'huggingface': LLMProvider.HUGGINGFACE,
        'ollama': LLMProvider.OLLAMA
    }
    return provider_map.get(provider_str, LLMProvider.OPENAI)


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
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
def create(topic, chapters, language, audience, output, provider):
    """Create a new book outline"""
    click.echo(f"Creating book outline for: {topic}")
    
    # Configure LLM
    llm_provider = get_provider_enum(provider)
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
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
def generate(input, chapter, output, provider):
    """Generate content for book chapters"""
    
    # Load book
    book = Book.load(input)
    click.echo(f"Loaded book: {book.title}")
    
    # Configure LLM
    llm_provider = get_provider_enum(provider)
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
@click.option('--format', '-f', type=click.Choice(['html', 'pdf', 'epub', 'markdown', 'pdf-pandoc']), 
              default='html', help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.option('--theme', default='tango', help='Syntax highlighting theme for pdf-pandoc (tango, pygments, kate, etc.)')
@click.option('--strict', is_flag=True, help='Strict Markdown validation for pdf-pandoc')
def export(input, format, output, theme, strict):
    """Export book to various formats"""
    
    # Load book
    book = Book.load(input)
    click.echo(f"Loaded book: {book.title}")
    
    # Determine output path
    if not output:
        base_name = os.path.splitext(input)[0]
        extensions = {'html': '.html', 'pdf': '.pdf', 'epub': '.epub', 'markdown': '.md', 'pdf-pandoc': '.pdf'}
        output = base_name + extensions[format]
    
    # Export based on format
    click.echo(f"Exporting to {format.upper()}...")
    
    if format == 'html':
        formatter = HTMLFormatter()
        formatter.format(book, output)
    elif format == 'pdf':
        formatter = PDFFormatter()
        formatter.format(book, output)
    elif format == 'pdf-pandoc':
        try:
            formatter = PandocPDFFormatter()
            click.echo(f"Using Pandoc with {theme} theme for syntax highlighting")
            formatter.format(book, output, strict_validation=strict, theme=theme)
        except RuntimeError as e:
            click.echo(f"✗ {str(e)}", err=True)
            return
        except ValueError as e:
            click.echo(f"✗ Markdown validation error:\n{str(e)}", err=True)
            return
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
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
def check(input, chapter, fix, provider):
    """Check grammar and style"""
    
    # Load book
    book = Book.load(input)
    click.echo(f"Checking book: {book.title}")
    
    # Configure LLM
    llm_provider = get_provider_enum(provider)
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
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
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
    llm_provider = get_provider_enum(provider)
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


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--output', '-o', help='Output file path')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
def generate_index(input, output, provider):
    """Generate an index of terms for the book"""
    
    book = Book.load(input)
    click.echo(f"Generating index for: {book.title}")
    
    # Configure LLM
    llm_provider = get_provider_enum(provider)
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    editor = BookEditor(llm_client)
    index = editor.generate_index(book)
    
    click.echo(f"\n📑 Index ({len(index)} terms)")
    for entry in index[:20]:  # Show first 20
        locations = ', '.join(entry['locations'][:3])
        click.echo(f"  {entry['term']}: {locations}")
    
    if len(index) > 20:
        click.echo(f"  ... and {len(index) - 20} more terms")
    
    # Save index to book metadata
    book.metadata['index'] = index
    output_path = output or input
    book.save(output_path)
    click.echo(f"\n✓ Index saved to book metadata: {output_path}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--output', '-o', help='Output file path')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
def generate_glossary(input, output, provider):
    """Generate a glossary of technical terms"""
    
    book = Book.load(input)
    click.echo(f"Generating glossary for: {book.title}")
    
    # Configure LLM
    llm_provider = get_provider_enum(provider)
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    editor = BookEditor(llm_client)
    glossary = editor.generate_glossary(book)
    
    click.echo(f"\n📖 Glossary ({len(glossary)} terms)")
    for term, definition in list(glossary.items())[:10]:
        click.echo(f"\n{term}:")
        click.echo(f"  {definition}")
    
    if len(glossary) > 10:
        click.echo(f"\n... and {len(glossary) - 10} more terms")
    
    # Save glossary to book metadata
    book.metadata['glossary'] = glossary
    output_path = output or input
    book.save(output_path)
    click.echo(f"\n✓ Glossary saved to book metadata: {output_path}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
def validate_references(input):
    """Validate cross-references in the book"""
    
    book = Book.load(input)
    click.echo(f"Validating references in: {book.title}")
    
    editor = BookEditor()
    broken_refs = editor.validate_cross_references(book)
    
    if broken_refs:
        click.echo(f"\n⚠ Found {len(broken_refs)} broken reference(s):")
        for ref in broken_refs:
            click.echo(f"  • {ref}")
    else:
        click.echo("\n✓ All references are valid!")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--output', '-o', help='Output file path')
@click.option('--style', '-s', default='PEP 8', help='Code style guide (e.g., PEP 8, Google, Airbnb)')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
def format_code(input, output, style, provider):
    """Format all code examples to follow a style guide"""
    
    book = Book.load(input)
    click.echo(f"Formatting code in: {book.title}")
    click.echo(f"Style guide: {style}")
    
    # Configure LLM
    llm_provider = get_provider_enum(provider)
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    editor = BookEditor(llm_client)
    
    click.echo("Updating code examples...")
    book = editor.batch_update_code_style(book, style)
    
    output_path = output or input
    book.save(output_path)
    click.echo(f"✓ Code formatted and saved to: {output_path}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
@click.option('--output', '-o', help='Output file path')
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'google', 'cohere', 'mistral', 'huggingface', 'ollama']), default='openai', help='LLM provider')
def add_objectives(input, output, provider):
    """Add learning objectives to each chapter"""
    
    book = Book.load(input)
    click.echo(f"Adding learning objectives to: {book.title}")
    
    # Configure LLM
    llm_provider = get_provider_enum(provider)
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    editor = BookEditor(llm_client)
    
    click.echo("Generating learning objectives for each chapter...")
    book = editor.add_learning_objectives(book)
    
    # Display objectives
    for chapter in book.chapters:
        if 'learning_objectives' in chapter.metadata:
            click.echo(f"\nChapter {chapter.number}: {chapter.title}")
            for obj in chapter.metadata['learning_objectives']:
                click.echo(f"  • {obj}")
    
    output_path = output or input
    book.save(output_path)
    click.echo(f"\n✓ Learning objectives added and saved to: {output_path}")


@main.command()
@click.option('--input', '-i', required=True, help='Input book file (JSON)')
def check_consistency(input):
    """Check content consistency across the book"""
    
    book = Book.load(input)
    click.echo(f"Checking consistency in: {book.title}")
    
    editor = BookEditor()
    issues = editor.check_content_consistency(book)
    
    total_issues = sum(len(v) for v in issues.values())
    
    if total_issues > 0:
        click.echo(f"\n⚠ Found {total_issues} consistency issue(s):\n")
        
        if issues['terminology']:
            click.echo("Terminology Issues:")
            for issue in issues['terminology']:
                click.echo(f"  • {issue}")
        
        if issues['formatting']:
            click.echo("\nFormatting Issues:")
            for issue in issues['formatting']:
                click.echo(f"  • {issue}")
        
        if issues['references']:
            click.echo("\nReference Issues:")
            for issue in issues['references']:
                click.echo(f"  • {issue}")
        
        if issues['code_style']:
            click.echo("\nCode Style Issues:")
            for issue in issues['code_style']:
                click.echo(f"  • {issue}")
    else:
        click.echo("\n✓ No consistency issues found!")


if __name__ == '__main__':
    main()
