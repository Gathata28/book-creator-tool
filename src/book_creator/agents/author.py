"""
Author Agent for Agentic-First Mode.

The Author Agent is responsible for:
- Writing chapters based on the blueprint
- Tracking introduced concepts and terminology
- Adhering to complexity and tone rules
- Maintaining narrative and conceptual continuity

Input: Book plan schema (BookBlueprint)
Output: Chapter drafts

Based on PRD Section 5.0.2
"""

import json
from typing import Optional, List, Dict, Set

from ..models.agentic import BookBlueprint, ChapterBlueprint, ComplexityLevel
from ..models.book import Book, Chapter, Section
from ..utils.llm_client import LLMClient, LLMConfig


def _extract_json_object(text: str) -> Optional[dict]:
    """
    Extract a JSON object from text, handling nested structures.
    """
    start = text.find('{')
    if start == -1:
        return None
    
    depth = 0
    end = start
    for i, char in enumerate(text[start:], start):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    if depth != 0:
        return None
    
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return None


class AuthorAgent:
    """
    Author Agent for writing chapters based on the blueprint.
    
    This agent writes chapters sequentially, tracking concepts introduced
    to maintain narrative continuity.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())
        self._introduced_concepts: Set[str] = set()
        self._terminology_map: Dict[str, str] = {}  # term -> definition
    
    def write_book(self, blueprint: BookBlueprint) -> Book:
        """
        Write the complete book based on the blueprint.
        
        Generates all chapters sequentially, maintaining continuity.
        """
        book = Book(
            title=blueprint.title,
            author=blueprint.author,
            description=blueprint.description,
            target_audience=blueprint.target_audience,
            programming_language=blueprint.programming_language
        )
        
        # Store blueprint info in metadata
        book.metadata["blueprint"] = {
            "complexity_level": blueprint.complexity_level.value,
            "learning_objectives": [
                obj.description for obj in blueprint.learning_objectives
            ],
            "assumed_prior_knowledge": blueprint.assumed_prior_knowledge
        }
        
        # Generate preface
        book.preface = self._generate_preface(blueprint)
        
        # Write each chapter
        for chapter_bp in blueprint.chapters:
            chapter = self._write_chapter(chapter_bp, blueprint)
            book.add_chapter(chapter)
        
        return book
    
    def write_chapter(
        self,
        chapter_blueprint: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Chapter:
        """Write a single chapter based on its blueprint."""
        return self._write_chapter(chapter_blueprint, blueprint)
    
    def _generate_preface(self, blueprint: BookBlueprint) -> str:
        """Generate book preface."""
        system_prompt = f"""You are writing the preface for a {blueprint.tone} book.
Keep it engaging and set clear expectations for readers."""

        prompt = f"""Write a preface for this book:

Title: {blueprint.title}
Description: {blueprint.description}
Target Audience: {blueprint.target_audience}
Complexity Level: {blueprint.complexity_level.value}

Learning Objectives:
{chr(10).join('- ' + obj.description for obj in blueprint.learning_objectives)}

Assumed Prior Knowledge:
{chr(10).join('- ' + k for k in blueprint.assumed_prior_knowledge)}

The preface should:
1. Welcome the reader
2. Explain who this book is for
3. Describe what they will learn
4. Guide them on how to use the book
5. Be 200-300 words

Write the preface:"""

        return self.llm_client.generate_text(prompt, system_prompt).strip()
    
    def _write_chapter(
        self,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Chapter:
        """Write a complete chapter based on its blueprint."""
        chapter = Chapter(
            title=chapter_bp.title,
            number=chapter_bp.number
        )
        
        # Store blueprint info in chapter metadata
        chapter.metadata["complexity_level"] = chapter_bp.complexity_level.value
        chapter.metadata["key_concepts"] = chapter_bp.key_concepts
        chapter.metadata["estimated_length"] = chapter_bp.estimated_length
        
        # Generate introduction
        chapter.introduction = self._generate_chapter_intro(chapter_bp, blueprint)
        
        # Generate each section
        for section_title in chapter_bp.section_titles:
            section = self._generate_section(
                section_title,
                chapter_bp,
                blueprint
            )
            chapter.add_section(section)
        
        # Generate summary
        chapter.summary = self._generate_chapter_summary(chapter, chapter_bp, blueprint)
        
        # Track concepts introduced in this chapter
        self._introduced_concepts.update(chapter_bp.key_concepts)
        
        return chapter
    
    def _generate_chapter_intro(
        self,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> str:
        """Generate chapter introduction."""
        system_prompt = self._get_system_prompt(blueprint, chapter_bp.complexity_level)
        
        prerequisites_text = ""
        if chapter_bp.prerequisites:
            prerequisites_text = f"""
