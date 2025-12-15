"""
Tests for Agentic-First Mode models and state machine.
"""

import pytest
from datetime import datetime

from book_creator.models.agentic import (
    LifecycleState,
    ComplexityLevel,
    ReviewStatus,
    UserPrompt,
    LearningObjective,
    ChapterBlueprint,
    BookBlueprint,
    ReviewResult,
    AgenticState
)


class TestLifecycleState:
    """Tests for LifecycleState enum."""
    
    def test_all_states_defined(self):
        """Test that all required states are defined."""
        expected_states = [
            "INIT", "INTERPRET", "PLAN", "WRITE", "REVIEW",
            "REPAIR", "FORMAT", "EXPORT", "COMPLETE", "FAILED"
        ]
        for state_name in expected_states:
            assert hasattr(LifecycleState, state_name)
    
    def test_state_values(self):
        """Test state values are lowercase strings."""
        assert LifecycleState.INIT.value == "init"
        assert LifecycleState.COMPLETE.value == "complete"


class TestComplexityLevel:
    """Tests for ComplexityLevel enum."""
    
    def test_all_levels_defined(self):
        """Test that all complexity levels are defined."""
        expected_levels = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
        for level_name in expected_levels:
            assert hasattr(ComplexityLevel, level_name)


class TestUserPrompt:
    """Tests for UserPrompt dataclass."""
    
    def test_creation_minimal(self):
        """Test creating a UserPrompt with minimal fields."""
        prompt = UserPrompt(topic="Python Programming")
        assert prompt.topic == "Python Programming"
        assert prompt.audience == ""
        assert prompt.tone == "professional"
        assert prompt.include_exercises is True
    
    def test_creation_full(self):
        """Test creating a UserPrompt with all fields."""
        prompt = UserPrompt(
            topic="Python Programming",
            audience="beginners",
            learning_outcome="Learn to code",
            complexity_level=ComplexityLevel.BEGINNER,
            book_length=10,
            tone="casual",
            output_format="pdf",
            region_context="US students",
            include_exercises=True,
            include_code_examples=True,
            programming_language="Python"
        )
        assert prompt.topic == "Python Programming"
        assert prompt.complexity_level == ComplexityLevel.BEGINNER
        assert prompt.book_length == 10
    
    def test_to_dict(self):
        """Test converting UserPrompt to dictionary."""
        prompt = UserPrompt(
            topic="Test Topic",
            audience="students",
            complexity_level=ComplexityLevel.INTERMEDIATE
        )
        data = prompt.to_dict()
        
        assert data["topic"] == "Test Topic"
        assert data["audience"] == "students"
        assert data["complexity_level"] == "intermediate"
    
    def test_from_dict(self):
        """Test creating UserPrompt from dictionary."""
        data = {
            "topic": "Test Topic",
            "audience": "students",
            "complexity_level": "advanced",
            "book_length": 15
        }
        prompt = UserPrompt.from_dict(data)
        
        assert prompt.topic == "Test Topic"
        assert prompt.audience == "students"
        assert prompt.complexity_level == ComplexityLevel.ADVANCED
        assert prompt.book_length == 15


class TestLearningObjective:
    """Tests for LearningObjective dataclass."""
    
    def test_creation(self):
        """Test creating a LearningObjective."""
        obj = LearningObjective(
            description="Understand variables",
            bloom_level="understand"
        )
        assert obj.description == "Understand variables"
        assert obj.bloom_level == "understand"
    
    def test_default_bloom_level(self):
        """Test default bloom level."""
        obj = LearningObjective(description="Test objective")
        assert obj.bloom_level == "understand"


class TestChapterBlueprint:
    """Tests for ChapterBlueprint dataclass."""
    
    def test_creation(self):
        """Test creating a ChapterBlueprint."""
        chapter = ChapterBlueprint(
            number=1,
            title="Introduction",
            description="Getting started",
            complexity_level=ComplexityLevel.BEGINNER,
            estimated_length=2000
        )
        assert chapter.number == 1
        assert chapter.title == "Introduction"
        assert chapter.review_status == ReviewStatus.PENDING
    
    def test_to_dict(self):
        """Test converting ChapterBlueprint to dictionary."""
        chapter = ChapterBlueprint(
            number=1,
            title="Test Chapter",
            description="Test description",
            complexity_level=ComplexityLevel.INTERMEDIATE,
            estimated_length=2500,
            section_titles=["Section 1", "Section 2"],
            key_concepts=["concept1", "concept2"]
        )
        data = chapter.to_dict()
        
        assert data["number"] == 1
        assert data["title"] == "Test Chapter"
        assert data["complexity_level"] == "intermediate"
        assert len(data["section_titles"]) == 2
    
    def test_from_dict(self):
        """Test creating ChapterBlueprint from dictionary."""
        data = {
            "number": 2,
            "title": "Variables",
            "description": "Learning about variables",
            "complexity_level": "beginner",
            "estimated_length": 1500,
            "section_titles": ["What are variables", "Variable types"]
        }
        chapter = ChapterBlueprint.from_dict(data)
        
        assert chapter.number == 2
        assert chapter.title == "Variables"
        assert chapter.complexity_level == ComplexityLevel.BEGINNER


