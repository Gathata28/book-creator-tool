"""
Grammar and style checker using LLM
"""

from typing import List, Dict, Any, Optional
from ..utils.llm_client import LLMClient, LLMConfig


class GrammarChecker:
    """AI-powered grammar and style checker"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """Check grammar and style in text"""
        
        system_prompt = (
            "You are an expert editor and grammarian. Identify grammar, spelling, "
            "and style issues in technical writing. Be precise and helpful."
        )

        prompt = f"""
Review the following text for grammar, spelling, and style issues:

{text}

Provide:
1. A list of issues found (if any)
2. Suggestions for improvement
3. An overall quality score (1-10)

Format:
ISSUES:
- [Issue 1]: [Description and location]
- [Issue 2]: [Description and location]

SUGGESTIONS:
- [Suggestion 1]
- [Suggestion 2]

SCORE: [1-10]

If no issues found, state "No issues found."
"""

        response = self.llm_client.generate_text(prompt, system_prompt)
        return self._parse_grammar_response(response)

    def fix_grammar(self, text: str) -> str:
        """Automatically fix grammar issues in text"""
        
        system_prompt = (
            "You are an expert editor. Fix grammar, spelling, and style issues "
            "while preserving the original meaning and technical accuracy."
        )

        prompt = f"""
Fix any grammar, spelling, and style issues in the following text.
Preserve technical terms and code references exactly as they are.
Return ONLY the corrected text.

Text:
{text}
"""

        corrected = self.llm_client.generate_text(prompt, system_prompt)
        return corrected.strip()

    def check_technical_accuracy(
        self,
        text: str,
        programming_language: str = "Python"
    ) -> Dict[str, Any]:
        """Check technical accuracy of content"""
        
        system_prompt = (
            f"You are an expert {programming_language} developer and technical reviewer. "
            "Identify technical inaccuracies and outdated information."
        )

        prompt = f"""
Review the following technical content for accuracy:

{text}

Check for:
1. Technical inaccuracies
2. Outdated information or practices
3. Misleading statements
4. Missing important caveats or warnings

Provide:
TECHNICAL_ISSUES:
- [Issue 1]
- [Issue 2]

ACCURACY_SCORE: [1-10]
"""

        response = self.llm_client.generate_text(prompt, system_prompt)
        return self._parse_technical_response(response)

    def improve_readability(self, text: str) -> str:
        """Improve text readability while maintaining technical accuracy"""
        
        system_prompt = (
            "You are an expert technical writer. Improve readability of technical "
            "content while maintaining accuracy and precision."
        )

        prompt = f"""
Improve the readability of the following technical text:

{text}

Guidelines:
1. Use clear, concise language
2. Break up long sentences
3. Add transitional phrases where helpful
4. Maintain all technical accuracy
5. Keep the same overall length

Return ONLY the improved text.
"""

        improved = self.llm_client.generate_text(prompt, system_prompt)
        return improved.strip()

    def _parse_grammar_response(self, response: str) -> Dict[str, Any]:
        """Parse grammar check response"""
        
        result = {
            "issues": [],
            "suggestions": [],
            "score": 0
        }

        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith("ISSUES:"):
                current_section = "issues"
            elif line.startswith("SUGGESTIONS:"):
                current_section = "suggestions"
            elif line.startswith("SCORE:"):
                try:
                    score_str = line.replace("SCORE:", "").strip()
                    result["score"] = int(score_str.split('/')[0])
                except:
                    result["score"] = 0
            elif line.startswith("-") and current_section:
                item = line.lstrip("- ").strip()
                if item and item.lower() != "no issues found.":
                    result[current_section].append(item)

        return result

    def _parse_technical_response(self, response: str) -> Dict[str, Any]:
        """Parse technical accuracy response"""
        
        result = {
            "issues": [],
            "score": 0
        }

        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith("TECHNICAL_ISSUES:"):
                current_section = "issues"
            elif line.startswith("ACCURACY_SCORE:"):
                try:
                    score_str = line.replace("ACCURACY_SCORE:", "").strip()
                    result["score"] = int(score_str.split('/')[0])
                except:
                    result["score"] = 0
            elif line.startswith("-") and current_section == "issues":
                item = line.lstrip("- ").strip()
                if item:
                    result["issues"].append(item)

        return result
