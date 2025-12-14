#!/usr/bin/env python3
"""
Demo script for Book Creator Tool

This script demonstrates the core functionality without requiring API keys.
It creates a sample book and exports it to various formats.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from book_creator.models.book import Book, Chapter, Section
from book_creator.formatters.html_formatter import HTMLFormatter
from book_creator.formatters.pdf_formatter import PDFFormatter
from book_creator.formatters.epub_formatter import EPUBFormatter
from book_creator.formatters.markdown_formatter import MarkdownFormatter


def create_demo_book():
    """Create a demo book with sample content"""
    
    print("📚 Creating demo book...")
    
    # Create book
    book = Book(
        title="Python Quick Start Guide",
        author="Book Creator Tool Demo",
        description="A quick introduction to Python programming",
        programming_language="Python",
        target_audience="beginners"
    )
    
    # Chapter 1
    chapter1 = Chapter(
        title="Introduction to Python",
        number=1,
        introduction="Python is a powerful yet easy-to-learn programming language. In this chapter, we'll explore why Python is so popular and get started with basic concepts."
    )
    
    section1 = Section(title="Why Learn Python?")
    section1.content = """Python has become one of the most popular programming languages for several reasons:

Readability: Python code is clean and easy to understand, making it perfect for beginners.

Versatility: From web development to data science, Python can handle almost any task.

Community: Python has a large, supportive community and extensive documentation.

Libraries: Thousands of libraries are available to extend Python's capabilities."""
    
    section2 = Section(title="Your First Python Program")
    section2.content = """Let's start with the classic "Hello, World!" program. This simple program demonstrates the basic syntax of Python."""
    section2.add_code_example(
        code='print("Hello, World!")\n\n# You can also use variables\nname = "Python"\nprint(f"Hello, {name}!")',
        language="python",
        explanation="The print() function displays output to the console. F-strings (formatted string literals) allow you to embed variables in strings."
    )
    
    section3 = Section(title="Variables and Data Types")
    section3.content = """Python has several built-in data types. The most common ones are integers, floats, strings, and booleans."""
    section3.add_code_example(
        code='''# Numeric types
age = 25                    # Integer
price = 19.99              # Float

# String
name = "Alice"

# Boolean
is_active = True

# Lists (ordered, mutable)
fruits = ["apple", "banana", "orange"]

# Dictionaries (key-value pairs)
person = {
    "name": "Bob",
    "age": 30,
    "city": "New York"
}''',
        language="python",
        explanation="Python automatically determines the type of a variable based on the value assigned to it. This is called dynamic typing."
    )
    
    section3.add_exercise(
        question="Create variables to store your name, age, and favorite hobby. Then print them in a formatted sentence.",
        hints=[
            "Use descriptive variable names",
            "Use an f-string to format your output",
            "Remember to use quotes for strings"
        ],
        answer='name = "Alice"\nage = 25\nhobby = "reading"\nprint(f"My name is {name}, I am {age} years old, and I love {hobby}.")'
    )
    
    chapter1.add_section(section1)
    chapter1.add_section(section2)
    chapter1.add_section(section3)
    chapter1.summary = "In this chapter, you learned why Python is popular, wrote your first Python program, and explored basic data types. You're now ready to dive deeper into Python programming!"
    
    book.add_chapter(chapter1)
    
    # Chapter 2
    chapter2 = Chapter(
        title="Control Flow",
        number=2,
        introduction="Control flow statements allow you to control the execution of your code. You'll learn about conditionals and loops in this chapter."
    )
    
    section4 = Section(title="If Statements")
    section4.content = """If statements allow your program to make decisions based on conditions. They're fundamental to writing dynamic programs."""
    section4.add_code_example(
        code='''age = 18

if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")

# Multiple conditions
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Your grade is: {grade}")''',
        language="python",
        explanation="Python uses indentation to define code blocks. The elif keyword is short for 'else if'."
    )
    
    section5 = Section(title="Loops")
    section5.content = """Loops allow you to repeat code multiple times. Python has two types of loops: for loops and while loops."""
    section5.add_code_example(
        code='''# For loop
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(f"I like {fruit}")

# Range function
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4

# While loop
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1''',
        language="python",
        explanation="For loops iterate over sequences, while loops continue as long as a condition is true. The range() function generates a sequence of numbers."
    )
    
    chapter2.add_section(section4)
    chapter2.add_section(section5)
    chapter2.summary = "You now understand how to use if statements for decision-making and loops for repetition. These are essential tools for any programmer."
    
    book.add_chapter(chapter2)
    
    return book


def main():
    """Main demo function"""
    
    print("=" * 60)
    print("Book Creator Tool - Demo")
    print("=" * 60)
    print()
    
    # Create demo book
    book = create_demo_book()
    
    # Create output directory
    output_dir = "demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"✓ Book created: {book.title}")
    print(f"  Chapters: {len(book.chapters)}")
    print()
    
    # Save as JSON
    json_path = os.path.join(output_dir, "demo-book.json")
    book.save(json_path)
    print(f"✓ Saved JSON: {json_path}")
    
    # Export to HTML
    print("📄 Exporting to HTML...")
    html_formatter = HTMLFormatter()
    html_path = os.path.join(output_dir, "demo-book.html")
    html_formatter.format(book, html_path)
    print(f"✓ Exported HTML: {html_path}")
    
    # Export to Markdown
    print("📝 Exporting to Markdown...")
    md_formatter = MarkdownFormatter()
    md_path = os.path.join(output_dir, "demo-book.md")
    md_formatter.format(book, md_path)
    print(f"✓ Exported Markdown: {md_path}")
    
    # Export to PDF
    print("📕 Exporting to PDF...")
    try:
        pdf_formatter = PDFFormatter()
        pdf_path = os.path.join(output_dir, "demo-book.pdf")
        pdf_formatter.format(book, pdf_path)
        print(f"✓ Exported PDF: {pdf_path}")
    except Exception as e:
        print(f"⚠ PDF export warning: {e}")
    
    # Export to EPUB
    print("📘 Exporting to EPUB...")
    try:
        epub_formatter = EPUBFormatter()
        epub_path = os.path.join(output_dir, "demo-book.epub")
        epub_formatter.format(book, epub_path)
        print(f"✓ Exported EPUB: {epub_path}")
    except Exception as e:
        print(f"⚠ EPUB export warning: {e}")
    
    print()
    print("=" * 60)
    print("✅ Demo completed successfully!")
    print(f"📁 Check the '{output_dir}' directory for output files")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Set up your API keys in .env file (see .env.example)")
    print("2. Try: book-creator create --topic 'Your Topic'")
    print("3. Read EXAMPLES.md for more usage examples")


if __name__ == "__main__":
    main()
