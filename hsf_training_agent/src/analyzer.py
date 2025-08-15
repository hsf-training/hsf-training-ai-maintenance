"""Main content analyzer orchestrating the workflow."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .github_client.client import GitHubClient
from .github_client.issue_creator import GitHubIssueCreator
from .ai.gemini_client import GeminiClient
from .processors.markdown_parser import MarkdownParser
from .processors.notebook_parser import NotebookParser
from .config import get_settings

logger = logging.getLogger(__name__)


class HSFTrainingAnalyzer:
    """Main analyzer for HSF training content."""
    
    def __init__(self, 
                 github_token: Optional[str] = None,
                 gemini_api_key: Optional[str] = None):
        """Initialize the analyzer with API clients."""
        self.settings = get_settings()
        
        # Initialize clients
        self.github_client = GitHubClient(github_token)
        self.gemini_client = GeminiClient(gemini_api_key)
        
        # Initialize processors
        self.markdown_parser = MarkdownParser()
        self.notebook_parser = NotebookParser()
        
        logger.info("HSF Training Analyzer initialized successfully")
    
    def analyze_repository(self, repo_url: str, 
                          create_issues: bool = True,
                          create_summary: bool = True) -> Dict[str, Any]:
        """Analyze a complete repository for training content updates."""
        logger.info(f"Starting analysis of repository: {repo_url}")
        
        try:
            # Step 1: Get repository and content
            repo = self.github_client.get_repository(repo_url)
            content_map = self.github_client.get_training_content(repo_url)
            
            if not content_map:
                logger.warning("No training content found in repository")
                return {'error': 'No training content found'}
            
            logger.info(f"Found {len(content_map)} training files")
            
            # Step 2: Analyze content structure
            processed_content = self._process_all_content(content_map)
            
            # Step 3: Generate AI analysis
            analysis_results = self._analyze_with_ai(processed_content)
            
            # Step 4: Create GitHub issues if requested
            issue_numbers = {}
            if create_issues:
                issue_numbers = self._create_github_issues(repo, analysis_results)
            
            # Step 5: Create summary issue if requested
            summary_issue = None
            if create_summary:
                summary_issue = self._create_summary_issue(repo, analysis_results, repo_url)
            
            # Step 6: Compile final results
            results = {
                'repository': repo_url,
                'analysis_date': self._get_timestamp(),
                'files_analyzed': len(content_map),
                'total_suggestions': sum(
                    len(result.get('suggestions', [])) 
                    for result in analysis_results.values() 
                    if result
                ),
                'content_structure': processed_content,
                'ai_analysis': analysis_results,
                'github_issues': issue_numbers,
                'summary_issue': summary_issue,
                'status': 'completed'
            }
            
            logger.info(f"Repository analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            return {
                'repository': repo_url,
                'status': 'failed',
                'error': str(e)
            }
    
    def analyze_single_file(self, repo_url: str, 
                           file_path: str) -> Dict[str, Any]:
        """Analyze a single file from a repository."""
        logger.info(f"Analyzing single file: {file_path} from {repo_url}")
        
        try:
            repo = self.github_client.get_repository(repo_url)
            content = self.github_client.get_file_content(repo, file_path)
            
            if not content:
                return {'error': f'Could not retrieve content for {file_path}'}
            
            # Process the content
            processed = self._process_single_content(file_path, content)
            
            # Analyze with AI
            ai_analysis = self.gemini_client.analyze_content(
                content=processed['processed_content'],
                file_path=file_path,
                chapter_title=processed['metadata'].get('title', file_path)
            )
            
            return {
                'file_path': file_path,
                'content_structure': processed,
                'ai_analysis': ai_analysis,
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Single file analysis failed: {e}")
            return {
                'file_path': file_path,
                'status': 'failed',
                'error': str(e)
            }
    
    def _process_all_content(self, content_map: Dict[str, str]) -> Dict[str, Dict]:
        """Process all content files and extract structure."""
        processed = {}
        
        for file_path, content in content_map.items():
            try:
                processed[file_path] = self._process_single_content(file_path, content)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                processed[file_path] = {
                    'error': str(e),
                    'processed_content': content  # Fallback to raw content
                }
        
        return processed
    
    def _process_single_content(self, file_path: str, content: str) -> Dict[str, Any]:
        """Process a single content file based on its type."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.ipynb':
            # Process Jupyter notebook
            structure = self.notebook_parser.analyze_notebook_structure(content, file_path)
            
            # Extract markdown content for AI analysis
            notebook = self.notebook_parser.load_notebook(content)
            if notebook:
                processed_content = self.notebook_parser.extract_markdown_content(notebook)
                # Add code cell information as comments
                code_blocks = self.notebook_parser.extract_code_blocks(notebook)
                if code_blocks:
                    processed_content += "\n\n<!-- Code Analysis -->\n"
                    for i, block in enumerate(code_blocks):
                        processed_content += f"\n<!-- Code Cell {block['cell_index']}: "
                        processed_content += f"Lines: {block['lines']}, "
                        processed_content += f"Imports: {', '.join(block['imports'][:3])} -->\n"
            else:
                processed_content = content
                
        elif file_ext in ['.md', '.rst']:
            # Process Markdown/RST
            structure = self.markdown_parser.analyze_content_structure(content, file_path)
            processed_content = content
            
        else:
            # Process as plain text
            structure = {
                'file_path': file_path,
                'content_type': 'text',
                'statistics': {
                    'lines': len(content.split('\n')),
                    'words': len(content.split())
                }
            }
            processed_content = content
        
        return {
            'structure': structure,
            'processed_content': processed_content,
            'metadata': structure.get('metadata', {}),
            'content_type': structure.get('content_type', 'unknown')
        }
    
    def _analyze_with_ai(self, processed_content: Dict[str, Dict]) -> Dict[str, Optional[Dict]]:
        """Analyze processed content with AI."""
        analysis_results = {}
        
        for file_path, content_data in processed_content.items():
            if 'error' in content_data:
                logger.warning(f"Skipping analysis for {file_path} due to processing error")
                analysis_results[file_path] = None
                continue
            
            try:
                processed_text = content_data['processed_content']
                title = content_data['metadata'].get('title', file_path)
                
                # Skip if content is too short
                if len(processed_text.strip()) < 100:
                    logger.info(f"Skipping {file_path} - content too short")
                    analysis_results[file_path] = None
                    continue
                
                result = self.gemini_client.analyze_content(
                    content=processed_text,
                    file_path=file_path,
                    chapter_title=title
                )
                
                analysis_results[file_path] = result
                
            except Exception as e:
                logger.error(f"AI analysis failed for {file_path}: {e}")
                analysis_results[file_path] = None
        
        return analysis_results
    
    def _create_github_issues(self, repo, analysis_results: Dict) -> Dict[str, int]:
        """Create GitHub issues for analysis results."""
        issue_creator = GitHubIssueCreator(repo)
        issue_numbers = {}
        
        for file_path, analysis in analysis_results.items():
            if not analysis or 'suggestions' not in analysis:
                continue
            
            suggestions = analysis['suggestions']
            if not suggestions:
                continue
            
            try:
                # Check for existing issues
                existing = issue_creator.check_existing_issues(file_path)
                if existing:
                    logger.info(f"Existing issues found for {file_path}: {existing}")
                    issue_numbers[file_path] = existing[0]  # Use first existing issue
                    continue
                
                # Create new issue
                issue_number = issue_creator.create_suggestion_issue(
                    suggestions=suggestions,
                    file_path=file_path
                )
                
                if issue_number:
                    issue_numbers[file_path] = issue_number
                    logger.info(f"Created issue #{issue_number} for {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to create issue for {file_path}: {e}")
        
        return issue_numbers
    
    def _create_summary_issue(self, repo, analysis_results: Dict, repo_url: str) -> Optional[int]:
        """Create a summary issue with overall analysis results."""
        issue_creator = GitHubIssueCreator(repo)
        
        # Filter results with suggestions
        results_with_suggestions = {
            path: analysis for path, analysis in analysis_results.items()
            if analysis and analysis.get('suggestions')
        }
        
        if not results_with_suggestions:
            logger.info("No suggestions found, skipping summary issue")
            return None
        
        try:
            return issue_creator.create_batch_summary_issue(
                analysis_results=results_with_suggestions,
                repo_url=repo_url
            )
        except Exception as e:
            logger.error(f"Failed to create summary issue: {e}")
            return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_analysis_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from analysis results."""
        if analysis_results.get('status') != 'completed':
            return {'error': 'Analysis not completed'}
        
        ai_results = analysis_results.get('ai_analysis', {})
        
        # Count suggestions by type
        suggestion_types = {}
        all_suggestions = []
        
        for file_path, analysis in ai_results.items():
            if analysis and 'suggestions' in analysis:
                suggestions = analysis['suggestions']
                all_suggestions.extend(suggestions)
                
                for suggestion in suggestions:
                    suggestion_type = suggestion.get('type', 'unknown')
                    suggestion_types[suggestion_type] = suggestion_types.get(suggestion_type, 0) + 1
        
        # Priority distribution
        priority_counts = {}
        for suggestion in all_suggestions:
            priority = suggestion.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            'total_files': analysis_results.get('files_analyzed', 0),
            'total_suggestions': len(all_suggestions),
            'suggestion_types': suggestion_types,
            'priority_distribution': priority_counts,
            'files_with_suggestions': len([r for r in ai_results.values() if r and r.get('suggestions')]),
            'github_issues_created': len(analysis_results.get('github_issues', {})),
            'analysis_date': analysis_results.get('analysis_date')
        }