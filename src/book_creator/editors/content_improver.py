"""
Content improver for enhancing book content
"""

from typing import Optional, Dict, Any
from ..models.book import Section, Chapter
from ..utils.llm_client import LLMClient, LLMConfig


class ContentImprover:
    """AI-powered content improvement tool"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())

    def improve_section(
        self,
        section: Section,
        focus: str = "clarity"
    ) -> Section:
        """Improve a section's content"""
        
        if not section.content:
            return section

        improved_content = self.improve_text(section.content, focus)
        section.content = improved_content
        
        return section

    def improve_text(
        self,
        text: str,
        focus: str = "clarity"
    ) -> str:
        """Improve text based on specific focus area"""
        
        focus_prompts = {
            "clarity": "Make the text clearer and easier to understand without losing technical accuracy.",
            "engagement": "Make the text more engaging and interesting while maintaining professionalism.",
            "conciseness": "Make the text more concise while preserving all important information.",
            "detail": "Add more detail and depth to the explanations.",
            "examples": "Add or improve examples to illustrate concepts better.",
        }

        system_prompt = (
            "You are an expert technical writer and editor. Improve technical content "
            "while maintaining accuracy and the author's voice."
        )

        prompt = f"""
Improve the following text with focus on: {focus}

Instruction: {focus_prompts.get(focus, focus_prompts["clarity"])}

Text:
{text}

Return ONLY the improved text.
"""

        improved = self.llm_client.generate_text(prompt, system_prompt)
        return improved.strip()

    def add_transitions(self, text: str) -> str:
        """Add smooth transitions between paragraphs"""
        
        system_prompt = (
            "You are an expert technical writer. Add smooth transitions between "
            "paragraphs to improve flow."
        )

        prompt = f"""
Improve the flow of this text by adding appropriate transitions between paragraphs:

{text}

Return the improved text with better transitions.
"""

        improved = self.llm_client.generate_text(prompt, system_prompt)
        return improved.strip()

    def enhance_with_examples(
        self,
        text: str,
        programming_language: str = "Python"
    ) -> str:
        """Add relevant examples to text"""
        
        system_prompt = (
            f"You are an expert {programming_language} developer and technical writer. "
            "Enhance explanations with relevant examples."
        )

        prompt = f"""
Enhance the following text by adding relevant, concrete examples where appropriate:

{text}

Guidelines:
1. Add examples that clarify concepts
2. Keep examples concise and relevant
3. Use {programming_language} for code examples if needed
4. Integrate examples naturally into the text

Return the enhanced text.
"""

        enhanced = self.llm_client.generate_text(prompt, system_prompt)
        return enhanced.strip()

    def suggest_improvements(
        self,
        text: str,
        aspect: str = "overall"
    ) -> Dict[str, Any]:
        """Get suggestions for improving text"""
        
        system_prompt = (
            "You are an expert technical editor. Provide constructive feedback "
            "and specific suggestions for improvement."
        )

        prompt = f"""
Analyze the following text and provide improvement suggestions:

Text:
{text}

Focus on: {aspect}

Provide:
STRENGTHS:
- [What works well]

AREAS_FOR_IMPROVEMENT:
- [Specific suggestion 1]
- [Specific suggestion 2]

PRIORITY_CHANGES:
- [Most important change to make]
"""

        response = self.llm_client.generate_text(prompt, system_prompt)
        return self._parse_suggestions(response)

    def _parse_suggestions(self, response: str) -> Dict[str, Any]:
        """Parse improvement suggestions"""
        
        result = {
            "strengths": [],
            "improvements": [],
            "priorities": []
        }

        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith("STRENGTHS:"):
                current_section = "strengths"
            elif line.startswith("AREAS_FOR_IMPROVEMENT:"):
                current_section = "improvements"
            elif line.startswith("PRIORITY_CHANGES:"):
                current_section = "priorities"
            elif line.startswith("-") and current_section:
                item = line.lstrip("- ").strip()
                if item:
                    result[current_section].append(item)

        return result
