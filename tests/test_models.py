"""
Basic tests for book creator tool models
"""

import json
import tempfile
import os

from book_creator.models.book import Book, Chapter, Section


def test_section_creation():
    """Test creating a section"""
    section = Section(title="Test Section")
    assert section.title == "Test Section"
    assert section.content == ""
    assert len(section.code_examples) == 0
    assert len(section.exercises) == 0


def test_section_add_code_example():
    """Test adding code example to section"""
    section = Section(title="Test Section")
    section.add_code_example(
        code="print('Hello')",
        language="python",
        explanation="A simple print statement"
    )
    assert len(section.code_examples) == 1
    assert section.code_examples[0]['code'] == "print('Hello')"
    assert section.code_examples[0]['language'] == "python"


def test_section_add_exercise():
    """Test adding exercise to section"""
    section = Section(title="Test Section")
    section.add_exercise(
        question="What is 2+2?",
        answer="4",
        hints=["Think about addition", "It's less than 5"]
    )
    assert len(section.exercises) == 1
    assert section.exercises[0]['question'] == "What is 2+2?"
    assert section.exercises[0]['answer'] == "4"
    assert len(section.exercises[0]['hints']) == 2


def test_chapter_creation():
    """Test creating a chapter"""
    chapter = Chapter(title="Test Chapter", number=1)
    assert chapter.title == "Test Chapter"
    assert chapter.number == 1
    assert len(chapter.sections) == 0


def test_chapter_add_section():
    """Test adding section to chapter"""
    chapter = Chapter(title="Test Chapter", number=1)
    section = Section(title="Test Section")
    chapter.add_section(section)
    assert len(chapter.sections) == 1
    assert chapter.sections[0] == section


def test_book_creation():
    """Test creating a book"""
    book = Book(title="Test Book", author="Test Author")
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert len(book.chapters) == 0


def test_book_add_chapter():
    """Test adding chapter to book"""
    book = Book(title="Test Book", author="Test Author")
    chapter = Chapter(title="Chapter 1", number=1)
    book.add_chapter(chapter)
    assert len(book.chapters) == 1
    assert book.get_chapter(1) == chapter


def test_book_get_chapter():
    """Test getting chapter by number"""
    book = Book(title="Test Book", author="Test Author")
    chapter1 = Chapter(title="Chapter 1", number=1)
    chapter2 = Chapter(title="Chapter 2", number=2)
    book.add_chapter(chapter1)
    book.add_chapter(chapter2)
    
    assert book.get_chapter(1) == chapter1
    assert book.get_chapter(2) == chapter2
    assert book.get_chapter(3) is None


def test_book_to_dict():
    """Test converting book to dictionary"""
    book = Book(title="Test Book", author="Test Author")
    chapter = Chapter(title="Chapter 1", number=1)
    section = Section(title="Section 1", content="Test content")
    chapter.add_section(section)
    book.add_chapter(chapter)
    
    book_dict = book.to_dict()
    assert book_dict['title'] == "Test Book"
    assert book_dict['author'] == "Test Author"
    assert len(book_dict['chapters']) == 1
    assert book_dict['chapters'][0]['title'] == "Chapter 1"


def test_book_to_json():
    """Test converting book to JSON"""
    book = Book(title="Test Book", author="Test Author")
    json_str = book.to_json()
    
    # Should be valid JSON
    data = json.loads(json_str)
    assert data['title'] == "Test Book"
    assert data['author'] == "Test Author"


def test_book_from_dict():
    """Test creating book from dictionary"""
    data = {
        "title": "Test Book",
        "author": "Test Author",
        "chapters": [
            {
                "title": "Chapter 1",
                "number": 1,
                "sections": [
                    {
                        "title": "Section 1",
                        "content": "Test content"
                    }
                ]
            }
        ]
    }
    
    book = Book.from_dict(data)
    assert book.title == "Test Book"
    assert len(book.chapters) == 1
    assert len(book.chapters[0].sections) == 1


def test_book_save_and_load():
    """Test saving and loading book to/from file"""
    book = Book(title="Test Book", author="Test Author")
    chapter = Chapter(title="Chapter 1", number=1)
    section = Section(title="Section 1", content="Test content")
    chapter.add_section(section)
    book.add_chapter(chapter)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        book.save(temp_file)
        
        # Load from file
        loaded_book = Book.load(temp_file)
        
        assert loaded_book.title == book.title
        assert loaded_book.author == book.author
        assert len(loaded_book.chapters) == len(book.chapters)
        assert loaded_book.chapters[0].title == book.chapters[0].title
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_section_to_from_dict():
    """Test section serialization"""
    section = Section(title="Test Section", content="Test content")
    section.add_code_example("print('hello')", "python", "Example")
    section.add_exercise("Question?", "Answer", ["Hint 1"])
    
    # Convert to dict and back
    section_dict = section.to_dict()
    restored_section = Section.from_dict(section_dict)
    
    assert restored_section.title == section.title
    assert restored_section.content == section.content
    assert len(restored_section.code_examples) == len(section.code_examples)
    assert len(restored_section.exercises) == len(section.exercises)


def test_chapter_to_from_dict():
    """Test chapter serialization"""
    chapter = Chapter(title="Test Chapter", number=1)
    chapter.introduction = "Intro text"
    chapter.summary = "Summary text"
    section = Section(title="Section 1")
    chapter.add_section(section)
    
    # Convert to dict and back
    chapter_dict = chapter.to_dict()
    restored_chapter = Chapter.from_dict(chapter_dict)
    
    assert restored_chapter.title == chapter.title
    assert restored_chapter.number == chapter.number
    assert restored_chapter.introduction == chapter.introduction
    assert restored_chapter.summary == chapter.summary
    assert len(restored_chapter.sections) == len(chapter.sections)
