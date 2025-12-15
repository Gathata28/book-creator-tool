"""
Planner Agent for Agentic-First Mode.

The Planner Agent is responsible for:
- Interpreting the user prompt
- Defining learning objectives
- Designing the table of contents
- Assigning complexity levels per section
- Estimating total length

Input: User prompt, preferences
Output: Book plan schema (BookBlueprint)

Based on PRD Section 5.0.1
"""

import json
import re
from typing import Optional, List, Any

from ..models.agentic import (
    UserPrompt,
    BookBlueprint,
    ChapterBlueprint,
    LearningObjective,
    ComplexityLevel
)
from ..utils.llm_client import LLMClient, LLMConfig


def _extract_json_object(text: str) -> Optional[dict]:
    """
    Extract a JSON object from text, handling nested structures.
    
    Uses a balanced brace approach to handle nested JSON objects.
    """
    # First try to find JSON by looking for balanced braces
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


def _extract_json_array(text: str) -> Optional[list]:
    """
    Extract a JSON array from text, handling nested structures.
    
    Uses a balanced bracket approach to handle nested arrays.
    """
    # First try to find JSON by looking for balanced brackets
    start = text.find('[')
    if start == -1:
        return None
    
    depth = 0
    end = start
    for i, char in enumerate(text[start:], start):
        if char == '[':
            depth += 1
        elif char == ']':
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


class PlannerAgent:
    """
    Planner Agent for interpreting prompts and designing book structure.
    
    This agent interprets user prompts and generates a comprehensive
    book blueprint that guides the Author Agent.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())
    
    def interpret_prompt(self, raw_prompt: str) -> UserPrompt:
        """
        Parse a natural language prompt into structured UserPrompt.
        
        Extracts:
        - Core topic
        - Intended audience
        - Desired learning outcome
        - Optional constraints (complexity, length, tone, format)
        """
        system_prompt = """You are an expert at interpreting book creation requests.
Extract the following information from the user's prompt:

Required:
1. topic: The main subject of the book
2. audience: Who the book is for (e.g., "beginners", "university students", "professionals")
3. learning_outcome: What readers should learn or be able to do

Optional (extract if mentioned):
4. complexity_level: beginner, intermediate, advanced, or expert
5. book_length: estimated number of chapters (default 10 if not specified)
6. tone: professional, casual, academic, technical (default professional)
7. output_format: pdf, epub, html, markdown (default pdf)
8. region_context: geographic or cultural context
9. include_exercises: true/false (default true)
10. include_code_examples: true/false (default true if technical)
11. programming_language: if it's a coding book

Return the result as valid JSON only, no other text."""

        prompt = f"""Parse this book request and extract structured information:

"{raw_prompt}"

Return as JSON with these fields:
{{
    "topic": "...",
    "audience": "...",
    "learning_outcome": "...",
    "complexity_level": "beginner|intermediate|advanced|expert" or null,
    "book_length": number or null,
    "tone": "professional|casual|academic|technical",
    "output_format": "pdf|epub|html|markdown",
    "region_context": "..." or "",
    "include_exercises": true|false,
    "include_code_examples": true|false,
    "programming_language": "..." or ""
}}"""

        response = self.llm_client.generate_text(prompt, system_prompt)
        
        # Parse JSON from response using balanced brace extraction
        try:
            data = _extract_json_object(response)
            if data is None:
                # Fallback to direct parsing
                data = json.loads(response)
            
            return UserPrompt.from_dict(data)
        except json.JSONDecodeError:
            # Fallback: create basic prompt from raw text
            return UserPrompt(
                topic=raw_prompt,
                audience="general readers",
                learning_outcome=f"Understand {raw_prompt}"
            )
    
    def create_blueprint(self, user_prompt: UserPrompt) -> BookBlueprint:
        """
        Generate a complete book blueprint from the user prompt.
        
        This is the main output of the Planner Agent as specified in PRD 5.0.1.
        """
        # Generate title and description
        title, description = self._generate_title_and_description(user_prompt)
        
        # Determine complexity level
        complexity = user_prompt.complexity_level or self._infer_complexity(user_prompt)
        
        # Generate learning objectives for the entire book
        book_objectives = self._generate_book_objectives(user_prompt)
        
        # Infer assumed prior knowledge
        prior_knowledge = self._infer_prior_knowledge(user_prompt, complexity)
        
        # Generate chapter blueprints
        num_chapters = user_prompt.book_length or 10
        chapters = self._generate_chapter_blueprints(user_prompt, num_chapters, complexity)
        
        # Calculate estimates
        estimated_words = sum(ch.estimated_length for ch in chapters)
        estimated_pages = estimated_words // 250  # ~250 words per page
        
        return BookBlueprint(
            title=title,
            description=description,
            target_audience=user_prompt.audience or "general readers",
            assumed_prior_knowledge=prior_knowledge,
            complexity_level=complexity,
            learning_objectives=book_objectives,
            chapters=chapters,
            total_chapters=len(chapters),
            estimated_total_words=estimated_words,
            estimated_pages=estimated_pages,
            tone=user_prompt.tone,
            output_format=user_prompt.output_format,
            programming_language=user_prompt.programming_language,
            include_exercises=user_prompt.include_exercises,
            include_code_examples=user_prompt.include_code_examples
        )
    
    def _generate_title_and_description(self, prompt: UserPrompt) -> tuple:
        """Generate book title and description."""
        system_prompt = """You are a professional book editor. Generate a compelling 
