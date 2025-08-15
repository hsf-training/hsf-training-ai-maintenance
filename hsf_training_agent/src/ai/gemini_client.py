"""Google Gemini API client for content analysis."""

import json
import logging
from typing import Dict, List, Optional, Any
import asyncio

from google import genai
from google.genai import types

from ..config import get_settings
from .prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client with API key."""
        self.settings = get_settings()
        self.api_key = api_key or self.settings.gemini_api_key
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)
        self.prompt_templates = PromptTemplates()
        
        logger.info(f"Initialized Gemini client with model: {self.settings.gemini_model}")
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from AI, handling potential formatting issues."""
        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            lines = response_text.strip().split('\n')
            json_lines = []
            in_json_block = False
            
            for line in lines:
                if line.strip().startswith('```json') or line.strip().startswith('```{'):
                    in_json_block = True
                    continue
                elif line.strip() == '```' and in_json_block:
                    in_json_block = False
                    break
                elif in_json_block:
                    json_lines.append(line)
            
            if json_lines:
                try:
                    return json.loads('\n'.join(json_lines))
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Failed to parse JSON response: {response_text[:200]}...")
            return None
    
    def analyze_content(self, content: str, 
                       file_path: str, 
                       chapter_title: str = "") -> Optional[Dict[str, Any]]:
        """Analyze training content and generate suggestions."""
        if not chapter_title:
            chapter_title = file_path.split('/')[-1]
        
        prompt = self.prompt_templates.get_primary_analysis_prompt(
            chapter_content=content,
            chapter_title=chapter_title,
            file_path=file_path
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=self.settings.max_tokens,
                    temperature=self.settings.temperature
                )
            )
            
            if response and response.text:
                parsed_response = self._parse_json_response(response.text)
                if parsed_response:
                    logger.info(f"Successfully analyzed {file_path}")
                    return parsed_response
                else:
                    logger.error(f"Failed to parse analysis response for {file_path}")
                    return None
            else:
                logger.error(f"Empty response from Gemini for {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing content for {file_path}: {e}")
            return None
    
    def verify_suggestion(self, suggestion: Dict[str, Any]) -> str:
        """Verify technical accuracy of a suggestion."""
        prompt = self.prompt_templates.get_technical_verification_prompt(suggestion)
        
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                    temperature=0.1  # Lower temperature for verification
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return "VERIFICATION_FAILED"
                
        except Exception as e:
            logger.error(f"Error verifying suggestion: {e}")
            return "VERIFICATION_FAILED"
    
    def validate_links(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract and validate links from content."""
        prompt = self.prompt_templates.get_link_validation_prompt(content)
        
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.2
                )
            )
            
            if response and response.text:
                return self._parse_json_response(response.text)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error validating links: {e}")
            return None
    
    def assess_difficulty_impact(self, original_content: str, 
                               suggested_changes: str) -> str:
        """Assess impact of changes on content difficulty."""
        prompt = self.prompt_templates.get_difficulty_assessment_prompt(
            original_content, suggested_changes
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                    temperature=0.2
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return "ASSESSMENT_FAILED"
                
        except Exception as e:
            logger.error(f"Error assessing difficulty impact: {e}")
            return "ASSESSMENT_FAILED"
    
    def generate_summary(self, all_suggestions: Dict[str, Any]) -> Optional[str]:
        """Generate summary of all analysis results."""
        prompt = self.prompt_templates.get_summary_prompt(all_suggestions)
        
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=3072,
                    temperature=0.3
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def batch_analyze_content(self, content_map: Dict[str, str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Analyze multiple content files in batch."""
        results = {}
        
        for file_path, content in content_map.items():
            logger.info(f"Analyzing {file_path}...")
            
            try:
                analysis_result = self.analyze_content(
                    content=content,
                    file_path=file_path,
                    chapter_title=file_path.split('/')[-1]
                )
                results[file_path] = analysis_result
                
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
                results[file_path] = None
        
        logger.info(f"Completed batch analysis of {len(content_map)} files")
        return results