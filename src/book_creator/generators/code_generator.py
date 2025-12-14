"""
Code generator for creating code examples and explanations
"""

from typing import List, Dict, Any, Optional
from ..utils.llm_client import LLMClient, LLMConfig


class CodeGenerator:
    """Generates code examples with explanations using LLM"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())

    def generate_code_example(
        self,
        concept: str,
        language: str = "python",
        difficulty: str = "intermediate",
        context: str = ""
    ) -> Dict[str, str]:
        """Generate a code example for a given concept"""
        
        system_prompt = (
            "You are an expert programmer and technical educator. "
            "Generate clear, well-commented, and best-practice code examples."
        )

        prompt = f"""
Generate a {difficulty} level code example in {language} that demonstrates: {concept}

{f"Context: {context}" if context else ""}

Requirements:
1. Include clear, concise comments
2. Follow best practices for {language}
3. Make it educational and easy to understand
4. Include example usage if applicable

Provide ONLY the code, properly formatted.
"""

        code = self.llm_client.generate_text(prompt, system_prompt)
        
        return {
            "code": self._clean_code(code),
            "language": language.lower()
        }

    def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium"
    ) -> str:
        """Generate an explanation for a code snippet"""
        
        system_prompt = (
            "You are an expert programming instructor. "
            "Explain code clearly and pedagogically."
        )

        detail_instruction = {
            "low": "Provide a brief, high-level explanation.",
            "medium": "Provide a detailed explanation covering key concepts.",
            "high": "Provide a comprehensive explanation with line-by-line breakdown."
        }

        prompt = f"""
Explain the following {language} code:

```{language}
{code}
```

{detail_instruction.get(detail_level, detail_instruction["medium"])}

Focus on:
1. What the code does
2. Key concepts and patterns used
3. Why this approach is used
4. Any important details or gotchas
"""

        explanation = self.llm_client.generate_text(prompt, system_prompt)
        return explanation

    def generate_code_with_explanation(
        self,
        concept: str,
        language: str = "python",
        difficulty: str = "intermediate"
    ) -> Dict[str, str]:
        """Generate code example with explanation"""
        
        code_example = self.generate_code_example(concept, language, difficulty)
        explanation = self.explain_code(code_example["code"], language)
        
        return {
            "code": code_example["code"],
            "language": code_example["language"],
            "explanation": explanation
        }

    def generate_exercise(
        self,
        topic: str,
        language: str = "python",
        difficulty: str = "intermediate"
    ) -> Dict[str, Any]:
        """Generate a coding exercise"""
        
        system_prompt = (
            "You are an expert programming instructor creating engaging exercises."
        )

        prompt = f"""
Create a {difficulty} level coding exercise in {language} on the topic: {topic}

Provide:
1. Exercise Question: A clear problem statement
2. Hints: 2-3 helpful hints
3. Solution: A complete solution with comments
4. Explanation: Why this solution works

Format:
QUESTION:
[Problem statement]

HINTS:
- [Hint 1]
- [Hint 2]

SOLUTION:
```{language}
[Code solution]
```

EXPLANATION:
[Explanation]
"""

        response = self.llm_client.generate_text(prompt, system_prompt)
        return self._parse_exercise(response, language)

    def _parse_exercise(self, response: str, language: str) -> Dict[str, Any]:
        """Parse exercise response"""
        
        exercise = {
            "question": "",
            "hints": [],
            "solution": "",
            "explanation": "",
            "language": language
        }

        sections = response.split('\n\n')
        current_section = None

        for section in sections:
            section = section.strip()
            if section.startswith("QUESTION:"):
                exercise["question"] = section.replace("QUESTION:", "").strip()
            elif section.startswith("HINTS:"):
                hints_text = section.replace("HINTS:", "").strip()
                exercise["hints"] = [
                    h.lstrip("- ").strip()
                    for h in hints_text.split('\n')
                    if h.strip().startswith("-")
                ]
            elif section.startswith("SOLUTION:"):
                solution_text = section.replace("SOLUTION:", "").strip()
                exercise["solution"] = self._clean_code(solution_text)
            elif section.startswith("EXPLANATION:"):
                exercise["explanation"] = section.replace("EXPLANATION:", "").strip()

        return exercise

    def _clean_code(self, code: str) -> str:
        """Clean code by removing markdown formatting"""
        lines = code.strip().split('\n')
        
        # Remove markdown code fences
        if lines and lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].startswith('```'):
            lines = lines[:-1]
            
        return '\n'.join(lines).strip()