This chapter builds on:
{chr(10).join('- ' + p for p in chapter_bp.prerequisites)}"""
        
        prompt = f"""Write an introduction for Chapter {chapter_bp.number}: {chapter_bp.title}

Chapter Description: {chapter_bp.description}

Sections in this chapter:
{chr(10).join('- ' + s for s in chapter_bp.section_titles)}

Key concepts to introduce:
{chr(10).join('- ' + c for c in chapter_bp.key_concepts)}
{prerequisites_text}

The introduction should:
1. Explain what readers will learn in this chapter
2. Motivate why this topic is important
3. Preview the main concepts
4. Be 150-250 words
5. Match complexity level: {chapter_bp.complexity_level.value}

Write the introduction:"""

        return self.llm_client.generate_text(prompt, system_prompt).strip()
    
    def _generate_section(
        self,
        section_title: str,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Section:
        """Generate a complete section with content and optionally code/exercises."""
        section = Section(title=section_title)
        
        # Generate main content
        section.content = self._generate_section_content(
            section_title,
            chapter_bp,
            blueprint
        )
        
        # Add code examples if configured
        if blueprint.include_code_examples and blueprint.programming_language:
            code_example = self._generate_code_example(
                section_title,
                chapter_bp,
                blueprint
            )
            if code_example:
                section.add_code_example(
                    code_example["code"],
                    code_example["language"],
                    code_example["explanation"]
                )
        
        # Add exercises if configured
        if blueprint.include_exercises:
            exercise = self._generate_exercise(
                section_title,
                chapter_bp,
                blueprint
            )
            if exercise:
                section.add_exercise(
                    exercise["question"],
                    exercise.get("answer", ""),
                    exercise.get("hints", [])
                )
        
        return section
    
    def _generate_section_content(
        self,
        section_title: str,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> str:
        """Generate the main content for a section."""
        system_prompt = self._get_system_prompt(blueprint, chapter_bp.complexity_level)
        
        # Reference previously introduced concepts
        concepts_context = ""
        if self._introduced_concepts:
            concepts_context = f"""
Previously introduced concepts (can reference):
{', '.join(list(self._introduced_concepts)[-10:])}"""
        
        prompt = f"""Write content for the section "{section_title}" in Chapter {chapter_bp.number}: {chapter_bp.title}

Chapter Description: {chapter_bp.description}
Complexity Level: {chapter_bp.complexity_level.value}
Target Audience: {blueprint.target_audience}
{concepts_context}

Requirements:
1. Start with a clear introduction to the concept
2. Explain key ideas step by step
3. Use clear and concise language appropriate for {chapter_bp.complexity_level.value} level
4. Include practical insights and best practices
5. Use examples and analogies to clarify complex points
6. Length: 400-600 words
7. Maintain a {blueprint.tone} tone

Write the section content:"""

        return self.llm_client.generate_text(prompt, system_prompt).strip()
    
    def _generate_code_example(
        self,
        section_title: str,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Optional[Dict]:
        """Generate a code example for the section."""
        system_prompt = f"""You are an expert {blueprint.programming_language} programmer 
writing educational code examples. Write clear, well-commented code."""

        prompt = f"""Generate a code example for the section "{section_title}".

Context: Chapter {chapter_bp.number}: {chapter_bp.title}
Programming Language: {blueprint.programming_language}
Complexity Level: {chapter_bp.complexity_level.value}

