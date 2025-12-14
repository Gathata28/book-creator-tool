"""
Outline generator for creating book structures
"""

from typing import List, Dict, Any, Optional
from ..models.book import Book, Chapter, Section
from ..utils.llm_client import LLMClient, LLMConfig


class OutlineGenerator:
    """Generates book outlines using LLM"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())

    def generate_outline(
        self,
        topic: str,
        num_chapters: int = 10,
        target_audience: str = "intermediate developers",
        programming_language: str = "Python"
    ) -> Book:
        """Generate a complete book outline"""
        
        system_prompt = (
            "You are an expert technical writer and educator specializing in "
            "creating comprehensive programming books. Generate well-structured, "
            "pedagogically sound book outlines."
        )

        prompt = f"""
Create a detailed outline for a coding book on the following topic:

Topic: {topic}
Programming Language: {programming_language}
Target Audience: {target_audience}
Number of Chapters: {num_chapters}

For each chapter, provide:
1. Chapter title
2. Brief description
3. 3-5 section titles

Format the response as follows:
Chapter 1: [Title]
Description: [Brief description]
Sections:
- [Section 1 title]
- [Section 2 title]
- [Section 3 title]
...

Generate the complete outline now.
"""

        response = self.llm_client.generate_text(prompt, system_prompt)
        return self._parse_outline(response, topic, programming_language, target_audience)

    def _parse_outline(
        self,
        outline_text: str,
        topic: str,
        programming_language: str,
        target_audience: str
    ) -> Book:
        """Parse LLM response into Book structure"""
        
        book = Book(
            title=f"Mastering {topic}",
            author="AI Book Creator",
            description=f"A comprehensive guide to {topic}",
            programming_language=programming_language,
            target_audience=target_audience
        )

        lines = outline_text.strip().split('\n')
        current_chapter = None
        current_chapter_num = 0
        in_sections = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Chapter "):
                if current_chapter:
                    book.add_chapter(current_chapter)
                
                current_chapter_num += 1
                parts = line.split(":", 1)
                title = parts[1].strip() if len(parts) > 1 else f"Chapter {current_chapter_num}"
                current_chapter = Chapter(
                    title=title,
                    number=current_chapter_num
                )
                in_sections = False

            elif line.startswith("Description:") and current_chapter:
                description = line.split(":", 1)[1].strip()
                current_chapter.introduction = description
                
            elif line.startswith("Sections:"):
                in_sections = True
                
            elif line.startswith("-") and current_chapter and in_sections:
                section_title = line.lstrip("- ").strip()
                if section_title:
                    section = Section(title=section_title)
                    current_chapter.add_section(section)

        if current_chapter:
            book.add_chapter(current_chapter)

        return book

    def expand_chapter(self, chapter: Chapter, detail_level: str = "medium") -> Chapter:
        """Expand a chapter with more detailed sections"""
        
        prompt = f"""
Expand the following chapter outline with more detailed sections:

Chapter: {chapter.title}
Introduction: {chapter.introduction}
Current Sections: {', '.join([s.title for s in chapter.sections])}

Generate {3 if detail_level == 'low' else 5 if detail_level == 'medium' else 8} detailed sections
for this chapter. For each section, provide a descriptive title.

Format:
- [Section 1 title]
- [Section 2 title]
...
"""

        response = self.llm_client.generate_text(prompt)
        
        # Parse new sections
        new_sections = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith("-"):
                section_title = line.lstrip("- ").strip()
                if section_title:
                    new_sections.append(Section(title=section_title))

        if new_sections:
            chapter.sections = new_sections

        return chapter
