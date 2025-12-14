"""
Data models for book structure
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class Section:
    """Represents a section within a chapter"""
    title: str
    content: str = ""
    code_examples: List[Dict[str, str]] = field(default_factory=list)
    exercises: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_code_example(self, code: str, language: str, explanation: str = ""):
        """Add a code example to the section"""
        self.code_examples.append({
            "code": code,
            "language": language,
            "explanation": explanation
        })

    def add_exercise(self, question: str, answer: str = "", hints: List[str] = None):
        """Add an exercise to the section"""
        self.exercises.append({
            "question": question,
            "answer": answer,
            "hints": hints or []
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary"""
        return {
            "title": self.title,
            "content": self.content,
            "code_examples": self.code_examples,
            "exercises": self.exercises,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Section':
        """Create section from dictionary"""
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            code_examples=data.get("code_examples", []),
            exercises=data.get("exercises", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class Chapter:
    """Represents a chapter in the book"""
    title: str
    number: int
    sections: List[Section] = field(default_factory=list)
    introduction: str = ""
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_section(self, section: Section):
        """Add a section to the chapter"""
        self.sections.append(section)

    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter to dictionary"""
        return {
            "title": self.title,
            "number": self.number,
            "introduction": self.introduction,
            "summary": self.summary,
            "sections": [s.to_dict() for s in self.sections],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chapter':
        """Create chapter from dictionary"""
        return cls(
            title=data.get("title", ""),
            number=data.get("number", 0),
            introduction=data.get("introduction", ""),
            summary=data.get("summary", ""),
            sections=[Section.from_dict(s) for s in data.get("sections", [])],
            metadata=data.get("metadata", {})
        )


@dataclass
class Book:
    """Represents a complete book"""
    title: str
    author: str
    chapters: List[Chapter] = field(default_factory=list)
    description: str = ""
    preface: str = ""
    target_audience: str = ""
    programming_language: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_chapter(self, chapter: Chapter):
        """Add a chapter to the book"""
        self.chapters.append(chapter)
        self.updated_at = datetime.now()

    def get_chapter(self, number: int) -> Optional[Chapter]:
        """Get a chapter by number"""
        for chapter in self.chapters:
            if chapter.number == number:
                return chapter
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert book to dictionary"""
        return {
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "preface": self.preface,
            "target_audience": self.target_audience,
            "programming_language": self.programming_language,
            "chapters": [c.to_dict() for c in self.chapters],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def to_json(self) -> str:
        """Convert book to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """Create book from dictionary"""
        return cls(
            title=data.get("title", ""),
            author=data.get("author", ""),
            description=data.get("description", ""),
            preface=data.get("preface", ""),
            target_audience=data.get("target_audience", ""),
            programming_language=data.get("programming_language", ""),
            chapters=[Chapter.from_dict(c) for c in data.get("chapters", [])],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Book':
        """Create book from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save(self, filepath: str):
        """Save book to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> 'Book':
        """Load book from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())