title and description for a book based on the topic and audience."""

        request = f"""Generate a title and description for a book about:
Topic: {prompt.topic}
Audience: {prompt.audience}
Learning Outcome: {prompt.learning_outcome}
Tone: {prompt.tone}

Return as JSON:
{{"title": "...", "description": "..."}}"""

        response = self.llm_client.generate_text(request, system_prompt)
        
        try:
            data = _extract_json_object(response)
            if data:
                return data.get("title", f"Mastering {prompt.topic}"), data.get("description", "")
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return f"Mastering {prompt.topic}", f"A comprehensive guide to {prompt.topic}"
    
    def _infer_complexity(self, prompt: UserPrompt) -> ComplexityLevel:
        """Infer complexity level from audience and context."""
        audience_lower = prompt.audience.lower()
        
        if any(word in audience_lower for word in ["beginner", "new", "intro", "basic", "children", "kids"]):
            return ComplexityLevel.BEGINNER
        elif any(word in audience_lower for word in ["advanced", "senior", "expert", "professional"]):
            return ComplexityLevel.ADVANCED
        elif any(word in audience_lower for word in ["expert", "specialist", "researcher"]):
            return ComplexityLevel.EXPERT
        else:
            return ComplexityLevel.INTERMEDIATE
    
    def _generate_book_objectives(self, prompt: UserPrompt) -> List[LearningObjective]:
        """Generate high-level learning objectives for the book."""
        system_prompt = """You are an instructional designer. Generate 3-5 clear, 
