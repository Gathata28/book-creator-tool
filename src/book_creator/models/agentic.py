"""
Agentic-First Mode models and state machine for autonomous book generation.

This module implements:
- Lifecycle State Machine (Section 9.0 of PRD)
- Multi-Agent Architecture schemas (Section 5.0 of PRD)
- Book Blueprint for inter-agent communication
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class LifecycleState(Enum):
    """
    Agentic Lifecycle State Machine states.
    
    The agentic system follows a deterministic lifecycle with clearly defined
    states and transitions as specified in PRD Section 9.0.
    """
    INIT = "init"           # Receive user prompt and preferences
    INTERPRET = "interpret" # Parse intent, constraints, and success criteria
    PLAN = "plan"           # Generate internal project plan and table of contents
    WRITE = "write"         # Produce draft chapters and sections
    REVIEW = "review"       # Perform coherence, quality, and complexity checks
    REPAIR = "repair"       # Fix detected issues (loop-back state)
    FORMAT = "format"       # Apply layout, front/back matter, and styling
    EXPORT = "export"       # Generate final files (PDF/EPUB/etc.)
    COMPLETE = "complete"   # Deliver output to user
    FAILED = "failed"       # Terminal failure state


class ComplexityLevel(Enum):
    """Book and section complexity levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ReviewStatus(Enum):
    """Review status for chapters."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REPAIR = "needs_repair"


@dataclass
class UserPrompt:
    """
    User prompt for Agentic-First Mode.
    
    Based on Prompt Contract (Section 1.0 of PRD):
    - Required: core topic, intended audience, desired learning outcome
    - Optional: complexity level, book length, tone/style, output format, region
    """
    # Required (Explicit or Implicit)
    topic: str
    audience: str = ""
    learning_outcome: str = ""
    
    # Optional (User-Specified)
    complexity_level: Optional[ComplexityLevel] = None
    book_length: Optional[int] = None  # Estimated number of chapters
    tone: str = "professional"  # professional, casual, academic, etc.
    output_format: str = "pdf"  # pdf, epub, html, markdown
    region_context: str = ""  # e.g., "African university students"
    
    # Additional preferences
    include_exercises: bool = True
    include_code_examples: bool = True
    programming_language: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic,
            "audience": self.audience,
            "learning_outcome": self.learning_outcome,
            "complexity_level": self.complexity_level.value if self.complexity_level else None,
            "book_length": self.book_length,
            "tone": self.tone,
            "output_format": self.output_format,
            "region_context": self.region_context,
            "include_exercises": self.include_exercises,
            "include_code_examples": self.include_code_examples,
            "programming_language": self.programming_language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPrompt':
        """Create from dictionary."""
        complexity = None
        if data.get("complexity_level"):
            complexity = ComplexityLevel(data["complexity_level"])
        
        return cls(
            topic=data.get("topic", ""),
            audience=data.get("audience", ""),
            learning_outcome=data.get("learning_outcome", ""),
            complexity_level=complexity,
            book_length=data.get("book_length"),
            tone=data.get("tone", "professional"),
            output_format=data.get("output_format", "pdf"),
            region_context=data.get("region_context", ""),
            include_exercises=data.get("include_exercises", True),
            include_code_examples=data.get("include_code_examples", True),
            programming_language=data.get("programming_language", "")
        )


@dataclass
class LearningObjective:
    """A learning objective for the book or chapter."""
    description: str
    chapter_number: Optional[int] = None
    bloom_level: str = "understand"  # remember, understand, apply, analyze, evaluate, create


@dataclass
class ChapterBlueprint:
    """
    Blueprint for a chapter in the book.
    
    Used for inter-agent communication between Planner and Author agents.
    """
    number: int
    title: str
    description: str
    complexity_level: ComplexityLevel
    estimated_length: int  # words
    section_titles: List[str] = field(default_factory=list)
    learning_objectives: List[LearningObjective] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # Concepts from previous chapters
    
    # Review tracking
    review_status: ReviewStatus = ReviewStatus.PENDING
    review_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "complexity_level": self.complexity_level.value,
            "estimated_length": self.estimated_length,
            "section_titles": self.section_titles,
            "learning_objectives": [
                {"description": obj.description, "bloom_level": obj.bloom_level}
                for obj in self.learning_objectives
            ],
            "key_concepts": self.key_concepts,
            "prerequisites": self.prerequisites,
            "review_status": self.review_status.value,
            "review_notes": self.review_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChapterBlueprint':
        """Create from dictionary."""
        objectives = [
            LearningObjective(
                description=obj.get("description", ""),
                bloom_level=obj.get("bloom_level", "understand")
            )
            for obj in data.get("learning_objectives", [])
        ]
        
        return cls(
            number=data.get("number", 0),
            title=data.get("title", ""),
            description=data.get("description", ""),
            complexity_level=ComplexityLevel(data.get("complexity_level", "intermediate")),
            estimated_length=data.get("estimated_length", 2000),
            section_titles=data.get("section_titles", []),
            learning_objectives=objectives,
            key_concepts=data.get("key_concepts", []),
            prerequisites=data.get("prerequisites", []),
            review_status=ReviewStatus(data.get("review_status", "pending")),
            review_notes=data.get("review_notes", [])
        )


@dataclass
class BookBlueprint:
    """
    Blueprint for the entire book.
    
    This is the main artifact for inter-agent communication as specified in
    PRD Section 5.0.1 (Planner Agent output) and Section 5.0.2 (Author Agent input).
    """
    title: str
    author: str = "AI Book Builder"
    description: str = ""
    
    # Inferred from user prompt
    target_audience: str = ""
    assumed_prior_knowledge: List[str] = field(default_factory=list)
    complexity_level: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    
    # Pedagogical structure
    learning_objectives: List[LearningObjective] = field(default_factory=list)
    chapters: List[ChapterBlueprint] = field(default_factory=list)
    
    # Estimated metrics
    total_chapters: int = 10
    estimated_total_words: int = 20000
    estimated_pages: int = 100
    
    # Style and format
    tone: str = "professional"
    output_format: str = "pdf"
    programming_language: str = ""
    include_exercises: bool = True
    include_code_examples: bool = True
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "target_audience": self.target_audience,
            "assumed_prior_knowledge": self.assumed_prior_knowledge,
            "complexity_level": self.complexity_level.value,
            "learning_objectives": [
                {"description": obj.description, "bloom_level": obj.bloom_level}
                for obj in self.learning_objectives
            ],
            "chapters": [ch.to_dict() for ch in self.chapters],
            "total_chapters": self.total_chapters,
            "estimated_total_words": self.estimated_total_words,
            "estimated_pages": self.estimated_pages,
            "tone": self.tone,
            "output_format": self.output_format,
            "programming_language": self.programming_language,
            "include_exercises": self.include_exercises,
            "include_code_examples": self.include_code_examples,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookBlueprint':
        """Create from dictionary."""
        objectives = [
            LearningObjective(
                description=obj.get("description", ""),
                bloom_level=obj.get("bloom_level", "understand")
            )
            for obj in data.get("learning_objectives", [])
        ]
        
        chapters = [
            ChapterBlueprint.from_dict(ch)
            for ch in data.get("chapters", [])
        ]
        
        created_at = datetime.now()
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                # If parsing fails, use current time
                created_at = datetime.now()
        
        return cls(
            title=data.get("title", ""),
            author=data.get("author", "AI Book Builder"),
            description=data.get("description", ""),
            target_audience=data.get("target_audience", ""),
            assumed_prior_knowledge=data.get("assumed_prior_knowledge", []),
            complexity_level=ComplexityLevel(data.get("complexity_level", "intermediate")),
            learning_objectives=objectives,
            chapters=chapters,
            total_chapters=data.get("total_chapters", 10),
            estimated_total_words=data.get("estimated_total_words", 20000),
            estimated_pages=data.get("estimated_pages", 100),
            tone=data.get("tone", "professional"),
            output_format=data.get("output_format", "pdf"),
            programming_language=data.get("programming_language", ""),
            include_exercises=data.get("include_exercises", True),
            include_code_examples=data.get("include_code_examples", True),
            created_at=created_at
        )


@dataclass
class ReviewResult:
    """Result from the Editor Agent review."""
    passed: bool
    chapter_number: int
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    # Issue categories based on PRD Section 10.1
    coherence_issues: List[str] = field(default_factory=list)
    complexity_issues: List[str] = field(default_factory=list)
    length_issues: List[str] = field(default_factory=list)
    topic_deviation_issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "chapter_number": self.chapter_number,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "coherence_issues": self.coherence_issues,
            "complexity_issues": self.complexity_issues,
            "length_issues": self.length_issues,
            "topic_deviation_issues": self.topic_deviation_issues
        }


@dataclass
class AgenticState:
    """
    Current state of the agentic book generation process.
    
    Tracks the lifecycle state and all artifacts produced by agents.
    """
    current_state: LifecycleState = LifecycleState.INIT
    
    # User input
    user_prompt: Optional[UserPrompt] = None
    raw_prompt: str = ""
    
    # Agent outputs
    blueprint: Optional[BookBlueprint] = None
    review_results: List[ReviewResult] = field(default_factory=list)
    
    # Progress tracking
    chapters_written: int = 0
    chapters_reviewed: int = 0
    repair_iterations: int = 0
    max_repair_iterations: int = 3
    
    # Output
    output_path: str = ""
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    
    def can_transition_to(self, new_state: LifecycleState) -> bool:
        """
        Check if transition to new state is allowed.
        
        Based on PRD Section 9.0 Allowed Transitions:
        - PLAN → WRITE
        - WRITE → REVIEW
        - REVIEW → FORMAT (if pass)
        - REVIEW → REPAIR (if fail)
        - REPAIR → REVIEW
        - FORMAT → EXPORT
        """
        allowed_transitions = {
            LifecycleState.INIT: [LifecycleState.INTERPRET, LifecycleState.FAILED],
            LifecycleState.INTERPRET: [LifecycleState.PLAN, LifecycleState.FAILED],
            LifecycleState.PLAN: [LifecycleState.WRITE, LifecycleState.FAILED],
            LifecycleState.WRITE: [LifecycleState.REVIEW, LifecycleState.FAILED],
            LifecycleState.REVIEW: [LifecycleState.FORMAT, LifecycleState.REPAIR, LifecycleState.FAILED],
            LifecycleState.REPAIR: [LifecycleState.REVIEW, LifecycleState.FAILED],
            LifecycleState.FORMAT: [LifecycleState.EXPORT, LifecycleState.FAILED],
            LifecycleState.EXPORT: [LifecycleState.COMPLETE, LifecycleState.FAILED],
            LifecycleState.COMPLETE: [],  # Terminal state
            LifecycleState.FAILED: []  # Terminal state
        }
        
        return new_state in allowed_transitions.get(self.current_state, [])
    
    def transition_to(self, new_state: LifecycleState) -> bool:
        """Transition to a new state if allowed."""
        if self.can_transition_to(new_state):
            self.current_state = new_state
            if new_state == LifecycleState.COMPLETE:
                self.completed_at = datetime.now()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_state": self.current_state.value,
            "user_prompt": self.user_prompt.to_dict() if self.user_prompt else None,
            "raw_prompt": self.raw_prompt,
            "blueprint": self.blueprint.to_dict() if self.blueprint else None,
            "review_results": [r.to_dict() for r in self.review_results],
            "chapters_written": self.chapters_written,
            "chapters_reviewed": self.chapters_reviewed,
            "repair_iterations": self.repair_iterations,
            "max_repair_iterations": self.max_repair_iterations,
            "output_path": self.output_path,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "errors": self.errors
        }
