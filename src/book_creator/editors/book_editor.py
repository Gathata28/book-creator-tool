"""
Book editor for automating editing tasks on existing books
"""

from typing import List, Dict, Any, Optional
from ..models.book import Book
from ..utils.llm_client import LLMClient, LLMConfig


class BookEditor:
    """Automated editing tools for existing books"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient(LLMConfig())

    def reorganize_chapters(self, book: Book, new_order: List[int]) -> Book:
        """
        Reorganize chapters in a different order
        
        Args:
            book: The book to reorganize
            new_order: List of chapter numbers in desired order
        
        Returns:
            Book with reorganized chapters
        """
        reordered_chapters = []
        for i, chapter_num in enumerate(new_order, 1):
            chapter = book.get_chapter(chapter_num)
            if chapter:
                chapter.number = i
                reordered_chapters.append(chapter)
        
        book.chapters = reordered_chapters
        return book

    def check_content_consistency(self, book: Book) -> Dict[str, List[str]]:
        """
        Check for content consistency issues across the book
        
        Returns:
            Dictionary with consistency issues found
        """
        issues = {
            "terminology": [],
            "formatting": [],
            "references": [],
            "code_style": []
        }

        # Collect all terms used
        all_terms = set()
        term_variants = {}
        
        for chapter in book.chapters:
            # Check chapter content
            if chapter.introduction:
                self._extract_terms(chapter.introduction, all_terms, term_variants)
            
            for section in chapter.sections:
                if section.content:
                    self._extract_terms(section.content, all_terms, term_variants)
        
        # Check for term inconsistencies
        for term, variants in term_variants.items():
            if len(variants) > 1:
                issues["terminology"].append(
                    f"Inconsistent usage: {', '.join(variants)}"
                )
        
        return issues

    def _extract_terms(self, text: str, all_terms: set, term_variants: dict):
        """Extract and track technical terms"""
        # Simple term extraction (can be enhanced with NLP)
        words = text.split()
        for word in words:
            clean_word = word.strip('.,!?;:').lower()
            if len(clean_word) > 3 and clean_word.isalpha():
                all_terms.add(clean_word)

    def generate_index(self, book: Book) -> List[Dict[str, Any]]:
        """
        Generate an index of important terms and their locations
        
        Returns:
            List of index entries with term and locations
        """
        index = {}
        
        for chapter in book.chapters:
            chapter_id = f"Chapter {chapter.number}"
            
            # Process chapter content
            if chapter.introduction:
                self._add_to_index(chapter.introduction, chapter_id, index)
            
            for section in chapter.sections:
                section_id = f"{chapter_id}, {section.title}"
                if section.content:
                    self._add_to_index(section.content, section_id, index)
        
        # Convert to sorted list
        index_list = [
            {"term": term, "locations": locations}
            for term, locations in sorted(index.items())
        ]
        
        return index_list

    def _add_to_index(self, text: str, location: str, index: dict):
        """Add terms from text to index"""
        # Extract capitalized terms (likely important)
        words = text.split()
        for word in words:
            clean_word = word.strip('.,!?;:')
            if clean_word and clean_word[0].isupper() and len(clean_word) > 3:
                if clean_word not in index:
                    index[clean_word] = []
                if location not in index[clean_word]:
                    index[clean_word].append(location)

    def generate_glossary(self, book: Book) -> Dict[str, str]:
        """
        Generate a glossary of technical terms using AI
        
        Returns:
            Dictionary mapping terms to definitions
        """
        # Collect all technical terms
        terms = set()
        
        for chapter in book.chapters:
            for section in chapter.sections:
                if section.content:
                    # Extract code-related terms
                    words = section.content.split()
                    for word in words:
                        clean_word = word.strip('.,!?;:')
                        if clean_word and len(clean_word) > 3:
                            # Check if likely technical term
                            if any(char.isupper() for char in clean_word[1:]) or '_' in clean_word:
                                terms.add(clean_word)
        
        # Generate definitions using LLM
        glossary = {}
        system_prompt = (
            "You are a technical writer creating a glossary for a programming book. "
            "Provide concise, clear definitions for technical terms."
        )
        
        for term in sorted(terms)[:50]:  # Limit to avoid too many API calls
            prompt = f"Define the technical term '{term}' in 1-2 sentences for a programming book glossary."
            definition = self.llm_client.generate_text(prompt, system_prompt)
            if definition:
                glossary[term] = definition.strip()
        
        return glossary

    def validate_cross_references(self, book: Book) -> List[str]:
        """
        Validate cross-references within the book
        
        Returns:
            List of broken or invalid references
        """
        broken_refs = []
        
        # Build map of all sections and chapters
        valid_refs = set()
        for chapter in book.chapters:
            valid_refs.add(f"Chapter {chapter.number}")
            valid_refs.add(chapter.title)
            for section in chapter.sections:
                valid_refs.add(section.title)
        
        # Check references in content
        for chapter in book.chapters:
            for section in chapter.sections:
                if section.content:
                    # Look for reference patterns like "see Chapter X" or "as discussed in..."
                    if "Chapter" in section.content:
                        # Simple check for chapter references
                        words = section.content.split()
                        for i, word in enumerate(words):
                            if word == "Chapter" and i + 1 < len(words):
                                try:
                                    ref_num = int(words[i + 1].strip('.,;:'))
                                    ref = f"Chapter {ref_num}"
                                    if ref not in valid_refs:
                                        broken_refs.append(
                                            f"Broken reference: '{ref}' in {chapter.title}/{section.title}"
                                        )
                                except ValueError:
                                    # Not a valid chapter number after "Chapter"; skip this word
                                    pass
        
        return broken_refs

    def batch_update_code_style(self, book: Book, style_guide: str = "PEP 8") -> Book:
        """
        Update all code examples to follow a specific style guide
        
        Args:
            book: The book to update
            style_guide: Style guide to follow (e.g., "PEP 8", "Google", "Airbnb")
        
        Returns:
            Book with updated code examples
        """
        system_prompt = (
            f"You are a code formatting expert. Reformat code to strictly follow {style_guide} "
            "style guide. Return only the formatted code, no explanations."
        )
        
        for chapter in book.chapters:
            for section in chapter.sections:
                for example in section.code_examples:
                    if example.get('code'):
                        prompt = f"Reformat this {example.get('language', 'python')} code to follow {style_guide}:\n\n{example['code']}"
                        formatted_code = self.llm_client.generate_text(prompt, system_prompt)
                        
                        if formatted_code:
                            # Clean code formatting
                            cleaned_code = formatted_code.strip()
                            if cleaned_code.startswith('```'):
                                lines = cleaned_code.split('\n')
                                cleaned_code = '\n'.join(lines[1:-1] if lines[-1].startswith('```') else lines[1:])
                            example['code'] = cleaned_code
        
        return book

    def standardize_terminology(self, book: Book, terminology_map: Dict[str, str]) -> Book:
        """
        Replace inconsistent terminology throughout the book
        
        Args:
            book: The book to update
            terminology_map: Dictionary mapping old terms to new standard terms
        
        Returns:
            Book with standardized terminology
        """
        for old_term, new_term in terminology_map.items():
            for chapter in book.chapters:
                # Update chapter content
                if chapter.introduction:
                    chapter.introduction = chapter.introduction.replace(old_term, new_term)
                if chapter.summary:
                    chapter.summary = chapter.summary.replace(old_term, new_term)
                
                # Update sections
                for section in chapter.sections:
                    if section.content:
                        section.content = section.content.replace(old_term, new_term)
        
        return book

    def add_learning_objectives(self, book: Book) -> Book:
        """
        Add learning objectives to each chapter using AI
        
        Returns:
            Book with learning objectives added to chapter metadata
        """
        system_prompt = (
            "You are an educational content expert. Generate 3-5 clear, measurable "
            "learning objectives for a book chapter. Start each with an action verb "
            "like 'Understand', 'Implement', 'Explain', or 'Apply'."
        )
        
        for chapter in book.chapters:
            prompt = f"""
