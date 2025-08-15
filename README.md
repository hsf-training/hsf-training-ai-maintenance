# AI agent for maintenance of HSF Training modules

The goal of this project is to create an AI agent that can 
assist in the maintenance and updating of HSF Training modules. 

The agent will be able to ingest training modules, look at the content,
and suggest updates or improvements based on the latest developments in the field.

## Models 

The project must support multiple LLM providers. The default is Google Gemini as it is accessible for free (up to some limit).
We plan to add support for other providers like OpenAI GPT, Anthropic Claude, and others in the future.


## Features

- **Automated Content Analysis**: Uses Google Gemini AI to analyze training materials
- **GitHub Integration**: Reads repository content and creates issues/PRs for suggestions
- **Multi-Format Support**: Handles Markdown files and Jupyter notebooks
- **Structured Suggestions**: Provides categorized, prioritized update recommendations
- **CLI Interface**: Easy-to-use command-line interface with rich output

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository_url>
cd hsf-training-ai-maintenance

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file based on the example:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
```

### 3. Basic Usage

Analyze a complete repository:

```bash
python hsf_training_agent/main.py analyze https://github.com/hsf-training/hsf-training-example
```

Analyze a single file:

```bash
python hsf_training_agent/main.py analyze-file https://github.com/hsf-training/hsf-training-example path/to/file.md
```

## API Keys Setup

### Google Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` permissions
3. Add it to your `.env` file as `GITHUB_TOKEN`

## Usage Examples

### Analyze Repository with Issues

```bash
python hsf_training_agent/main.py analyze https://github.com/hsf-training/hsf-training-example
```

This will:
- Analyze all training content
- Create GitHub issues with suggestions
- Generate a summary issue

### Analyze Without Creating Issues

```bash
python hsf_training_agent/main.py analyze --no-issues --no-summary https://github.com/hsf-training/hsf-training-example
```

### Save Results to File

```bash
python hsf_training_agent/main.py analyze -o results.json https://github.com/hsf-training/hsf-training-example
```

### Single File Analysis

```bash
python hsf_training_agent/main.py analyze-file https://github.com/hsf-training/hsf-training-example _episodes/01-introduction.md
```

## Configuration Options

The agent can be configured via environment variables or `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GITHUB_TOKEN` | GitHub API token | Optional |
| `LOG_LEVEL` | Logging level | INFO |
| `MAX_FILE_SIZE_MB` | Maximum file size to process | 10 |
| `ANALYSIS_TIMEOUT_SECONDS` | Analysis timeout | 300 |

## What the Agent Analyzes

The agent focuses on identifying:

1. **Software Updates**: Outdated versions, libraries, frameworks
2. **Best Practices**: Evolved methodologies and improved practices  
3. **Recent Developments**: New developments in HEP and computational science
4. **Resource Updates**: Broken links, outdated documentation
5. **Technical Accuracy**: Outdated or incorrect technical information
6. **Example Improvements**: More current examples and case studies

## Suggestion Types

- `software_update`: Outdated software versions or tools
- `best_practice`: Improved methodologies or practices
- `recent_development`: Recent field developments
- `resource_update`: Link updates or resource changes
- `technical_accuracy`: Technical corrections
- `example_improvement`: Better examples or exercises

## Output Formats

### GitHub Issues

The agent creates structured GitHub issues with:
- Clear titles and descriptions
- Categorized suggestions with priorities
- Specific change recommendations
- Educational context preservation

### JSON Reports

When using `-o` option, results are saved as JSON with:
- Complete analysis results
- Structured suggestion data
- Repository metadata
- Processing statistics

## Development

### Project Structure

```
hsf_training_agent/
├── src/
│   ├── ai/                 # AI integration (Gemini)
│   ├── github/            # GitHub API clients
│   ├── processors/        # Content processors
│   ├── config/           # Configuration management
│   ├── analyzer.py       # Main orchestrator
│   ├── cli.py           # Command line interface
│   └── utils.py         # Utilities and error handling
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

### Adding New Processors

To add support for new file formats:

1. Create a processor in `src/processors/`
2. Implement content analysis methods
3. Register in the main analyzer

### Extending Prompts

Modify `src/ai/prompt_templates.py` to:
- Add new analysis prompts
- Customize suggestion categories
- Adjust analysis focus areas

## Troubleshooting

### Common Issues

**"No Gemini API key"**
- Ensure `GEMINI_API_KEY` is set in `.env`
- Verify the key is valid and has quota

**"GitHub API rate limit"**
- Add `GITHUB_TOKEN` for higher rate limits
- Consider using `--no-issues` for analysis-only mode

**"File not found"**
- Check repository URL format
- Verify file paths are relative to repository root

### Debug Mode

Run with debug logging:

```bash
python hsf_training_agent/main.py --log-level DEBUG analyze <repo_url>
```

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation for new features
4. Ensure error handling is comprehensive
