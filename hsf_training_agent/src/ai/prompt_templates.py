"""Prompt templates for AI content analysis."""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for content analysis."""
    
    @staticmethod
    def get_primary_analysis_prompt(chapter_content: str, 
                                  chapter_title: str, 
                                  file_path: str) -> str:
        """Generate primary analysis prompt for educational content."""
        return f"""You are an expert in high-energy physics and computational science education with deep knowledge of current software tools, best practices, and recent developments in the field (2024-2025).

TASK: Analyze the following training chapter content and identify specific areas that could benefit from updates based on recent developments, while preserving the core educational value and structure.

FILE: {file_path}
CHAPTER TITLE: {chapter_title}

CONTENT:
{chapter_content}

ANALYSIS FOCUS:
1. **Software/Tool Updates**: Identify outdated software versions, libraries, frameworks, or tools that have newer stable releases
2. **Best Practices**: Highlight practices that have evolved or improved methodologies that should be adopted
3. **Recent Developments**: Note recent developments in high-energy physics, data analysis, or computational methods relevant to this content
4. **Resource Updates**: Identify broken links, outdated documentation references, or resources that have moved
5. **Technical Accuracy**: Check for technical information that may be outdated or incorrect
6. **Example Improvements**: Suggest more current or effective examples, case studies, or exercises

CONSTRAINTS:
- Do NOT suggest major structural changes to the educational flow
- Preserve the current difficulty level and learning objectives
- Focus on incremental improvements that enhance learning without disrupting the core content
- Prioritize changes that have clear educational benefits

OUTPUT FORMAT:
Provide your analysis as a JSON object with this structure:
{{
  "suggestions": [
    {{
      "title": "Brief descriptive title",
      "type": "software_update|best_practice|recent_development|resource_update|technical_accuracy|example_improvement",
      "priority": "high|medium|low",
      "description": "Clear description of what needs updating and why",
      "justification": "Explanation of benefits and relevance to current practices",
      "specific_changes": "Concrete suggestions for what to change",
      "location": "Specific section, line, or area where change applies",
      "resources": "Helpful links or references (optional)"
    }}
  ],
  "overall_assessment": "Brief summary of content quality and update needs"
}}

Be specific and actionable. Only suggest changes that genuinely improve the educational value or technical accuracy of the content."""

    @staticmethod
    def get_technical_verification_prompt(suggestion: Dict[str, Any]) -> str:
        """Generate prompt for technical verification of suggestions."""
        return f"""You are a technical expert in high-energy physics and computational science. Please verify the technical accuracy and relevance of the following suggestion:

SUGGESTION:
Title: {suggestion.get('title', 'N/A')}
Type: {suggestion.get('type', 'N/A')}
Description: {suggestion.get('description', 'N/A')}
Specific Changes: {suggestion.get('specific_changes', 'N/A')}

VERIFICATION TASKS:
1. Confirm the technical accuracy of the suggested changes
2. Validate that recommended software versions/tools are stable and widely adopted
3. Check that the suggestion aligns with current best practices in the field
4. Verify that any links or resources mentioned are valid and current

Respond with:
- "VERIFIED" if the suggestion is technically sound and beneficial
- "NEEDS_REVISION" if the suggestion has issues but the general idea is good (provide revised suggestion)
- "REJECT" if the suggestion is technically incorrect or not beneficial

Include a brief explanation of your assessment."""

    @staticmethod
    def get_link_validation_prompt(content: str) -> str:
        """Generate prompt for validating links in content."""
        return f"""Extract all URLs and web links from the following content and categorize them:

CONTENT:
{content}

Please identify:
1. All HTTP/HTTPS URLs
2. DOI links
3. GitHub/GitLab repository links
4. Documentation links
5. Academic paper references with URLs

For each link, assess:
- Current accessibility status
- Whether it's likely to be outdated based on the domain/path structure
- Alternative or updated versions if the link appears outdated

Format as JSON:
{{
  "links": [
    {{
      "url": "original_url",
      "type": "documentation|repository|paper|resource|other",
      "status": "likely_valid|potentially_outdated|definitely_outdated",
      "alternative": "suggested replacement URL (if applicable)"
    }}
  ]
}}"""

    @staticmethod
    def get_difficulty_assessment_prompt(original_content: str, 
                                       suggested_changes: str) -> str:
        """Generate prompt for assessing if changes maintain appropriate difficulty level."""
        return f"""You are an educational expert specializing in computational science training. Assess whether the suggested changes maintain the appropriate difficulty level for the target audience.

ORIGINAL CONTENT EXCERPT:
{original_content[:1000]}...

SUGGESTED CHANGES:
{suggested_changes}

ASSESSMENT CRITERIA:
1. Does the change maintain the same learning curve progression?
2. Are new concepts introduced appropriately with adequate explanation?
3. Will the change make the content significantly harder or easier?
4. Are prerequisites still appropriate for the target audience?

Respond with:
- "MAINTAINS_LEVEL" if difficulty is preserved
- "INCREASES_DIFFICULTY" if the change makes content harder (explain why)
- "DECREASES_DIFFICULTY" if the change makes content easier (explain why)
- "UNCLEAR" if the impact on difficulty cannot be determined

Include specific recommendations for maintaining appropriate difficulty if needed."""

    @staticmethod
    def get_summary_prompt(all_suggestions: Dict[str, Any]) -> str:
        """Generate prompt for creating analysis summary."""
        return f"""Create a comprehensive summary of the content analysis results for an HSF training repository.

ANALYSIS RESULTS:
{all_suggestions}

SUMMARY REQUIREMENTS:
1. Overall assessment of the repository's current state
2. Most critical updates needed (top 5 priorities)
3. Categorization of suggestions by type and urgency
4. Estimated effort level for implementing suggested changes
5. Potential risks or considerations for updates
6. Recommendations for maintenance schedule

Format as a clear, structured summary that would be useful for repository maintainers to prioritize their update efforts."""