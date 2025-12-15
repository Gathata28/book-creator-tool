"""
Agentic Book Generator - Main orchestrator for Agentic-First Mode.

This module implements the orchestration layer that coordinates the
multi-agent workflow for autonomous book generation.

Based on PRD Sections 4.0 (Generation Modes) and 9.0 (Agentic Lifecycle)
"""

import logging
from typing import Optional, Callable

from .models.agentic import (
    LifecycleState,
    UserPrompt,
    BookBlueprint,
    AgenticState
)
from .models.book import Book
from .agents.planner import PlannerAgent
from .agents.author import AuthorAgent
from .agents.editor import EditorAgent
from .agents.formatter import FormatterAgent
from .utils.llm_client import LLMClient, LLMConfig


class AgenticBookGenerator:
    """
    Main orchestrator for Agentic-First Mode book generation.
    
    This class coordinates the multi-agent workflow:
    1. INIT -> INTERPRET: Receive and parse user prompt
    2. INTERPRET -> PLAN: Generate book blueprint
    3. PLAN -> WRITE: Write all chapters
    4. WRITE -> REVIEW: Quality check content
    5. REVIEW -> REPAIR -> REVIEW: Fix issues if needed
    6. REVIEW -> FORMAT: Apply formatting
    7. FORMAT -> EXPORT: Generate final output
    8. EXPORT -> COMPLETE: Deliver result
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        """
        Initialize the agentic book generator.
        
        Args:
            llm_client: LLM client for all agents (shared)
            progress_callback: Optional callback for progress updates
                               Signature: (status_message, progress_percent)
        """
        self.llm_client = llm_client or LLMClient(LLMConfig())
        self.progress_callback = progress_callback
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm_client)
        self.author = AuthorAgent(self.llm_client)
        self.editor = EditorAgent(self.llm_client)
        self.formatter = FormatterAgent(self.llm_client)
        
        # State tracking
        self.state = AgenticState()
    
    def generate_from_prompt(
        self,
        prompt: str,
        output_path: str = "output/book",
        max_repair_iterations: int = 3
    ) -> Book:
        """
        Generate a complete book from a single prompt.
        
        This is the main entry point for Agentic-First Mode as specified
        in PRD Section 4.1.1.
        
        Args:
            prompt: Natural language book request
            output_path: Base path for output (extension will be added)
            max_repair_iterations: Maximum repair loop iterations
            
        Returns:
            The generated Book object
        """
        # Initialize state
        self.state = AgenticState()
        self.state.raw_prompt = prompt
        self.state.output_path = output_path
        self.state.max_repair_iterations = max_repair_iterations
        
        self._report_progress("Starting book generation", 0)
        
        try:
            # Phase 1: INIT -> INTERPRET
            self._transition(LifecycleState.INTERPRET)
            self._report_progress("Interpreting prompt", 5)
            user_prompt = self._interpret_prompt(prompt)
            self.state.user_prompt = user_prompt
            
            # Phase 2: INTERPRET -> PLAN
            self._transition(LifecycleState.PLAN)
            self._report_progress("Planning book structure", 10)
            blueprint = self._plan_book(user_prompt)
            self.state.blueprint = blueprint
            
            # Phase 3: PLAN -> WRITE
            self._transition(LifecycleState.WRITE)
            self._report_progress("Writing chapters", 20)
            book = self._write_book(blueprint)
            
            # Phase 4: WRITE -> REVIEW
            self._transition(LifecycleState.REVIEW)
            self._report_progress("Reviewing content", 70)
            review_results = self._review_book(book, blueprint)
            self.state.review_results = review_results
            
            # Phase 5: REVIEW -> REPAIR (if needed) -> REVIEW
            repair_iteration = 0
            while self._needs_repair(review_results) and repair_iteration < max_repair_iterations:
                self._transition(LifecycleState.REPAIR)
                self._report_progress(f"Repairing issues (iteration {repair_iteration + 1})", 75)
                book = self._repair_book(book, blueprint, review_results)
                self.state.repair_iterations = repair_iteration + 1
                
                # Re-review
                self._transition(LifecycleState.REVIEW)
                self._report_progress("Re-reviewing content", 80)
                review_results = self._review_book(book, blueprint)
                self.state.review_results = review_results
                repair_iteration += 1
            
            # Check if unresolved issues remain after repair loop
            if self._needs_repair(review_results):
                self.logger.warning(
                    "Book exported with unresolved review issues after %d repair iterations",
                    repair_iteration
                )
                book.metadata["unresolved_review_issues"] = True
            
            # Phase 6: REVIEW -> FORMAT
            self._transition(LifecycleState.FORMAT)
            self._report_progress("Formatting book", 85)
            book = self._format_book(book, blueprint)
            
            # Phase 7: FORMAT -> EXPORT
            self._transition(LifecycleState.EXPORT)
            self._report_progress("Exporting book", 90)
            output_file = self._export_book(book, blueprint, output_path)
            self.state.output_path = output_file
            
            # Phase 8: EXPORT -> COMPLETE
            self._transition(LifecycleState.COMPLETE)
            self._report_progress(f"Book generation complete: {output_file}", 100)
            
            return book
            
        except Exception as e:
            self.state.errors.append(str(e))
            self.state.transition_to(LifecycleState.FAILED)
            self.logger.error(f"Book generation failed: {e}")
            raise
    
    def _transition(self, new_state: LifecycleState):
        """Transition to a new lifecycle state."""
        if not self.state.transition_to(new_state):
            raise RuntimeError(
                f"Invalid state transition: {self.state.current_state.value} -> {new_state.value}"
            )
        self.logger.info(f"Transitioned to state: {new_state.value}")
    
    def _report_progress(self, message: str, percent: float):
        """Report progress to callback if provided."""
        self.logger.info(f"[{percent:.0f}%] {message}")
        if self.progress_callback:
            self.progress_callback(message, percent)
    
    def _interpret_prompt(self, prompt: str) -> UserPrompt:
        """Phase 1: Interpret the user prompt."""
        return self.planner.interpret_prompt(prompt)
    
    def _plan_book(self, user_prompt: UserPrompt) -> BookBlueprint:
        """Phase 2: Generate book blueprint."""
        return self.planner.create_blueprint(user_prompt)
    
    def _write_book(self, blueprint: BookBlueprint) -> Book:
        """Phase 3: Write all chapters."""
        self.author.reset_concept_tracking()
        
        total_chapters = len(blueprint.chapters)
        book = Book(
            title=blueprint.title,
            author=blueprint.author,
            description=blueprint.description,
            target_audience=blueprint.target_audience,
            programming_language=blueprint.programming_language
        )
        
        # Generate preface
        book.preface = self.author._generate_preface(blueprint)
        
        # Write each chapter with progress updates
        for i, chapter_bp in enumerate(blueprint.chapters):
            progress = 20 + (50 * (i / total_chapters))  # 20% to 70%
            self._report_progress(
                f"Writing Chapter {chapter_bp.number}: {chapter_bp.title}",
                progress
            )
            
            chapter = self.author.write_chapter(chapter_bp, blueprint)
            book.add_chapter(chapter)
            self.state.chapters_written = i + 1
        
        # Store blueprint in metadata
        book.metadata["blueprint"] = blueprint.to_dict()
        
        return book
    
    def _review_book(self, book: Book, blueprint: BookBlueprint) -> list:
        """Phase 4: Review all chapters."""
        results = []
        
        # Reset counter for this review pass (tracks reviews in current iteration)
        review_count = 0
        
        for chapter in book.chapters:
            # Find corresponding blueprint
            chapter_bp = None
            for bp in blueprint.chapters:
                if bp.number == chapter.number:
                    chapter_bp = bp
                    break
            
            if chapter_bp:
                result = self.editor.review_chapter(chapter, chapter_bp, blueprint)
            else:
                result = self.editor._basic_review(chapter)
            
            results.append(result)
            review_count += 1
        
        # Update total reviews count
        self.state.chapters_reviewed = review_count
        
        return results
    
    def _needs_repair(self, review_results: list) -> bool:
        """Check if any chapters need repair."""
        return any(not result.passed for result in review_results)
    
    def _repair_book(
        self,
        book: Book,
        blueprint: BookBlueprint,
        review_results: list
    ) -> Book:
        """Phase 5: Repair chapters with issues."""
        for result in review_results:
            if not result.passed:
                # Find the chapter and its blueprint
                chapter = book.get_chapter(result.chapter_number)
                chapter_bp = None
                for bp in blueprint.chapters:
                    if bp.number == result.chapter_number:
                        chapter_bp = bp
                        break
                
                if chapter and chapter_bp:
                    self._report_progress(
                        f"Repairing Chapter {chapter.number}",
                        75
                    )
                    
                    # Repair the chapter
                    repaired = self.editor.repair_chapter(
                        chapter,
                        chapter_bp,
                        blueprint,
                        result.issues
                    )
                    
                    # Update the book's chapter
                    for i, ch in enumerate(book.chapters):
                        if ch.number == chapter.number:
                            book.chapters[i] = repaired
                            break
        
        return book
    
    def _format_book(self, book: Book, blueprint: BookBlueprint) -> Book:
        """Phase 6: Apply formatting and generate front/back matter."""
        # The formatter agent will handle this during export
        # Here we just ensure metadata is ready
        
        if not book.preface:
            book.preface = self.formatter._generate_preface(book, blueprint)
        
        # Add learning objectives to metadata
        book.metadata["learning_objectives"] = [
            obj.description for obj in blueprint.learning_objectives
        ]
        
        # Add assumed prior knowledge
        book.metadata["assumed_prior_knowledge"] = blueprint.assumed_prior_knowledge
        
        return book
    
    def _export_book(
        self,
        book: Book,
        blueprint: BookBlueprint,
        output_path: str
    ) -> str:
        """Phase 7: Export the book to file."""
        return self.formatter.format_book(
            book,
            blueprint,
            output_path,
            blueprint.output_format
        )
    
    def get_state(self) -> AgenticState:
        """Get the current state of the generation process."""
        return self.state
    
    def get_blueprint(self) -> Optional[BookBlueprint]:
        """Get the generated blueprint (available after PLAN phase)."""
        return self.state.blueprint
    
    def get_review_results(self) -> list:
        """Get review results (available after REVIEW phase)."""
        return self.state.review_results


def generate_book_from_prompt(
    prompt: str,
    output_path: str = "output/book",
    provider: str = "openai",
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Book:
    """
    Convenience function to generate a book from a single prompt.
    
    This is the simplest way to use Agentic-First Mode:
    
    Example:
        book = generate_book_from_prompt(
            "Create a beginner-friendly book on Python programming for high school students",
            output_path="my_python_book"
        )
    
    Args:
        prompt: Natural language book request
        output_path: Base path for output file
        provider: LLM provider (openai, anthropic, etc.)
        progress_callback: Optional progress callback
        
    Returns:
        Generated Book object
    """
    from .utils.llm_client import LLMProvider
    
    # Map provider string to enum
    provider_map = {
        'openai': LLMProvider.OPENAI,
        'anthropic': LLMProvider.ANTHROPIC,
        'google': LLMProvider.GOOGLE,
        'cohere': LLMProvider.COHERE,
        'mistral': LLMProvider.MISTRAL,
        'huggingface': LLMProvider.HUGGINGFACE,
        'ollama': LLMProvider.OLLAMA
    }
    
    llm_provider = provider_map.get(provider, LLMProvider.OPENAI)
    llm_config = LLMConfig(provider=llm_provider)
    llm_client = LLMClient(llm_config)
    
    generator = AgenticBookGenerator(llm_client, progress_callback)
    return generator.generate_from_prompt(prompt, output_path)
