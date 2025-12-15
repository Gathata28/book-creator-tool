"""
Agents module for Agentic-First Mode.

This module contains specialized agents for autonomous book generation:
- PlannerAgent: Interprets prompts, designs book structure
- AuthorAgent: Writes chapters based on blueprint
- EditorAgent: Reviews and quality controls content
- FormatterAgent: Formats and exports the book
"""

from .planner import PlannerAgent
from .author import AuthorAgent
from .editor import EditorAgent
from .formatter import FormatterAgent

__all__ = [
    "PlannerAgent",
    "AuthorAgent",
    "EditorAgent",
    "FormatterAgent"
]
