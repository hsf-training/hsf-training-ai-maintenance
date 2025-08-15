#!/usr/bin/env python3
"""
Example usage of HSF Training AI Maintenance Agent
"""

import os
import sys
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from hsf_training_agent.src.analyzer import HSFTrainingAnalyzer
from hsf_training_agent.src.config import load_env_file

def main():
    """Example usage of the HSF Training AI agent."""
    
    # Load configuration from .env file
    load_env_file()
    
    # Example repository URL (replace with actual HSF training repo)
    repo_url = "https://github.com/hsf-training/hsf-training-singularity-webpage"
    
    print(f"🔍 Analyzing HSF training repository: {repo_url}")
    
    try:
        # Initialize the analyzer
        analyzer = HSFTrainingAnalyzer()
        
        print("📊 Starting repository analysis...")
        
        # Analyze the repository
        results = analyzer.analyze_repository(
            repo_url=repo_url,
            create_issues=False,  # Set to True to create actual GitHub issues
            create_summary=False  # Set to True to create summary issue
        )
        
        # Display results
        if results.get('status') == 'completed':
            print("✅ Analysis completed successfully!")
            
            # Get summary statistics
            summary = analyzer.get_analysis_summary(results)
            
            print(f"\n📈 Analysis Summary:")
            print(f"  • Files analyzed: {summary.get('total_files', 0)}")
            print(f"  • Total suggestions: {summary.get('total_suggestions', 0)}")
            print(f"  • Files with suggestions: {summary.get('files_with_suggestions', 0)}")
            
            # Show suggestion types
            if summary.get('suggestion_types'):
                print(f"\n🏷️  Suggestion Types:")
                for suggestion_type, count in summary['suggestion_types'].items():
                    print(f"  • {suggestion_type.replace('_', ' ').title()}: {count}")
            
            # Show priority distribution
            if summary.get('priority_distribution'):
                print(f"\n⚡ Priority Distribution:")
                for priority, count in summary['priority_distribution'].items():
                    print(f"  • {priority.title()}: {count}")
            
            # Show first few suggestions as examples
            ai_results = results.get('ai_analysis', {})
            example_count = 0
            
            print(f"\n💡 Example Suggestions:")
            for file_path, analysis in ai_results.items():
                if analysis and 'suggestions' in analysis and example_count < 3:
                    suggestions = analysis['suggestions'][:2]  # First 2 suggestions per file
                    
                    print(f"\n  📁 {file_path}:")
                    for suggestion in suggestions:
                        print(f"    • {suggestion.get('title', 'Untitled')}")
                        print(f"      Type: {suggestion.get('type', 'unknown')}")
                        print(f"      Priority: {suggestion.get('priority', 'medium')}")
                        print(f"      Description: {suggestion.get('description', 'No description')[:100]}...")
                    
                    example_count += 1
                    
                if example_count >= 3:
                    break
            
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0


def analyze_single_file_example():
    """Example of analyzing a single file."""
    
    load_env_file()
    
    repo_url = "https://github.com/hsf-training/hsf-training-singularity-webpage"
    file_path = "_episodes/01-introduction.md"  # Example file path
    
    print(f"🔍 Analyzing single file: {file_path}")
    
    try:
        analyzer = HSFTrainingAnalyzer()
        
        result = analyzer.analyze_single_file(repo_url, file_path)
        
        if result.get('status') == 'completed':
            print("✅ File analysis completed!")
            
            analysis = result.get('ai_analysis', {})
            if analysis and 'suggestions' in analysis:
                suggestions = analysis['suggestions']
                print(f"📝 Found {len(suggestions)} suggestions for {file_path}")
                
                for i, suggestion in enumerate(suggestions[:3], 1):
                    print(f"\n  {i}. {suggestion.get('title', 'Suggestion')}")
                    print(f"     Priority: {suggestion.get('priority', 'medium')}")
                    print(f"     Type: {suggestion.get('type', 'unknown')}")
                    print(f"     Description: {suggestion.get('description', 'No description')[:150]}...")
            else:
                print("✨ No suggestions needed - content appears up to date!")
        else:
            print(f"❌ File analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during file analysis: {e}")


if __name__ == "__main__":
    # Check if API keys are configured
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not found in environment")
        print("   Please set your Gemini API key in .env file")
        print("   Example: GEMINI_API_KEY=your_api_key_here")
    
    print("🚀 HSF Training AI Agent - Example Usage")
    print("=" * 50)
    
    # Run main repository analysis example
    exit_code = main()
    
    print("\n" + "=" * 50)
    print("🔍 Single File Analysis Example")
    print("=" * 50)
    
    # Run single file analysis example
    analyze_single_file_example()
    
    sys.exit(exit_code)