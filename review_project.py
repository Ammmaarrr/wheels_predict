#!/usr/bin/env python3
"""
Project Reviewer CLI
===================

Command-line interface for the Senior Software Developer & AI Engineer
Project Reviewer Agent.

Usage:
    python review_project.py [project_path] [options]

Examples:
    python review_project.py                    # Review current directory
    python review_project.py ../my-project      # Review specific project
    python review_project.py --output report.md # Save report to file
    python review_project.py --format json      # Output as JSON
"""

import os
import sys
import argparse
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from project_reviewer_agent import ProjectReviewerAgent


def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Senior Software Developer & AI Engineer Project Reviewer",
        epilog="Review projects with AI-powered analysis and recommendations"
    )
    
    parser.add_argument(
        "project_path", 
        nargs='?', 
        default=".", 
        help="Path to the project to review (default: current directory)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file for the report (default: print to console)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress during analysis"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip AI analysis for faster results"
    )
    
    args = parser.parse_args()
    
    # Validate project path
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"❌ Error: Project path '{project_path}' does not exist")
        sys.exit(1)
    
    if not project_path.is_dir():
        print(f"❌ Error: '{project_path}' is not a directory")
        sys.exit(1)
    
    # Initialize reviewer
    print("🤖 Initializing Senior Project Reviewer Agent...")
    if args.verbose:
        print(f"📁 Project path: {project_path}")
        print(f"🧠 AI Model: Claude Sonnet 4 via OpenRouter")
        print(f"📋 Output format: {args.format}")
    
    try:
        reviewer = ProjectReviewerAgent(str(project_path))
        
        # Perform analysis
        if args.quick:
            print("⚡ Running quick analysis (no AI analysis)...")
            # Temporarily disable AI analysis
            original_method = reviewer._perform_ai_analysis
            reviewer._perform_ai_analysis = lambda: None
            result = reviewer.analyze_project()
            reviewer._perform_ai_analysis = original_method
        else:
            result = reviewer.analyze_project()
        
        # Generate output
        if args.format == "json":
            import json
            from dataclasses import asdict
            
            report_data = asdict(result)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, default=str)
                print(f"📄 JSON report saved to: {args.output}")
            else:
                print(json.dumps(report_data, indent=2, default=str))
        else:
            # Markdown format
            report = reviewer.generate_report(result, args.output)
            if not args.output:
                print(report)
        
        # Show summary
        print(f"\n🎉 Review completed!")
        print(f"📊 Overall Score: {result.overall_score}/10.0")
        print(f"⚠️ Issues Found: {len(result.issues)}")
        
        critical_issues = [i for i in result.issues if i.severity == 'critical']
        if critical_issues:
            print(f"🚨 Critical Issues: {len(critical_issues)}")
        
        if args.output:
            print(f"📄 Report saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Analysis interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def show_examples():
    """Show usage examples"""
    examples = """
🚀 Project Reviewer CLI Examples:

Basic usage:
  python review_project.py                    # Review current directory
  python review_project.py ../my-project      # Review specific project

Output options:
  python review_project.py --output report.md # Save markdown report
  python review_project.py --format json      # Output as JSON
  python review_project.py -o report.json -f json  # Save JSON report

Analysis options:
  python review_project.py --quick            # Skip AI analysis
  python review_project.py --verbose          # Show detailed progress

Advanced usage:
  python review_project.py /path/to/project --output /reports/analysis.md --verbose
  python review_project.py . --format json --output project_metrics.json
"""
    print(examples)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        main()
    elif len(sys.argv) > 1 and sys.argv[1] in ["examples", "--examples"]:
        show_examples()
    else:
        main()