class TestBookBlueprint:
    """Tests for BookBlueprint dataclass."""
    
    def test_creation(self):
        """Test creating a BookBlueprint."""
        blueprint = BookBlueprint(
            title="Python for Beginners",
            target_audience="beginners",
            complexity_level=ComplexityLevel.BEGINNER,
            total_chapters=10
        )
        assert blueprint.title == "Python for Beginners"
        assert blueprint.total_chapters == 10
    
    def test_to_dict(self):
        """Test converting BookBlueprint to dictionary."""
        chapter = ChapterBlueprint(
            number=1,
            title="Chapter 1",
            description="First chapter",
            complexity_level=ComplexityLevel.BEGINNER,
            estimated_length=2000
        )
        blueprint = BookBlueprint(
            title="Test Book",
            target_audience="students",
            chapters=[chapter]
        )
        data = blueprint.to_dict()
        
        assert data["title"] == "Test Book"
        assert len(data["chapters"]) == 1
        assert "created_at" in data
    
    def test_from_dict(self):
        """Test creating BookBlueprint from dictionary."""
        data = {
            "title": "Test Book",
            "target_audience": "professionals",
            "complexity_level": "advanced",
            "chapters": [
                {
                    "number": 1,
                    "title": "Chapter 1",
                    "description": "First chapter",
                    "complexity_level": "intermediate",
                    "estimated_length": 2000
                }
            ]
        }
        blueprint = BookBlueprint.from_dict(data)
        
        assert blueprint.title == "Test Book"
        assert blueprint.complexity_level == ComplexityLevel.ADVANCED
        assert len(blueprint.chapters) == 1


class TestReviewResult:
    """Tests for ReviewResult dataclass."""
    
    def test_creation_passed(self):
        """Test creating a passed ReviewResult."""
        result = ReviewResult(passed=True, chapter_number=1)
        assert result.passed is True
        assert result.chapter_number == 1
        assert len(result.issues) == 0
    
    def test_creation_failed(self):
        """Test creating a failed ReviewResult."""
        result = ReviewResult(
            passed=False,
            chapter_number=2,
            issues=["Too short", "Missing examples"]
        )
        assert result.passed is False
        assert len(result.issues) == 2
    
    def test_to_dict(self):
        """Test converting ReviewResult to dictionary."""
        result = ReviewResult(
            passed=False,
            chapter_number=1,
            issues=["Issue 1"],
            coherence_issues=["Coherence issue"],
            complexity_issues=["Complexity issue"]
        )
        data = result.to_dict()
        
        assert data["passed"] is False
        assert len(data["coherence_issues"]) == 1