Generate learning objectives for this chapter:

Title: {chapter.title}
Introduction: {chapter.introduction[:200]}...

Sections:
{chr(10).join([f"- {s.title}" for s in chapter.sections[:5]])}

Provide 3-5 learning objectives.
"""
            objectives_text = self.llm_client.generate_text(prompt, system_prompt)
            
            if objectives_text:
                # Parse objectives
                objectives = []
                for line in objectives_text.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        objective = line.lstrip('0123456789.-) ').strip()
                        if objective:
                            objectives.append(objective)
                
                chapter.metadata['learning_objectives'] = objectives
        
        return book

    def enhance_code_comments(self, book: Book) -> Book:
        """
        Enhance code examples with better comments using AI
        
        Returns:
            Book with improved code comments
        """
        system_prompt = (
            "You are a programming instructor. Add clear, helpful comments to code "
            "that explain what each section does. Keep comments concise and focused "
            "on the 'why' not just the 'what'. Return only the code with comments."
        )
        
        for chapter in book.chapters:
            for section in chapter.sections:
                for example in section.code_examples:
                    if example.get('code') and len(example['code'].split('\n')) > 5:
                        language = example.get('language', 'python')
                        prompt = f"Add helpful comments to this {language} code:\n\n{example['code']}"
                        
                        commented_code = self.llm_client.generate_text(prompt, system_prompt)
                        
                        if commented_code:
                            # Clean and update
                            cleaned_code = commented_code.strip()
                            if cleaned_code.startswith('```'):
                                lines = cleaned_code.split('\n')
                                cleaned_code = '\n'.join(lines[1:-1] if lines[-1].startswith('```') else lines[1:])
                            example['code'] = cleaned_code
        
        return book