measurable learning objectives for a book. Use Bloom's Taxonomy verbs."""

        request = f"""Generate learning objectives for a book about:
Topic: {prompt.topic}
Audience: {prompt.audience}
Learning Outcome: {prompt.learning_outcome}

Return as JSON array:
[{{"description": "...", "bloom_level": "remember|understand|apply|analyze|evaluate|create"}}]"""

        response = self.llm_client.generate_text(request, system_prompt)
        
        try:
            data = _extract_json_array(response)
            if data and isinstance(data, list):
                return [
                    LearningObjective(
                        description=obj.get("description", ""),
                        bloom_level=obj.get("bloom_level", "understand")
                    )
                    for obj in data
                ]
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback objectives
        return [
            LearningObjective(description=f"Understand the fundamentals of {prompt.topic}"),
            LearningObjective(description=f"Apply {prompt.topic} concepts in practice", bloom_level="apply"),
            LearningObjective(description=f"Analyze problems using {prompt.topic}", bloom_level="analyze")
        ]
    
    def _infer_prior_knowledge(self, prompt: UserPrompt, complexity: ComplexityLevel) -> List[str]:
        """Infer assumed prior knowledge based on complexity and audience."""
        system_prompt = """You are an instructional designer. Identify what prior 
knowledge readers should have before reading this book."""

        request = f"""What prior knowledge should readers have for a {complexity.value}-level 
book about {prompt.topic} for {prompt.audience}?

Return as JSON array of strings: ["...", "...", "..."]"""

        response = self.llm_client.generate_text(request, system_prompt)
        
        try:
            data = _extract_json_array(response)
            if data and isinstance(data, list):
                return data
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback
        if complexity == ComplexityLevel.BEGINNER:
            return ["No prior knowledge required"]
        elif complexity == ComplexityLevel.INTERMEDIATE:
            return [f"Basic familiarity with {prompt.topic}"]
        else:
            return [f"Strong foundation in {prompt.topic}"]
    
    def _generate_chapter_blueprints(
        self,
        prompt: UserPrompt,
        num_chapters: int,
        complexity: ComplexityLevel
    ) -> List[ChapterBlueprint]:
        """Generate detailed blueprints for all chapters."""
        system_prompt = """You are an expert technical writer and instructional designer.
Design a comprehensive chapter outline for a book. Each chapter should build on previous ones."""

        request = f"""Design {num_chapters} chapters for a book about:
Topic: {prompt.topic}
Audience: {prompt.audience}
Complexity: {complexity.value}
Include exercises: {prompt.include_exercises}
Include code examples: {prompt.include_code_examples}
Programming language: {prompt.programming_language or "N/A"}

For each chapter, provide:
1. title: Chapter title
2. description: Brief description (1-2 sentences)
3. section_titles: List of 3-5 sections
4. key_concepts: List of concepts introduced
5. estimated_length: Word count (1500-3000 words)

Return as JSON array:
[{{"title": "...", "description": "...", "section_titles": [...], "key_concepts": [...], "estimated_length": ...}}]"""

        response = self.llm_client.generate_text(request, system_prompt)
        
        chapters = []
        try:
            data = _extract_json_array(response)
            if data and isinstance(data, list):
                all_concepts = []  # Track concepts for prerequisites
                
                for i, ch_data in enumerate(data[:num_chapters], 1):
                    # Chapter complexity can progress
                    ch_complexity = self._get_chapter_complexity(i, num_chapters, complexity)
                    
                    # Prerequisites are concepts from previous chapters
                    prerequisites = all_concepts.copy()
                    
                    chapter = ChapterBlueprint(
                        number=i,
                        title=ch_data.get("title", f"Chapter {i}"),
                        description=ch_data.get("description", ""),
                        complexity_level=ch_complexity,
                        estimated_length=ch_data.get("estimated_length", 2000),
                        section_titles=ch_data.get("section_titles", []),
                        key_concepts=ch_data.get("key_concepts", []),
                        prerequisites=prerequisites[:5]  # Limit to most recent 5
                    )
                    
                    # Add chapter's concepts to tracking
                    all_concepts.extend(ch_data.get("key_concepts", []))
                    
                    chapters.append(chapter)
                    
        except (json.JSONDecodeError, AttributeError):
            # Fallback: generate basic chapters
            for i in range(1, num_chapters + 1):
                chapters.append(ChapterBlueprint(
                    number=i,
                    title=f"Chapter {i}: {prompt.topic} - Part {i}",
                    description=f"Part {i} of {prompt.topic}",
                    complexity_level=complexity,
                    estimated_length=2000,
                    section_titles=[f"Section {i}.1", f"Section {i}.2", f"Section {i}.3"]
                ))
        
        return chapters
    
    def _get_chapter_complexity(
        self,
        chapter_num: int,
        total_chapters: int,
        base_complexity: ComplexityLevel
    ) -> ComplexityLevel:
        """
        Determine complexity for a chapter based on progression.
        
        Books typically start simpler and progress to more complex topics.
        """
        progress = chapter_num / total_chapters
        
        if base_complexity == ComplexityLevel.BEGINNER:
            return ComplexityLevel.BEGINNER
        elif base_complexity == ComplexityLevel.INTERMEDIATE:
            if progress < 0.3:
                return ComplexityLevel.BEGINNER
            else:
                return ComplexityLevel.INTERMEDIATE
        elif base_complexity == ComplexityLevel.ADVANCED:
            if progress < 0.2:
                return ComplexityLevel.BEGINNER
            elif progress < 0.5:
                return ComplexityLevel.INTERMEDIATE
            else:
                return ComplexityLevel.ADVANCED
        else:  # EXPERT
            if progress < 0.2:
                return ComplexityLevel.INTERMEDIATE
            elif progress < 0.6:
                return ComplexityLevel.ADVANCED
            else:
                return ComplexityLevel.EXPERT
