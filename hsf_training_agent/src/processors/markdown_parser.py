"""Markdown content processor for training materials."""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc

logger = logging.getLogger(__name__)


class MarkdownParser:
    """Parser for Markdown training content."""
    
    def __init__(self):
        """Initialize markdown parser with extensions."""
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',
                'fenced_code', 
                'tables',
                'toc',
                'attr_list',
                'def_list'
            ],
            extension_configs={
                'codehilite': {'css_class': 'highlight'},
                'toc': {'anchorlink': True}
            }
        )
    
    def extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from markdown frontmatter."""
        metadata = {}
        
        # Check for YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            
            # Simple YAML parsing for common fields
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
    
    def extract_headers(self, content: str) -> List[Dict[str, str]]:
        """Extract all headers from markdown content."""
        headers = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # ATX-style headers (# ## ###)
            atx_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if atx_match:
                level = len(atx_match.group(1))
                text = atx_match.group(2).strip()
                headers.append({
                    'level': level,
                    'text': text,
                    'line': i + 1
                })
        
        return headers
    
    def extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks with language and content."""
        code_blocks = []
        
        # Fenced code blocks
        fenced_pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(fenced_pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            code_blocks.append({
                'language': language,
                'code': code,
                'line': line_num,
                'type': 'fenced'
            })
        
        # Indented code blocks
        lines = content.split('\n')
        in_code_block = False
        current_block = []
        block_start = 0
        
        for i, line in enumerate(lines):
            if line.startswith('    ') or line.startswith('\t'):
                if not in_code_block:
                    in_code_block = True
                    block_start = i + 1
                current_block.append(line[4:] if line.startswith('    ') else line[1:])
            else:
                if in_code_block and current_block:
                    code_blocks.append({
                        'language': 'text',
                        'code': '\n'.join(current_block),
                        'line': block_start,
                        'type': 'indented'
                    })
                    current_block = []
                in_code_block = False
        
        # Handle final code block
        if in_code_block and current_block:
            code_blocks.append({
                'language': 'text',
                'code': '\n'.join(current_block),
                'line': block_start,
                'type': 'indented'
            })
        
        return code_blocks
    
    def extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract all links from markdown content."""
        links = []
        
        # Markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            links.append({
                'text': text,
                'url': url,
                'line': line_num,
                'type': 'markdown'
            })
        
        # Reference links [text][ref]
        ref_pattern = r'\[([^\]]+)\]\[([^\]]+)\]'
        for match in re.finditer(ref_pattern, content):
            text = match.group(1)
            ref = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            links.append({
                'text': text,
                'url': f'[ref:{ref}]',  # Mark as reference
                'line': line_num,
                'type': 'reference'
            })
        
        # Plain URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+[^\s<>"{}|\\^`[\].,;:!?]'
        for match in re.finditer(url_pattern, content):
            url = match.group(0)
            line_num = content[:match.start()].count('\n') + 1
            
            links.append({
                'text': url,
                'url': url,
                'line': line_num,
                'type': 'plain'
            })
        
        return links
    
    def extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract content sections based on headers."""
        sections = []
        headers = self.extract_headers(content)
        lines = content.split('\n')
        
        for i, header in enumerate(headers):
            start_line = header['line'] - 1  # Convert to 0-based
            
            # Find end of section (next header of same or higher level)
            end_line = len(lines)
            for j in range(i + 1, len(headers)):
                if headers[j]['level'] <= header['level']:
                    end_line = headers[j]['line'] - 1
                    break
            
            section_content = '\n'.join(lines[start_line:end_line])
            
            sections.append({
                'title': header['text'],
                'level': header['level'],
                'content': section_content,
                'start_line': start_line + 1,
                'end_line': end_line
            })
        
        return sections
    
    def analyze_content_structure(self, content: str, file_path: str) -> Dict[str, any]:
        """Analyze markdown content structure comprehensively."""
        metadata = self.extract_metadata(content)
        headers = self.extract_headers(content)
        code_blocks = self.extract_code_blocks(content)
        links = self.extract_links(content)
        sections = self.extract_sections(content)
        
        # Calculate statistics
        lines = content.split('\n')
        word_count = len(content.split())
        
        analysis = {
            'file_path': file_path,
            'metadata': metadata,
            'statistics': {
                'lines': len(lines),
                'words': word_count,
                'headers': len(headers),
                'code_blocks': len(code_blocks),
                'links': len(links),
                'sections': len(sections)
            },
            'structure': {
                'headers': headers,
                'sections': sections,
                'code_blocks': code_blocks,
                'links': links
            },
            'content_type': self._determine_content_type(metadata, headers, code_blocks)
        }
        
        return analysis
    
    def _determine_content_type(self, metadata: Dict, headers: List, code_blocks: List) -> str:
        """Determine the type of training content."""
        # Check metadata first
        if 'type' in metadata:
            return metadata['type']
        
        # Analyze content characteristics
        has_code = len(code_blocks) > 0
        has_exercises = any('exercise' in h['text'].lower() or 'challenge' in h['text'].lower() 
                          for h in headers)
        has_solutions = any('solution' in h['text'].lower() or 'answer' in h['text'].lower() 
                          for h in headers)
        
        if has_exercises and has_solutions:
            return 'tutorial_with_exercises'
        elif has_exercises:
            return 'tutorial'
        elif has_code:
            return 'code_example'
        elif any('introduction' in h['text'].lower() for h in headers):
            return 'introduction'
        else:
            return 'documentation'
    
    def get_chapter_summary(self, content: str) -> str:
        """Generate a brief summary of the chapter content."""
        # Get first paragraph after title
        lines = content.split('\n')
        summary_lines = []
        found_content = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip headers
            if line.startswith('#'):
                found_content = True
                continue
                
            if found_content and not line.startswith('#'):
                summary_lines.append(line)
                if len(summary_lines) >= 3:  # First few lines
                    break
        
        return ' '.join(summary_lines)[:200] + '...' if summary_lines else 'No summary available'