# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a fully implemented AI agent for maintenance and updating of HSF (High Energy Physics Software Foundation) Training modules. The system ingests training modules from various formats (Markdown, Jupyter Notebooks, etc.), analyzes content using Google Gemini AI, and automatically suggests improvements or updates based on latest field developments through GitHub issues.

## Key Capabilities (✅ Implemented)

The agent can:
- ✅ Ingest training modules from GitHub repositories (Markdown, Jupyter Notebooks)
- ✅ Analyze content using sophisticated AI prompts for educational context
- ✅ Generate categorized, prioritized suggestions for updates
- ✅ Create structured GitHub issues with detailed recommendations
- ✅ Process both full repositories and individual files
- ✅ Provide rich CLI interface with progress indicators and formatted output
- ✅ Handle rate limiting, error recovery, and configuration management

## Technology Stack

- **AI Provider**: Google Gemini 2.0-flash (primary implementation)
- **GitHub Integration**: PyGithub + direct REST API calls
- **Content Processing**: Custom parsers for Markdown and Jupyter notebooks
- **CLI Framework**: Click + Rich for beautiful terminal output
- **Configuration**: Pydantic settings with .env support

## Implementation Status

✅ **COMPLETED**: Full AI agent implementation with the following components:

### Project Structure
```
hsf_training_agent/
├── src/
│   ├── ai/                 # Google Gemini integration & prompt templates
│   ├── github/            # GitHub API client & issue creation
│   ├── processors/        # Markdown & Jupyter notebook processors
│   ├── config/           # Settings & configuration management
│   ├── analyzer.py       # Main orchestration logic
│   ├── cli.py           # Rich CLI interface
│   └── utils.py         # Error handling & utilities
├── main.py              # Entry point
├── examples/            # Usage examples
└── requirements.txt     # Dependencies
```

## Usage Commands

### Basic Analysis
```bash
# Analyze complete repository
python hsf_training_agent/main.py analyze https://github.com/hsf-training/repo-name

# Analyze single file
python hsf_training_agent/main.py analyze-file https://github.com/hsf-training/repo-name path/to/file.md

# View configuration
python hsf_training_agent/main.py config
```

### Options
- `--output/-o FILE`: Save results to JSON file
- `--no-issues`: Skip creating GitHub issues
- `--no-summary`: Skip creating summary issue
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

## Required Configuration

Create `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
```

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys** in `.env`:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Get API Keys:**
   - **Gemini API**: Visit [Google AI Studio](https://ai.google.dev/) 
   - **GitHub Token**: GitHub Settings → Developer settings → Personal access tokens

## Common Development Tasks

### Running the Agent
```bash
# Full repository analysis
python hsf_training_agent/main.py analyze https://github.com/hsf-training/repo-name

# Single file analysis
python hsf_training_agent/main.py analyze-file https://github.com/hsf-training/repo-name path/to/file.md

# Dry run mode - see what would be done without creating issues
python hsf_training_agent/main.py analyze --dry-run https://github.com/hsf-training/repo-name

# Test without creating issues
python hsf_training_agent/main.py analyze --no-issues --output results.json <repo-url>
```

### Testing & Development
```bash
# Run example usage script
python examples/example_usage.py

# Debug mode
python hsf_training_agent/main.py --log-level DEBUG analyze <repo-url>

# Check configuration
python hsf_training_agent/main.py config
```

## Architecture Notes

- **Modular Design**: Each component (AI, GitHub, processors) is independently testable
- **Error Handling**: Comprehensive error recovery with graceful degradation
- **Content Processing**: Specialized parsers extract structure and metadata from training materials
- **AI Prompts**: Carefully crafted prompts maintain educational context while suggesting updates
- **Rate Limiting**: Built-in protection against API rate limits
- **Rich Output**: Beautiful terminal output with progress indicators and formatted results

## AI Analysis Focus Areas

The agent identifies updates in these categories:
1. **Software Updates**: Outdated versions, libraries, frameworks
2. **Best Practices**: Evolved methodologies and improved practices
3. **Recent Developments**: New developments in HEP and computational science
4. **Resource Updates**: Broken links, outdated documentation
5. **Technical Accuracy**: Outdated or incorrect technical information
6. **Example Improvements**: Better examples, case studies, exercises

## File Support

- **Markdown Files** (`.md`): Full structure analysis including headers, code blocks, links
- **Jupyter Notebooks** (`.ipynb`): Code cell analysis, library detection, learning progression
- **Size Limits**: Configurable max file size (default: 10MB)
- **Filtering**: Automatic filtering of non-training content