Requirements:
1. Code should demonstrate the concept from the section
2. Include clear comments
3. Keep it concise but complete
4. Match complexity level
5. Return as JSON: {{"code": "...", "language": "{blueprint.programming_language.lower()}", "explanation": "..."}}

Generate the code example:"""

        try:
            response = self.llm_client.generate_text(prompt, system_prompt)
            return _extract_json_object(response)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return None
    
    def _generate_exercise(
        self,
        section_title: str,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Optional[Dict]:
        """Generate an exercise for the section."""
        system_prompt = """You are an experienced educator creating practice exercises.
Design exercises that reinforce learning without being too difficult."""

        complexity_guidance = {
            ComplexityLevel.BEGINNER: "simple, straightforward exercise",
            ComplexityLevel.INTERMEDIATE: "moderately challenging exercise",
            ComplexityLevel.ADVANCED: "challenging exercise requiring deeper thinking",
            ComplexityLevel.EXPERT: "complex exercise requiring synthesis of concepts"
        }

        prompt = f"""Create a {complexity_guidance[chapter_bp.complexity_level]} for the section "{section_title}".

Context: Chapter {chapter_bp.number}: {chapter_bp.title}
Complexity Level: {chapter_bp.complexity_level.value}
Target Audience: {blueprint.target_audience}

Return as JSON:
{{"question": "...", "answer": "...", "hints": ["hint1", "hint2"]}}

Generate the exercise:"""

        try:
            response = self.llm_client.generate_text(prompt, system_prompt)
            return _extract_json_object(response)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return None
    
    def _generate_chapter_summary(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> str:
        """Generate chapter summary."""
        system_prompt = self._get_system_prompt(blueprint, chapter_bp.complexity_level)
        
        prompt = f"""Write a summary for Chapter {chapter_bp.number}: {chapter.title}

Sections covered:
{chr(10).join('- ' + s.title for s in chapter.sections)}

Key concepts:
{chr(10).join('- ' + c for c in chapter_bp.key_concepts)}

The summary should:
1. Recap the key concepts covered
2. Highlight the most important takeaways
3. Connect to what comes next (if applicable)
4. Be 100-150 words

Write the summary:"""

        return self.llm_client.generate_text(prompt, system_prompt).strip()
    
    def _get_system_prompt(
        self,
        blueprint: BookBlueprint,
        complexity: ComplexityLevel
    ) -> str:
        """Get the appropriate system prompt based on blueprint settings."""
        complexity_guidelines = {
            ComplexityLevel.BEGINNER: "Use simple language, avoid jargon, explain every term",
            ComplexityLevel.INTERMEDIATE: "Use moderate technical language, explain complex terms",
            ComplexityLevel.ADVANCED: "Use technical language, assume reader knows fundamentals",
            ComplexityLevel.EXPERT: "Use expert terminology, focus on advanced concepts"
        }
        
        tone_guidelines = {
            "professional": "Be clear, authoritative, and well-structured",
            "casual": "Be friendly, conversational, and approachable",
            "academic": "Be formal, rigorous, and citation-aware",
            "technical": "Be precise, detailed, and technically accurate"
        }
        
        return f"""You are an expert technical writer creating educational content.

Book: {blueprint.title}
Target Audience: {blueprint.target_audience}
Complexity: {complexity.value} - {complexity_guidelines.get(complexity, "")}
Tone: {blueprint.tone} - {tone_guidelines.get(blueprint.tone, "")}

Guidelines:
- Write pedagogically sound content that builds understanding progressively
- Use examples and analogies appropriate for the audience
- Maintain consistency in terminology throughout
- Connect concepts to practical applications"""
    
    def get_introduced_concepts(self) -> Set[str]:
        """Get the set of all concepts introduced so far."""
        return self._introduced_concepts.copy()
    
    def reset_concept_tracking(self):
        """Reset concept tracking for a new book."""
        self._introduced_concepts.clear()
        self._terminology_map.clear()
