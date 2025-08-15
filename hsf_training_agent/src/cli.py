"""Command line interface for HSF Training AI Maintenance Agent."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from .analyzer import HSFTrainingAnalyzer
from .config import get_settings, load_env_file

console = Console()


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging with rich handler."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_time=False, show_path=False)]
    )


@click.group()
@click.option('--log-level', default='INFO', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Set logging level')
@click.option('--config', type=click.Path(exists=True),
              help='Path to configuration file (.env)')
def cli(log_level: str, config: Optional[str]) -> None:
    """HSF Training AI Maintenance Agent - Analyze and maintain training repositories."""
    setup_logging(log_level)
    
    if config:
        load_env_file(Path(config))
    else:
        load_env_file()


@cli.command()
@click.argument('repo_url')
@click.option('--output', '-o', type=click.Path(), 
              help='Output file for analysis results (JSON)')
@click.option('--no-issues', is_flag=True,
              help='Skip creating GitHub issues')
@click.option('--no-summary', is_flag=True,
              help='Skip creating summary issue')
@click.option('--github-token', envvar='GITHUB_TOKEN',
              help='GitHub API token')
@click.option('--gemini-key', envvar='GEMINI_API_KEY',
              help='Google Gemini API key')
def analyze(repo_url: str,
           output: Optional[str],
           no_issues: bool,
           no_summary: bool,
           github_token: Optional[str],
           gemini_key: Optional[str]) -> None:
    """Analyze a complete HSF training repository."""
    
    console.print(Panel.fit(
        f"[bold blue]HSF Training Repository Analysis[/bold blue]\n"
        f"Repository: [green]{repo_url}[/green]",
        border_style="blue"
    ))
    
    try:
        # Initialize analyzer
        with console.status("[bold green]Initializing analyzer...", spinner="dots"):
            analyzer = HSFTrainingAnalyzer(
                github_token=github_token,
                gemini_api_key=gemini_key
            )
        
        # Run analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Analyzing repository...", total=None)
            
            results = analyzer.analyze_repository(
                repo_url=repo_url,
                create_issues=not no_issues,
                create_summary=not no_summary
            )
            
            progress.update(task, description="Analysis complete!")
        
        # Display results
        if results.get('status') == 'completed':
            _display_analysis_results(results)
        else:
            console.print(f"[bold red]Analysis failed:[/bold red] {results.get('error', 'Unknown error')}")
            sys.exit(1)
        
        # Save results if requested
        if output:
            _save_results(results, output)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument('repo_url')
@click.argument('file_path')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for analysis results (JSON)')
@click.option('--github-token', envvar='GITHUB_TOKEN',
              help='GitHub API token')
@click.option('--gemini-key', envvar='GEMINI_API_KEY',
              help='Google Gemini API key')
def analyze_file(repo_url: str,
                file_path: str,
                output: Optional[str],
                github_token: Optional[str],
                gemini_key: Optional[str]) -> None:
    """Analyze a single file from an HSF training repository."""
    
    console.print(Panel.fit(
        f"[bold blue]Single File Analysis[/bold blue]\n"
        f"Repository: [green]{repo_url}[/green]\n"
        f"File: [yellow]{file_path}[/yellow]",
        border_style="blue"
    ))
    
    try:
        # Initialize analyzer
        with console.status("[bold green]Initializing analyzer...", spinner="dots"):
            analyzer = HSFTrainingAnalyzer(
                github_token=github_token,
                gemini_api_key=gemini_key
            )
        
        # Analyze file
        with console.status(f"[bold green]Analyzing {file_path}...", spinner="dots"):
            result = analyzer.analyze_single_file(repo_url, file_path)
        
        # Display results
        if result.get('status') == 'completed':
            _display_file_analysis(result)
        else:
            console.print(f"[bold red]Analysis failed:[/bold red] {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        # Save results if requested
        if output:
            _save_results(result, output)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def config() -> None:
    """Show current configuration settings."""
    try:
        settings = get_settings()
        
        config_table = Table(title="Configuration Settings", show_header=True)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        config_table.add_column("Source", style="yellow")
        
        # Display key settings (masking sensitive values)
        config_table.add_row("Gemini API Key", 
                           "*" * 20 if settings.gemini_api_key else "Not set",
                           "Environment")
        config_table.add_row("GitHub Token", 
                           "*" * 20 if settings.github_token else "Not set",
                           "Environment")
        config_table.add_row("Log Level", settings.log_level, "Config")
        config_table.add_row("Max File Size (MB)", str(settings.max_file_size_mb), "Config")
        config_table.add_row("Analysis Timeout (s)", str(settings.analysis_timeout_seconds), "Config")
        config_table.add_row("Gemini Model", settings.gemini_model, "Config")
        
        console.print(config_table)
        
        # Show supported file extensions
        console.print(f"\n[bold]Supported Extensions:[/bold] {', '.join(settings.supported_extensions)}")
        console.print(f"[bold]Ignore Patterns:[/bold] {', '.join(settings.ignore_patterns)}")
        
    except Exception as e:
        console.print(f"[bold red]Error loading configuration:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def version() -> None:
    """Show version information."""
    try:
        from hsf_training_agent import __version__
        console.print(f"HSF Training AI Maintenance Agent v{__version__}")
    except ImportError:
        console.print("HSF Training AI Maintenance Agent v0.1.0")


def _display_analysis_results(results: dict) -> None:
    """Display analysis results in a formatted table."""
    summary = HSFTrainingAnalyzer(github_token="dummy", gemini_api_key="dummy").get_analysis_summary(results)
    
    # Summary statistics
    stats_table = Table(title="Analysis Summary", show_header=True)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Files Analyzed", str(summary.get('total_files', 0)))
    stats_table.add_row("Total Suggestions", str(summary.get('total_suggestions', 0)))
    stats_table.add_row("Files with Suggestions", str(summary.get('files_with_suggestions', 0)))
    stats_table.add_row("GitHub Issues Created", str(summary.get('github_issues_created', 0)))
    
    console.print(stats_table)
    
    # Suggestion types
    if summary.get('suggestion_types'):
        types_table = Table(title="Suggestion Types", show_header=True)
        types_table.add_column("Type", style="cyan")
        types_table.add_column("Count", style="green")
        
        for type_name, count in summary['suggestion_types'].items():
            types_table.add_row(type_name.replace('_', ' ').title(), str(count))
        
        console.print(types_table)
    
    # Priority distribution
    if summary.get('priority_distribution'):
        priority_table = Table(title="Priority Distribution", show_header=True)
        priority_table.add_column("Priority", style="cyan")
        priority_table.add_column("Count", style="green")
        
        for priority, count in summary['priority_distribution'].items():
            color = {"high": "red", "medium": "yellow", "low": "green"}.get(priority, "white")
            priority_table.add_row(f"[{color}]{priority.title()}[/{color}]", str(count))
        
        console.print(priority_table)


def _display_file_analysis(result: dict) -> None:
    """Display single file analysis results."""
    file_path = result.get('file_path', 'Unknown')
    analysis = result.get('ai_analysis', {})
    
    console.print(f"\n[bold]Analysis for:[/bold] {file_path}")
    
    if analysis and 'suggestions' in analysis:
        suggestions = analysis['suggestions']
        
        if suggestions:
            console.print(f"[green]Found {len(suggestions)} suggestions:[/green]\n")
            
            for i, suggestion in enumerate(suggestions, 1):
                priority_color = {
                    "high": "red",
                    "medium": "yellow", 
                    "low": "green"
                }.get(suggestion.get('priority', 'medium').lower(), "white")
                
                console.print(Panel(
                    f"[bold]{suggestion.get('title', 'Suggestion')}\n\n[/bold]"
                    f"[bold]Type:[/bold] {suggestion.get('type', 'Unknown')}\n"
                    f"[bold]Priority:[/bold] [{priority_color}]{suggestion.get('priority', 'Medium')}[/{priority_color}]\n\n"
                    f"[bold]Description:[/bold]\n{suggestion.get('description', 'No description')}\n\n"
                    f"[bold]Justification:[/bold]\n{suggestion.get('justification', 'No justification')}",
                    title=f"Suggestion {i}",
                    border_style=priority_color
                ))
        else:
            console.print("[green]No suggestions found - content appears up to date![/green]")
    else:
        console.print("[yellow]Analysis completed but no structured results available[/yellow]")


def _save_results(results: dict, output_path: str) -> None:
    """Save analysis results to JSON file."""
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"[green]Results saved to:[/green] {output_path}")
    except Exception as e:
        console.print(f"[bold red]Failed to save results:[/bold red] {e}")


if __name__ == '__main__':
    cli()