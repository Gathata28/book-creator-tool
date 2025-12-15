"""
Editor Agent for Agentic-First Mode.

The Editor Agent is responsible for:
- Reviewing content for clarity, coherence, and flow
- Detecting contradictions and repetition
- Verifying alignment with target complexity
- Flagging chapters that need repair

Input: Chapter drafts
Output: Approved or flagged chapters (ReviewResult)

Based on PRD Section 5.0.3
"""

import json
import re
from typing import Optional, List

from ..models.agentic import (
    BookBlueprint,
    ChapterBlueprint,
    ReviewResult,
    ReviewStatus,
    ComplexityLevel
)
from ..models.book import Book, Chapter
from ..utils.llm_client import LLMClient, LLMConfig


class EditorAgent:
    """
    Editor Agent for reviewing and quality-controlling book content.
    
    This agent performs self-review for clarity, flow, and duplication,
    checks for internal contradictions, and ensures complexity alignment.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())
    
    def review_book(self, book: Book, blueprint: BookBlueprint) -> List[ReviewResult]:
        """
        Review the entire book against the blueprint.
        
        Returns a list of ReviewResults for each chapter.
        """
        results = []
        
        for chapter in book.chapters:
            # Find corresponding blueprint
            chapter_bp = None
            for bp in blueprint.chapters:
                if bp.number == chapter.number:
                    chapter_bp = bp
                    break
            
            if chapter_bp:
                result = self.review_chapter(chapter, chapter_bp, blueprint)
            else:
                # Chapter without blueprint - basic review
                result = self._basic_review(chapter)
            
            results.append(result)
        
        return results
    
    def review_chapter(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> ReviewResult:
        """
        Review a single chapter against its blueprint.
        
        Checks:
        1. Coherence and flow
        2. Complexity alignment
        3. Length compliance
        4. Topic adherence
        """
        result = ReviewResult(
            passed=True,
            chapter_number=chapter.number
        )
        
        # Check coherence
        coherence_issues = self._check_coherence(chapter)
        result.coherence_issues = coherence_issues
        
        # Check complexity alignment
        complexity_issues = self._check_complexity(chapter, chapter_bp.complexity_level)
        result.complexity_issues = complexity_issues
        
        # Check length
        length_issues = self._check_length(chapter, chapter_bp.estimated_length)
        result.length_issues = length_issues
        
        # Check topic adherence
        topic_issues = self._check_topic_adherence(chapter, chapter_bp, blueprint)
        result.topic_deviation_issues = topic_issues
        
        # Aggregate all issues
        all_issues = (
            coherence_issues + 
            complexity_issues + 
            length_issues + 
            topic_issues
        )
        
        result.issues = all_issues
        result.passed = len(all_issues) == 0
        
        # Generate suggestions if issues found
        if not result.passed:
            result.suggestions = self._generate_suggestions(chapter, all_issues)
        
        # Update blueprint status
        chapter_bp.review_status = (
            ReviewStatus.PASSED if result.passed 
            else ReviewStatus.NEEDS_REPAIR
        )
        chapter_bp.review_notes = all_issues
        
        return result
    
    def _check_coherence(self, chapter: Chapter) -> List[str]:
        """Check for coherence issues in the chapter."""
        issues = []
        
        # Combine all content for analysis
        content_parts = [chapter.introduction]
        for section in chapter.sections:
            content_parts.append(section.content)
        content_parts.append(chapter.summary)
        
        full_content = "\n\n".join(filter(None, content_parts))
        
        if not full_content.strip():
            return ["Chapter has no content"]
        
        system_prompt = """You are an expert editor reviewing content for coherence.
Check for:
1. Logical flow between paragraphs
2. Contradictions within the text
3. Undefined terms used without explanation
4. Broken progression of ideas
5. Repetitive content

Return issues as JSON array: ["issue1", "issue2", ...]
If no issues, return: []"""

        prompt = f"""Review this chapter for coherence issues:

Chapter: {chapter.title}

Content:
{full_content[:4000]}  # Limit to avoid token limits

