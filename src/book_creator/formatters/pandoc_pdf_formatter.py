"""
Pandoc-based PDF formatter for generating PDFs from Markdown
"""

import os
import subprocess
import tempfile
import re
from typing import Optional
from ..models.book import Book
from .markdown_formatter import MarkdownFormatter


class PandocPDFFormatter:
    """
    Generate PDF from Markdown using Pandoc with strict syntax validation
    """
    
    def __init__(self, pandoc_path: str = "pandoc"):
        """
        Initialize Pandoc PDF formatter
        
        Args:
            pandoc_path: Path to pandoc executable (default: "pandoc" from PATH)
        """
        self.pandoc_path = pandoc_path
        self._verify_pandoc()
    
    def _verify_pandoc(self):
        """Verify that Pandoc is installed and accessible"""
        try:
            result = subprocess.run(
                [self.pandoc_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            # Extract version for logging
            version_line = result.stdout.split('\n')[0]
            print(f"Using {version_line}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(
                f"Pandoc is not installed or not found at '{self.pandoc_path}'. "
                "Please install Pandoc from https://pandoc.org/installing.html"
            ) from e
    
    def validate_markdown(self, markdown_content: str) -> tuple[bool, list[str]]:
        """
        Validate Markdown syntax according to CommonMark standard
        
        Args:
            markdown_content: Markdown content to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check for balanced code fences
        code_fence_pattern = r'^```'
        fence_matches = re.findall(code_fence_pattern, markdown_content, re.MULTILINE)
        if len(fence_matches) % 2 != 0:
            errors.append("Unbalanced code fences: odd number of ``` delimiters found")
        
        # Check for proper heading syntax (must have space after #)
        lines = markdown_content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check headings
            if line.startswith('#'):
                if not re.match(r'^#{1,6}\s+\S', line):
                    if not re.match(r'^#{1,6}$', line):  # Empty heading is also invalid
                        errors.append(f"Line {i}: Invalid heading syntax - missing space after #")
            
            # Check for common Markdown syntax errors
            # Lists should have space after marker (only check lines starting with list marker)
            stripped_line = line.lstrip()
            if stripped_line and stripped_line[0] in ['*', '-', '+']:
                # Check if it's actually a list (not bold/italic or horizontal rule)
                if len(stripped_line) > 1 and stripped_line[1] not in [' ', '*', '-', '+']:
                    errors.append(f"Line {i}: List marker should be followed by a space")
            
        
        # Check for proper link syntax
        for match in re.finditer(r'\[[^\]]*\](?!\()', markdown_content):
            # Found a bracket without matching parenthesis
            context = markdown_content[max(0, match.start()-20):match.end()+20]
            if not re.match(r'\[[^\]]+\]:', context):  # Not a reference-style link definition
                errors.append(f"Potential broken link syntax near: {context[:40]}...")
        
        # Validate code block language specifiers
        code_blocks = re.finditer(r'^```(\w*)\n', markdown_content, re.MULTILINE)
        for match in code_blocks:
            lang = match.group(1)
            if lang:  # If language is specified, check it's valid
                # Common valid languages
                valid_langs = {
                    'python', 'javascript', 'java', 'c', 'cpp', 'csharp', 'ruby', 
                    'go', 'rust', 'typescript', 'php', 'swift', 'kotlin', 'bash',
                    'shell', 'sql', 'html', 'css', 'json', 'xml', 'yaml', 'markdown'
                }
                if lang.lower() not in valid_langs:
                    # Warning, not error - Pandoc supports many languages
                    pass
        
        return (len(errors) == 0, errors)
    
    def format(self, book: Book, output_path: str, 
               strict_validation: bool = True,
               syntax_highlighting: bool = True,
               theme: str = "tango"):
        """
        Format book as PDF using Pandoc
        
        Args:
            book: Book object to format
            output_path: Path for output PDF file
            strict_validation: If True, fail on Markdown syntax errors
            syntax_highlighting: Enable syntax highlighting for code blocks
            theme: Syntax highlighting theme (tango, pygments, kate, monochrome, etc.)
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Generate Markdown content
        md_formatter = MarkdownFormatter()
        
        # Create temporary file for Markdown
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
            tmp_md_path = tmp_md.name
            markdown_content = md_formatter._generate_markdown(book)
            
            # Validate Markdown syntax
            is_valid, errors = self.validate_markdown(markdown_content)
            
            if not is_valid:
                error_msg = "Markdown validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
                if strict_validation:
                    # Clean up temp file
                    try:
                        os.unlink(tmp_md_path)
                    except FileNotFoundError:
                        # It's safe to ignore if the temp file was already deleted
                        pass
                    raise ValueError(error_msg)
                else:
                    print(f"Warning: {error_msg}")
            
            tmp_md.write(markdown_content)
        
        try:
            # Build Pandoc command
            pandoc_args = [
                self.pandoc_path,
                tmp_md_path,
                '-o', output_path,
                '--from', 'markdown',
                '--to', 'pdf',
                '--pdf-engine=xelatex',  # Better Unicode support
                '--toc',  # Table of contents
                '--toc-depth=3',
                '--number-sections',
                '-V', 'geometry:margin=1in',
                '-V', 'fontsize=11pt',
                '-V', 'documentclass=report',
            ]
            
            # Add syntax highlighting
            if syntax_highlighting:
                pandoc_args.extend(['--highlight-style', theme])
            else:
                pandoc_args.append('--no-highlight')
            
            # Execute Pandoc
            result = subprocess.run(
                pandoc_args,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                error_msg = f"Pandoc PDF generation failed:\n{result.stderr}"
                raise RuntimeError(error_msg)
            
            print(f"PDF generated successfully: {output_path}")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_md_path)
            except FileNotFoundError:
                # It's safe to ignore if the temp file was already deleted
                pass
    
    def format_with_custom_template(self, book: Book, output_path: str,
                                   template_path: Optional[str] = None,
                                   metadata: Optional[dict] = None):
        """
        Format book as PDF with custom Pandoc template
        
        Args:
            book: Book object to format
            output_path: Path for output PDF file
            template_path: Path to custom Pandoc template file
            metadata: Additional metadata to pass to Pandoc
        """
        md_formatter = MarkdownFormatter()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
            tmp_md_path = tmp_md.name
            markdown_content = md_formatter._generate_markdown(book)
            
            # Validate
            is_valid, errors = self.validate_markdown(markdown_content)
            if not is_valid:
                os.unlink(tmp_md_path)
                raise ValueError("Markdown validation failed:\n" + "\n".join(errors))
            
            tmp_md.write(markdown_content)
        
        try:
            pandoc_args = [
                self.pandoc_path,
                tmp_md_path,
                '-o', output_path,
                '--pdf-engine=xelatex',
                '--highlight-style', 'tango',
            ]
            
            if template_path:
                pandoc_args.extend(['--template', template_path])
            
            if metadata:
                for key, value in metadata.items():
                    pandoc_args.extend(['-M', f'{key}={value}'])
            
            result = subprocess.run(pandoc_args, capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                raise RuntimeError(f"Pandoc failed: {result.stderr}")
                
        finally:
            try:
                os.unlink(tmp_md_path)
            except FileNotFoundError:
                # Ignore errors if the temp file was already deleted
                pass
    
    def get_supported_themes(self) -> list[str]:
        """Get list of supported syntax highlighting themes"""
        return [
            'pygments', 'tango', 'espresso', 'zenburn', 'kate', 
            'monochrome', 'breezedark', 'haddock'
        ]
