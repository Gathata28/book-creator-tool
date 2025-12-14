"""
Content generator for chapters and sections
"""

from typing import Optional
from ..models.book import Chapter, Section
from ..utils.llm_client import LLMClient, LLMConfig


class ContentGenerator:
    """Generates content for chapters and sections using LLM"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())

    def generate_section_content(
        self,
        section: Section,
        chapter_context: str = "",
        programming_language: str = "Python",
        target_audience: str = "intermediate developers"
    ) -> Section:
        """Generate detailed content for a section"""
        
        system_prompt = (
            "You are an expert technical writer creating educational content for programming books. "
            "Write clear, engaging, and pedagogically sound content."
        )

        prompt = f"""
Write detailed content for the following section in a {programming_language} programming book:

Section Title: {section.title}
{f"Chapter Context: {chapter_context}" if chapter_context else ""}
Target Audience: {target_audience}

Requirements:
1. Start with a clear introduction to the concept
2. Explain key ideas step by step
3. Use clear and concise language
4. Include practical insights and best practices
5. Length: 300-500 words

Write the section content now:
"""

        content = self.llm_client.generate_text(prompt, system_prompt)
        section.content = content.strip()
        
        return section

    def generate_chapter_introduction(
        self,
        chapter: Chapter,
        book_context: str = "",
        programming_language: str = "Python"
    ) -> str:
        """Generate an introduction for a chapter"""
        
        system_prompt = (
            "You are an expert technical writer. Write engaging chapter introductions "
            "that motivate readers and set clear learning objectives."
        )

        sections_list = "\n".join([f"- {s.title}" for s in chapter.sections])

        prompt = f"""
Write an engaging introduction for the following chapter in a {programming_language} programming book:

Chapter {chapter.number}: {chapter.title}
{f"Book Context: {book_context}" if book_context else ""}

Sections in this chapter:
{sections_list}

The introduction should:
1. Explain what readers will learn
2. Motivate why this chapter is important
3. Preview the main topics covered
4. Length: 150-250 words

Write the introduction now:
"""

        introduction = self.llm_client.generate_text(prompt, system_prompt)
        return introduction.strip()

    def generate_chapter_summary(
        self,
        chapter: Chapter,
        programming_language: str = "Python"
    ) -> str:
        """Generate a summary for a chapter"""
        
        system_prompt = (
            "You are an expert technical writer. Write concise chapter summaries "
            "that reinforce key learning points."
        )

        sections_list = "\n".join([f"- {s.title}" for s in chapter.sections])

        prompt = f"""
Write a summary for the following chapter in a {programming_language} programming book:

Chapter {chapter.number}: {chapter.title}
Introduction: {chapter.introduction}

Sections covered:
{sections_list}

The summary should:
1. Recap the key concepts covered
2. Highlight the most important takeaways
3. Suggest how to apply what was learned
4. Length: 100-150 words

Write the summary now:
"""

        summary = self.llm_client.generate_text(prompt, system_prompt)
        return summary.strip()

    def generate_complete_chapter(
        self,
        chapter: Chapter,
        programming_language: str = "Python",
        target_audience: str = "intermediate developers",
        include_code_examples: bool = True
    ) -> Chapter:
        """Generate complete content for a chapter"""
        
        # Generate introduction if not present
        if not chapter.introduction:
            chapter.introduction = self.generate_chapter_introduction(
                chapter, programming_language=programming_language
            )

        # Generate content for each section
        for section in chapter.sections:
            if not section.content:
                section = self.generate_section_content(
                    section,
                    chapter_context=chapter.introduction,
                    programming_language=programming_language,
                    target_audience=target_audience
                )

        # Generate summary
        if not chapter.summary:
            chapter.summary = self.generate_chapter_summary(
                chapter, programming_language=programming_language
            )

        return chapter