Return issues as JSON array:"""

        try:
            response = self.llm_client.generate_text(prompt, system_prompt)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                found_issues = json.loads(json_match.group())
                if isinstance(found_issues, list):
                    issues.extend(found_issues[:5])  # Limit to 5 issues
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return issues
    
    def _check_complexity(
        self,
        chapter: Chapter,
        target_complexity: ComplexityLevel
    ) -> List[str]:
        """Check if chapter content matches target complexity."""
        issues = []
        
        content_parts = [chapter.introduction]
        for section in chapter.sections:
            content_parts.append(section.content)
        
        full_content = "\n\n".join(filter(None, content_parts))
        
        if not full_content.strip():
            return []
        
        complexity_descriptions = {
            ComplexityLevel.BEGINNER: "Simple language, no jargon, all terms explained",
            ComplexityLevel.INTERMEDIATE: "Moderate technical language, some assumed knowledge",
            ComplexityLevel.ADVANCED: "Technical language, assumes solid foundation",
            ComplexityLevel.EXPERT: "Expert terminology, advanced concepts"
        }
        
        system_prompt = """You are an expert editor checking content complexity.
Analyze if the content matches the target complexity level.
Return issues as JSON array: ["issue1", "issue2", ...]
If complexity is appropriate, return: []"""

        prompt = f"""Analyze if this content matches the target complexity:

Target Complexity: {target_complexity.value}
Expected: {complexity_descriptions[target_complexity]}

Content sample:
{full_content[:3000]}

Return complexity issues as JSON array:"""

        try:
            response = self.llm_client.generate_text(prompt, system_prompt)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                found_issues = json.loads(json_match.group())
                if isinstance(found_issues, list):
                    issues.extend(found_issues[:3])
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return issues
    
    def _check_length(
        self,
        chapter: Chapter,
        target_length: int
    ) -> List[str]:
        """Check if chapter length is within acceptable range."""
        issues = []
        
        # Calculate actual length
        word_count = 0
        
        if chapter.introduction:
            word_count += len(chapter.introduction.split())
        
        for section in chapter.sections:
            if section.content:
                word_count += len(section.content.split())
        
        if chapter.summary:
            word_count += len(chapter.summary.split())
        
        # Check against target (allow 30% variance)
        min_length = int(target_length * 0.7)
        max_length = int(target_length * 1.3)
        
        if word_count < min_length:
            issues.append(
                f"Chapter is too short: {word_count} words (target: {target_length})"
            )
        elif word_count > max_length:
            issues.append(
                f"Chapter is too long: {word_count} words (target: {target_length})"
            )
        
        return issues
    
    def _check_topic_adherence(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> List[str]:
        """Check if chapter content stays on topic."""
        issues = []
        
        content_parts = [chapter.introduction]
        for section in chapter.sections:
            content_parts.append(section.content)
        
        full_content = "\n\n".join(filter(None, content_parts))
        
        if not full_content.strip():
            return []
        
        system_prompt = """You are an expert editor checking topic adherence.
Identify any sections that deviate from the intended topic.
Return issues as JSON array: ["issue1", "issue2", ...]
If content stays on topic, return: []"""

        prompt = f"""Check if this chapter stays on topic:

Book Topic: {blueprint.title}
Chapter Topic: {chapter_bp.title}
Chapter Description: {chapter_bp.description}
Expected Key Concepts: {', '.join(chapter_bp.key_concepts)}

Content sample:
{full_content[:3000]}

Return topic deviation issues as JSON array:"""

        try:
            response = self.llm_client.generate_text(prompt, system_prompt)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                found_issues = json.loads(json_match.group())
                if isinstance(found_issues, list):
                    issues.extend(found_issues[:3])
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return issues
    
    def _generate_suggestions(
        self,
        chapter: Chapter,
        issues: List[str]
    ) -> List[str]:
        """Generate actionable suggestions to fix identified issues."""
        if not issues:
            return []
        
        system_prompt = """You are an expert editor providing actionable suggestions.
For each issue, provide a specific, actionable suggestion for improvement.
Return suggestions as JSON array: ["suggestion1", "suggestion2", ...]"""

        prompt = f"""Generate specific suggestions to fix these issues in Chapter {chapter.number}:

Issues:
{chr(10).join('- ' + issue for issue in issues)}

Return actionable suggestions as JSON array:"""

        try:
            response = self.llm_client.generate_text(prompt, system_prompt)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                if isinstance(suggestions, list):
                    return suggestions[:5]  # Limit to 5 suggestions
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback: generic suggestions based on issue types
        return ["Review and revise content addressing the identified issues"]
    
    def _basic_review(self, chapter: Chapter) -> ReviewResult:
        """Perform basic review when blueprint is not available."""
        result = ReviewResult(
            passed=True,
            chapter_number=chapter.number
        )
        
        # Basic checks
        if not chapter.introduction:
            result.issues.append("Chapter is missing introduction")
        
        if not chapter.sections:
            result.issues.append("Chapter has no sections")
        
        for section in chapter.sections:
            if not section.content:
                result.issues.append(f"Section '{section.title}' has no content")
        
        if not chapter.summary:
            result.issues.append("Chapter is missing summary")
        
        result.passed = len(result.issues) == 0
        
        return result
    
    def repair_chapter(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint,
        issues: List[str]
    ) -> Chapter:
        """
        Repair a chapter based on identified issues.
        
        This method attempts to fix the issues identified during review.
        """
        system_prompt = f"""You are an expert editor improving book content.
