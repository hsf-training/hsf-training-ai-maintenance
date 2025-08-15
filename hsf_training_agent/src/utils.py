"""Utility functions for error handling and validation."""

import logging
import functools
from typing import Any, Callable, Dict, Optional
import time

logger = logging.getLogger(__name__)


def handle_api_errors(func: Callable) -> Callable:
    """Decorator for handling API errors gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"API error in {func.__name__}: {error_type}: {str(e)}")
            
            # Return appropriate error response based on function context
            if 'analyze' in func.__name__:
                return {'error': f'{error_type}: {str(e)}', 'status': 'failed'}
            elif 'create' in func.__name__ or 'issue' in func.__name__:
                return None
            else:
                raise
    
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying functions on failure with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    logger.info(f"Retrying in {current_delay} seconds...")
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None  # Should not reach here
        
        return wrapper
    return decorator


def validate_github_url(url: str) -> bool:
    """Validate that a URL is a valid GitHub repository URL."""
    if not url:
        return False
    
    # Basic validation
    if not url.startswith(('https://github.com/', 'http://github.com/')):
        return False
    
    # Check for valid repo structure
    parts = url.replace('https://github.com/', '').replace('http://github.com/', '').split('/')
    
    if len(parts) < 2:
        return False
    
    # Remove .git if present
    if parts[1].endswith('.git'):
        parts[1] = parts[1][:-4]
    
    # Basic character validation
    if not all(part.replace('-', '').replace('_', '').replace('.', '').isalnum() for part in parts[:2]):
        return False
    
    return True


def sanitize_file_path(file_path: str) -> str:
    """Sanitize file path to prevent directory traversal."""
    import os
    
    # Remove any directory traversal attempts
    path = os.path.normpath(file_path)
    
    # Remove leading slashes and dots
    while path.startswith(('/', '../', './')):
        if path.startswith('/'):
            path = path[1:]
        elif path.startswith('../'):
            path = path[3:]
        elif path.startswith('./'):
            path = path[2:]
    
    return path


def truncate_content(content: str, max_length: int = 10000) -> str:
    """Truncate content to prevent API limits."""
    if len(content) <= max_length:
        return content
    
    truncated = content[:max_length]
    
    # Try to truncate at a sentence boundary
    last_period = truncated.rfind('.')
    if last_period > max_length * 0.8:  # If we can keep most of the content
        truncated = truncated[:last_period + 1]
    
    return truncated + "\n\n... (content truncated for analysis)"


def estimate_token_count(text: str) -> int:
    """Rough estimation of token count for API planning."""
    # Very rough estimate: ~4 characters per token for English text
    return len(text) // 4


def format_error_message(error: Exception, context: str = "") -> str:
    """Format error message for user display."""
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"Error in {context}: {error_type} - {error_msg}"
    else:
        return f"{error_type}: {error_msg}"


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        # Check if we need to wait
        if len(self.calls) >= self.calls_per_minute:
            oldest_call = min(self.calls)
            sleep_time = 60 - (now - oldest_call)
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Waiting {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
        
        # Record this call
        self.calls.append(now)


def safe_json_serialize(obj: Any) -> Any:
    """Safely serialize objects for JSON output."""
    if hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):  # custom objects
        return obj.__dict__
    elif isinstance(obj, (set, frozenset)):
        return list(obj)
    else:
        return str(obj)


def create_issue_safe_title(title: str, max_length: int = 100) -> str:
    """Create a GitHub-safe issue title."""
    # Remove or replace problematic characters
    safe_chars = []
    for char in title:
        if char.isalnum() or char in ' -_.,()[]{}':
            safe_chars.append(char)
        else:
            safe_chars.append('_')
    
    safe_title = ''.join(safe_chars)
    
    # Truncate if needed
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length-3] + '...'
    
    return safe_title.strip()


def chunk_content(content: str, chunk_size: int = 5000, overlap: int = 200) -> list[str]:
    """Split large content into overlapping chunks."""
    if len(content) <= chunk_size:
        return [content]
    
    chunks = []
    start = 0
    
    while start < len(content):
        end = start + chunk_size
        
        # Try to find a good break point (sentence or paragraph)
        if end < len(content):
            # Look for paragraph break first
            para_break = content.rfind('\n\n', start, end)
            if para_break > start + chunk_size * 0.5:
                end = para_break
            else:
                # Look for sentence break
                sent_break = content.rfind('.', start, end)
                if sent_break > start + chunk_size * 0.5:
                    end = sent_break + 1
        
        chunk = content[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = max(start + chunk_size - overlap, end)
        
        if start >= len(content):
            break
    
    return chunks