class TestAgenticState:
    """Tests for AgenticState and state machine transitions."""
    
    def test_initial_state(self):
        """Test initial state is INIT."""
        state = AgenticState()
        assert state.current_state == LifecycleState.INIT
    
    def test_valid_transitions(self):
        """Test valid state transitions."""
        state = AgenticState()
        
        # INIT -> INTERPRET
        assert state.can_transition_to(LifecycleState.INTERPRET)
        assert state.transition_to(LifecycleState.INTERPRET)
        assert state.current_state == LifecycleState.INTERPRET
        
        # INTERPRET -> PLAN
        assert state.can_transition_to(LifecycleState.PLAN)
        assert state.transition_to(LifecycleState.PLAN)
        
        # PLAN -> WRITE
        assert state.can_transition_to(LifecycleState.WRITE)
        assert state.transition_to(LifecycleState.WRITE)
        
        # WRITE -> REVIEW
        assert state.can_transition_to(LifecycleState.REVIEW)
        assert state.transition_to(LifecycleState.REVIEW)
    
    def test_invalid_transitions(self):
        """Test invalid state transitions are rejected."""
        state = AgenticState()
        
        # Cannot skip INTERPRET
        assert not state.can_transition_to(LifecycleState.PLAN)
        assert not state.transition_to(LifecycleState.PLAN)
        assert state.current_state == LifecycleState.INIT
    
    def test_review_to_repair_transition(self):
        """Test REVIEW -> REPAIR transition."""
        state = AgenticState()
        state.current_state = LifecycleState.REVIEW
        
        assert state.can_transition_to(LifecycleState.REPAIR)
        assert state.transition_to(LifecycleState.REPAIR)
    
    def test_review_to_format_transition(self):
        """Test REVIEW -> FORMAT transition."""
        state = AgenticState()
        state.current_state = LifecycleState.REVIEW
        
        assert state.can_transition_to(LifecycleState.FORMAT)
        assert state.transition_to(LifecycleState.FORMAT)
    
    def test_repair_to_review_transition(self):
        """Test REPAIR -> REVIEW transition."""
        state = AgenticState()
        state.current_state = LifecycleState.REPAIR
        
        assert state.can_transition_to(LifecycleState.REVIEW)
        assert state.transition_to(LifecycleState.REVIEW)
    
    def test_complete_is_terminal(self):
        """Test COMPLETE is a terminal state."""
        state = AgenticState()
        state.current_state = LifecycleState.COMPLETE
        
        assert not state.can_transition_to(LifecycleState.INIT)
        assert not state.can_transition_to(LifecycleState.WRITE)
    
    def test_failed_is_terminal(self):
        """Test FAILED is a terminal state."""
        state = AgenticState()
        state.current_state = LifecycleState.FAILED
        
        assert not state.can_transition_to(LifecycleState.INIT)
        assert not state.can_transition_to(LifecycleState.REPAIR)
    
    def test_fail_from_any_state(self):
        """Test that FAILED can be reached from any non-terminal state."""
        non_terminal_states = [
            LifecycleState.INIT,
            LifecycleState.INTERPRET,
            LifecycleState.PLAN,
            LifecycleState.WRITE,
            LifecycleState.REVIEW,
            LifecycleState.REPAIR,
            LifecycleState.FORMAT,
            LifecycleState.EXPORT
        ]
        
        for start_state in non_terminal_states:
            state = AgenticState()
            state.current_state = start_state
            assert state.can_transition_to(LifecycleState.FAILED), \
                f"Should be able to fail from {start_state.value}"
    
    def test_complete_sets_timestamp(self):
        """Test that completing sets the completed_at timestamp."""
        state = AgenticState()
        state.current_state = LifecycleState.EXPORT
        
        assert state.completed_at is None
        state.transition_to(LifecycleState.COMPLETE)
        assert state.completed_at is not None
    
    def test_to_dict(self):
        """Test converting AgenticState to dictionary."""
        state = AgenticState()
        state.user_prompt = UserPrompt(topic="Test")
        state.errors = ["Error 1"]
        
        data = state.to_dict()
        
        assert data["current_state"] == "init"
        assert data["user_prompt"]["topic"] == "Test"
        assert len(data["errors"]) == 1


class TestFullLifecycle:
    """Tests for complete lifecycle transitions."""
    
    def test_happy_path_lifecycle(self):
        """Test complete happy path through lifecycle."""
        state = AgenticState()
        
        transitions = [
            LifecycleState.INTERPRET,
            LifecycleState.PLAN,
            LifecycleState.WRITE,
            LifecycleState.REVIEW,
            LifecycleState.FORMAT,
            LifecycleState.EXPORT,
            LifecycleState.COMPLETE
        ]
        
        for new_state in transitions:
            assert state.transition_to(new_state), \
                f"Failed to transition to {new_state.value}"
        
        assert state.current_state == LifecycleState.COMPLETE
    
    def test_repair_loop_lifecycle(self):
        """Test lifecycle with repair loop."""
        state = AgenticState()
        
        # Get to REVIEW
        state.transition_to(LifecycleState.INTERPRET)
        state.transition_to(LifecycleState.PLAN)
        state.transition_to(LifecycleState.WRITE)
        state.transition_to(LifecycleState.REVIEW)
        
        # Repair loop
        for _ in range(3):
            assert state.transition_to(LifecycleState.REPAIR)
            assert state.transition_to(LifecycleState.REVIEW)
        
        # Continue to completion
        state.transition_to(LifecycleState.FORMAT)
        state.transition_to(LifecycleState.EXPORT)
        state.transition_to(LifecycleState.COMPLETE)
        
        assert state.current_state == LifecycleState.COMPLETE