Fix the following issues while maintaining the {blueprint.tone} tone
and {chapter_bp.complexity_level.value} complexity level."""

        # Group issues by type and repair accordingly
        for issue in issues:
            if "too short" in issue.lower():
                chapter = self._expand_chapter(chapter, chapter_bp, blueprint)
            elif "too long" in issue.lower():
                chapter = self._compress_chapter(chapter, chapter_bp, blueprint)
            elif "complexity" in issue.lower():
                chapter = self._adjust_complexity(chapter, chapter_bp, blueprint)
        
        # General content improvement for other issues
        if any("coherence" in i.lower() or "contradiction" in i.lower() for i in issues):
            chapter = self._improve_coherence(chapter, chapter_bp, blueprint)
        
        return chapter
    
    def _expand_chapter(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Chapter:
        """Expand chapter content to meet length requirements."""
        system_prompt = f"""You are an expert writer expanding educational content.
Maintain the {blueprint.tone} tone and {chapter_bp.complexity_level.value} complexity."""

        for section in chapter.sections:
            if section.content and len(section.content.split()) < 300:
                prompt = f"""Expand this section with more detail and examples:

Section: {section.title}
Current Content: {section.content}
Complexity: {chapter_bp.complexity_level.value}

Add more explanation, examples, or practical applications.
Target: 400-600 words."""

                expanded = self.llm_client.generate_text(prompt, system_prompt)
                section.content = expanded.strip()
        
        return chapter
    
    def _compress_chapter(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Chapter:
        """Compress chapter content to meet length requirements."""
        system_prompt = f"""You are an expert editor condensing educational content.
Maintain key information while reducing verbosity."""

        for section in chapter.sections:
            if section.content and len(section.content.split()) > 600:
                prompt = f"""Condense this section while keeping key information:

Section: {section.title}
Current Content: {section.content}

Remove redundancy and focus on essential concepts.
Target: 400-500 words."""

                compressed = self.llm_client.generate_text(prompt, system_prompt)
                section.content = compressed.strip()
        
        return chapter
    
    def _adjust_complexity(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Chapter:
        """Adjust chapter complexity to match target level."""
        complexity_instructions = {
            ComplexityLevel.BEGINNER: "Simplify language, explain all terms, use basic examples",
            ComplexityLevel.INTERMEDIATE: "Use moderate technical terms with explanations",
            ComplexityLevel.ADVANCED: "Use technical language appropriately",
            ComplexityLevel.EXPERT: "Use expert terminology and advanced concepts"
        }
        
        system_prompt = f"""You are an expert editor adjusting content complexity.
Target: {chapter_bp.complexity_level.value}
Instruction: {complexity_instructions[chapter_bp.complexity_level]}"""

        for section in chapter.sections:
            if section.content:
                prompt = f"""Adjust this content to match {chapter_bp.complexity_level.value} level:

{section.content}

{complexity_instructions[chapter_bp.complexity_level]}"""

                adjusted = self.llm_client.generate_text(prompt, system_prompt)
                section.content = adjusted.strip()
        
        return chapter
    
    def _improve_coherence(
        self,
        chapter: Chapter,
        chapter_bp: ChapterBlueprint,
        blueprint: BookBlueprint
    ) -> Chapter:
        """Improve chapter coherence and flow."""
        system_prompt = """You are an expert editor improving content coherence.
Fix contradictions, improve transitions, and ensure logical flow."""

        # Improve transitions between sections
        for i, section in enumerate(chapter.sections):
            if i > 0 and section.content:
                prev_section = chapter.sections[i-1]
                prompt = f"""Improve the transition and coherence of this section:

Previous Section Summary: {prev_section.title}
Current Section: {section.title}
Current Content: {section.content}

Ensure smooth transition and logical flow from the previous section."""

                improved = self.llm_client.generate_text(prompt, system_prompt)
                section.content = improved.strip()
        
        return chapter
