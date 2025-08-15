"""Jupyter notebook processor for training materials."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import nbformat
from nbformat import NotebookNode

logger = logging.getLogger(__name__)


class NotebookParser:
    """Parser for Jupyter notebook training content."""
    
    def __init__(self):
        """Initialize notebook parser."""
        pass
    
    def load_notebook(self, content: str) -> Optional[NotebookNode]:
        """Load notebook from JSON string."""
        try:
            notebook_dict = json.loads(content)
            notebook = nbformat.from_dict(notebook_dict)
            return notebook
        except (json.JSONDecodeError, nbformat.ValidationError) as e:
            logger.error(f"Failed to load notebook: {e}")
            return None
    
    def extract_metadata(self, notebook: NotebookNode) -> Dict[str, Any]:
        """Extract metadata from notebook."""
        metadata = {}
        
        # Notebook-level metadata
        if hasattr(notebook, 'metadata') and notebook.metadata:
            nb_meta = notebook.metadata
            
            # Common fields
            for field in ['title', 'authors', 'description', 'keywords', 'language']:
                if field in nb_meta:
                    metadata[field] = nb_meta[field]
            
            # Kernel info
            if 'kernelspec' in nb_meta:
                kernel = nb_meta['kernelspec']
                metadata['kernel_name'] = kernel.get('name', 'unknown')
                metadata['kernel_display_name'] = kernel.get('display_name', 'unknown')
                metadata['language'] = kernel.get('language', 'unknown')
        
        return metadata
    
    def extract_cells_by_type(self, notebook: NotebookNode) -> Dict[str, List[Dict]]:
        """Extract cells grouped by type."""
        cells = {
            'markdown': [],
            'code': [],
            'raw': []
        }
        
        for i, cell in enumerate(notebook.cells):
            cell_info = {
                'index': i,
                'source': cell.get('source', ''),
                'metadata': cell.get('metadata', {})
            }
            
            if cell.cell_type == 'code':
                cell_info.update({
                    'execution_count': cell.get('execution_count'),
                    'outputs': cell.get('outputs', [])
                })
                cells['code'].append(cell_info)
                
            elif cell.cell_type == 'markdown':
                cells['markdown'].append(cell_info)
                
            elif cell.cell_type == 'raw':
                cells['raw'].append(cell_info)
        
        return cells
    
    def extract_code_blocks(self, notebook: NotebookNode) -> List[Dict[str, Any]]:
        """Extract code blocks with execution information."""
        code_blocks = []
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == 'code':
                source = cell.get('source', '')
                if source.strip():  # Only non-empty cells
                    
                    # Analyze imports and libraries
                    imports = self._extract_imports(source)
                    
                    # Check for common patterns
                    patterns = self._analyze_code_patterns(source)
                    
                    code_blocks.append({
                        'cell_index': i,
                        'source': source,
                        'execution_count': cell.get('execution_count'),
                        'has_output': bool(cell.get('outputs', [])),
                        'imports': imports,
                        'patterns': patterns,
                        'lines': len(source.split('\n'))
                    })
        
        return code_blocks
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        return imports
    
    def _analyze_code_patterns(self, code: str) -> Dict[str, bool]:
        """Analyze code for common patterns and libraries."""
        patterns = {
            'matplotlib': 'matplotlib' in code or 'plt.' in code,
            'pandas': 'pandas' in code or 'pd.' in code,
            'numpy': 'numpy' in code or 'np.' in code,
            'scipy': 'scipy' in code,
            'sklearn': 'sklearn' in code,
            'tensorflow': 'tensorflow' in code or 'tf.' in code,
            'pytorch': 'torch' in code,
            'root_analysis': 'ROOT' in code or 'uproot' in code,
            'statistical_analysis': any(term in code.lower() for term in 
                                      ['histogram', 'fit', 'chi2', 'p-value', 'distribution']),
            'file_io': any(term in code for term in 
                         ['open(', 'read(', 'write(', 'with open', 'json.', 'csv']),
            'loops': any(term in code for term in ['for ', 'while ']),
            'functions': 'def ' in code,
            'classes': 'class ' in code
        }
        
        return patterns
    
    def extract_markdown_content(self, notebook: NotebookNode) -> str:
        """Extract all markdown content as a single string."""
        markdown_parts = []
        
        for cell in notebook.cells:
            if cell.cell_type == 'markdown':
                source = cell.get('source', '').strip()
                if source:
                    markdown_parts.append(source)
                    markdown_parts.append('')  # Add spacing
        
        return '\n'.join(markdown_parts)
    
    def analyze_learning_progression(self, notebook: NotebookNode) -> Dict[str, Any]:
        """Analyze the learning progression in the notebook."""
        cells = notebook.cells
        progression = {
            'total_cells': len(cells),
            'code_to_markdown_ratio': 0,
            'has_introduction': False,
            'has_exercises': False,
            'has_conclusions': False,
            'complexity_progression': []
        }
        
        code_cells = sum(1 for cell in cells if cell.cell_type == 'code')
        markdown_cells = sum(1 for cell in cells if cell.cell_type == 'markdown')
        
        if markdown_cells > 0:
            progression['code_to_markdown_ratio'] = code_cells / markdown_cells
        
        # Analyze content for educational patterns
        all_text = self.extract_markdown_content(notebook).lower()
        
        progression['has_introduction'] = any(term in all_text for term in 
                                            ['introduction', 'overview', 'getting started'])
        progression['has_exercises'] = any(term in all_text for term in 
                                         ['exercise', 'challenge', 'try', 'practice'])
        progression['has_conclusions'] = any(term in all_text for term in 
                                           ['conclusion', 'summary', 'wrap up'])
        
        # Analyze code complexity progression
        for i, cell in enumerate(cells):
            if cell.cell_type == 'code':
                source = cell.get('source', '')
                complexity = self._estimate_code_complexity(source)
                progression['complexity_progression'].append({
                    'cell_index': i,
                    'complexity': complexity
                })
        
        return progression
    
    def _estimate_code_complexity(self, code: str) -> str:
        """Estimate code complexity level."""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        
        if len(lines) == 0:
            return 'empty'
        elif len(lines) <= 3:
            return 'simple'
        elif len(lines) <= 10:
            if any(keyword in code for keyword in ['def ', 'class ', 'for ', 'while ', 'if ']):
                return 'intermediate'
            else:
                return 'simple'
        else:
            return 'complex'
    
    def extract_outputs(self, notebook: NotebookNode) -> List[Dict[str, Any]]:
        """Extract cell outputs for analysis."""
        outputs = []
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == 'code' and cell.get('outputs'):
                for j, output in enumerate(cell.outputs):
                    output_info = {
                        'cell_index': i,
                        'output_index': j,
                        'output_type': output.get('output_type', 'unknown')
                    }
                    
                    # Handle different output types
                    if output_info['output_type'] == 'display_data':
                        output_info['has_plot'] = 'image/png' in output.get('data', {})
                        output_info['has_html'] = 'text/html' in output.get('data', {})
                    elif output_info['output_type'] == 'stream':
                        output_info['stream_name'] = output.get('name', 'unknown')
                        output_info['text_length'] = len(output.get('text', []))
                    elif output_info['output_type'] == 'execute_result':
                        output_info['has_data'] = bool(output.get('data'))
                    
                    outputs.append(output_info)
        
        return outputs
    
    def analyze_notebook_structure(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze notebook structure comprehensively."""
        notebook = self.load_notebook(content)
        if not notebook:
            return {'error': 'Failed to load notebook'}
        
        metadata = self.extract_metadata(notebook)
        cells = self.extract_cells_by_type(notebook)
        code_blocks = self.extract_code_blocks(notebook)
        learning_progression = self.analyze_learning_progression(notebook)
        outputs = self.extract_outputs(notebook)
        
        # Calculate statistics
        total_code_lines = sum(block['lines'] for block in code_blocks)
        
        # Extract unique libraries
        all_imports = []
        for block in code_blocks:
            all_imports.extend(block['imports'])
        unique_libraries = list(set(all_imports))
        
        analysis = {
            'file_path': file_path,
            'metadata': metadata,
            'statistics': {
                'total_cells': len(notebook.cells),
                'code_cells': len(cells['code']),
                'markdown_cells': len(cells['markdown']),
                'raw_cells': len(cells['raw']),
                'total_code_lines': total_code_lines,
                'unique_libraries': len(unique_libraries),
                'cells_with_output': len(outputs)
            },
            'structure': {
                'cells': cells,
                'code_blocks': code_blocks,
                'learning_progression': learning_progression,
                'outputs': outputs,
                'libraries': unique_libraries
            },
            'content_type': self._determine_notebook_type(learning_progression, code_blocks)
        }
        
        return analysis
    
    def _determine_notebook_type(self, progression: Dict, code_blocks: List) -> str:
        """Determine the type of notebook content."""
        if progression['has_exercises']:
            return 'tutorial_with_exercises'
        elif progression['has_introduction'] and progression['has_conclusions']:
            return 'complete_tutorial'
        elif len(code_blocks) > 5:
            return 'code_heavy_tutorial'
        elif progression['has_introduction']:
            return 'introduction'
        else:
            return 'notebook'
    
    def get_notebook_summary(self, notebook: NotebookNode) -> str:
        """Generate a brief summary of the notebook content."""
        markdown_content = self.extract_markdown_content(notebook)
        
        # Extract first few sentences from markdown
        sentences = markdown_content.split('.')[:3]
        summary = '. '.join(sentences).strip()
        
        if len(summary) > 200:
            summary = summary[:200] + '...'
        
        return summary if summary else 'Jupyter notebook with code and analysis'