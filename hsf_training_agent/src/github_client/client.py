"""GitHub API client for repository content access."""

import base64
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

import requests
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile

from ..config import get_settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with optional token."""
        self.settings = get_settings()
        self.token = token or self.settings.github_token
        
        if self.token:
            self.github = Github(self.token)
        else:
            self.github = Github()  # Anonymous access for public repos
            logger.warning("No GitHub token provided. Limited to public repositories.")
    
    def parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
        """Parse GitHub repository URL to extract owner and repo name."""
        parsed = urlparse(repo_url)
        
        if parsed.netloc != "github.com":
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
        
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        
        owner, repo = path_parts[0], path_parts[1]
        
        # Remove .git suffix if present
        if repo.endswith(".git"):
            repo = repo[:-4]
        
        return owner, repo
    
    def get_repository(self, repo_url: str) -> Repository:
        """Get GitHub repository object from URL."""
        owner, repo = self.parse_repo_url(repo_url)
        
        try:
            return self.github.get_repo(f"{owner}/{repo}")
        except GithubException as e:
            logger.error(f"Failed to access repository {owner}/{repo}: {e}")
            raise
    
    def get_file_content(self, repo: Repository, file_path: str) -> Optional[str]:
        """Get content of a specific file from repository."""
        try:
            content_file = repo.get_contents(file_path)
            
            # Handle single file (not directory)
            if isinstance(content_file, ContentFile):
                if content_file.encoding == "base64":
                    decoded_content = base64.b64decode(content_file.content).decode("utf-8")
                    return decoded_content
                else:
                    return content_file.decoded_content.decode("utf-8")
            else:
                logger.warning(f"Path {file_path} is a directory, not a file")
                return None
                
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"File not found: {file_path}")
            else:
                logger.error(f"Error accessing file {file_path}: {e}")
            return None
    
    def list_repository_files(self, repo: Repository, 
                             path: str = "", 
                             recursive: bool = True) -> List[Dict[str, Any]]:
        """List all files in repository with metadata."""
        files = []
        
        try:
            contents = repo.get_contents(path)
            
            # Handle single file case
            if isinstance(contents, ContentFile):
                contents = [contents]
            
            for content in contents:
                if content.type == "file":
                    file_info = {
                        "path": content.path,
                        "name": content.name,
                        "size": content.size,
                        "sha": content.sha,
                        "download_url": content.download_url,
                        "type": "file"
                    }
                    files.append(file_info)
                
                elif content.type == "dir" and recursive:
                    # Recursively get files from subdirectories
                    subfiles = self.list_repository_files(repo, content.path, recursive=True)
                    files.extend(subfiles)
        
        except GithubException as e:
            logger.error(f"Error listing files in {path}: {e}")
        
        return files
    
    def filter_training_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter files to only include training-related content."""
        training_files = []
        
        for file_info in files:
            file_path = Path(file_info["path"])
            
            # Check if file extension is supported
            if file_path.suffix.lower() not in self.settings.supported_extensions:
                continue
            
            # Skip files matching ignore patterns
            if any(file_path.match(pattern) for pattern in self.settings.ignore_patterns):
                continue
            
            # Check file size limit
            size_mb = file_info["size"] / (1024 * 1024)
            if size_mb > self.settings.max_file_size_mb:
                logger.warning(f"Skipping large file {file_path} ({size_mb:.1f}MB)")
                continue
            
            training_files.append(file_info)
        
        return training_files
    
    def get_training_content(self, repo_url: str) -> Dict[str, str]:
        """Get all training content from repository."""
        repo = self.get_repository(repo_url)
        all_files = self.list_repository_files(repo)
        training_files = self.filter_training_files(all_files)
        
        content_map = {}
        
        for file_info in training_files:
            file_path = file_info["path"]
            content = self.get_file_content(repo, file_path)
            
            if content:
                content_map[file_path] = content
                logger.info(f"Retrieved content for: {file_path}")
            else:
                logger.warning(f"Failed to retrieve content for: {file_path}")
        
        return content_map