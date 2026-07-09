#!/usr/bin/env python3
"""
Quick Project Review CLI
=======================

A simple command-line interface to run the Project Reviewer Agent
"""

import os
import sys
import argparse
from datetime import datetime
from project_reviewer_agent import ProjectReviewerAgent, ProjectType

def display_banner():
    """Display the application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                   PROJECT REVIEWER AGENT                     ║
║              Senior Software Developer & AI Engineer         ║
║                         Version 1.0.0                        ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def display_review_summary(review):
    """Display a quick summary of the review"""
    print(f"\n📊 REVIEW SUMMARY")
    print("=" * 50)
    print(f"🎯 Project: {review.project_name}")
    print(f"📅 Reviewed: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🏆 Overall Score: {review.overall_score}/10")
    print(f"⚡ Complexity: {review.complexity_rating}")
    print(f"🔧 Technical Debt: {review.technical_debt_level}")
    print(f"🛠️  Maintainability: {review.maintainability_index}/10")
    
    # Score breakdown
    print(f"\n📈 CATEGORY BREAKDOWN")
    print("-" * 30)
    for score in review.category_scores:
        category = score.category.value.replace('_', ' ').title()
        emoji = "🟢" if score.score >= 8 else "🟡" if score.score >= 6 else "🔴"
        print(f"{emoji} {category:20s} {score.score:4.1f}/10")
    
    # Top strengths
    if review.strengths:
        print(f"\n✅ TOP STRENGTHS")
        print("-" * 20)
        for strength in review.strengths[:3]:
            print(f"  • {strength}")
    
    # Critical issues
    critical_issues = []
    for score in review.category_scores:
        critical_issues.extend(score.critical_issues)
    
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES")
        print("-" * 20)
        for issue in critical_issues[:3]:
            print(f"  ⚠️  {issue}")
    
    # Top recommendations
    if review.recommendations:
        print(f"\n🎯 TOP RECOMMENDATIONS")
        print("-" * 25)
        for rec in review.recommendations[:3]:
            print(f"  💡 {rec}")
    
    print(f"\n📝 REVIEWER NOTES")
    print("-" * 20)
    print(f"  {review.reviewer_notes}")

def quick_review():
    """Run a quick review of the current directory"""
    print("🔍 Starting quick review of current directory...")
    
    reviewer = ProjectReviewerAgent(".")
    review = reviewer.review_project()
    
    display_review_summary(review)
    
    # Ask if user wants detailed report
    response = input("\n❓ Generate detailed report? (y/N): ").lower().strip()
    if response in ['y', 'yes']:
        report_path = reviewer.generate_report(review)
        json_path = reviewer.save_review_json(review)
        print(f"\n📋 Detailed report saved: {report_path}")
        print(f"💾 JSON data saved: {json_path}")

def interactive_review():
    """Run an interactive review session"""
    print("🤖 Welcome to Interactive Project Review!")
    print("\nI'll help you analyze your project step by step.\n")
    
    # Get project path
    path = input("📁 Enter project path (press Enter for current directory): ").strip()
    if not path:
        path = "."
    
    if not os.path.exists(path):
        print(f"❌ Path '{path}' does not exist!")
        return
    
    # Get project name
    project_name = input("🏷️  Enter project name (optional): ").strip()
    if not project_name:
        project_name = os.path.basename(os.path.abspath(path))
    
    print(f"\n🔍 Analyzing project: {project_name}")
    print("⏳ This may take a moment...")
    
    # Run review
    reviewer = ProjectReviewerAgent(path)
    review = reviewer.review_project(project_name)
    
    display_review_summary(review)
    
    # Interactive options
    while True:
        print(f"\n🔧 WHAT WOULD YOU LIKE TO DO?")
        print("1. 📋 Generate detailed report")
        print("2. 🔍 View specific category details")
        print("3. 💾 Export as JSON")
        print("4. 🎯 Get improvement roadmap")
        print("5. ❌ Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            report_path = reviewer.generate_report(review)
            print(f"📋 Report saved: {report_path}")
            
        elif choice == "2":
            print("\n📊 CATEGORY DETAILS")
            print("-" * 20)
            for i, score in enumerate(review.category_scores, 1):
                category = score.category.value.replace('_', ' ').title()
                print(f"{i}. {category} ({score.score}/10)")
            
            try:
                cat_choice = int(input("\nSelect category (number): ")) - 1
                if 0 <= cat_choice < len(review.category_scores):
                    score = review.category_scores[cat_choice]
                    print(f"\n📈 {score.category.value.replace('_', ' ').title()}")
                    print(f"Score: {score.score}/10")
                    print(f"Feedback: {score.feedback}")
                    if score.suggestions:
                        print("Suggestions:")
                        for suggestion in score.suggestions:
                            print(f"  • {suggestion}")
                    if score.critical_issues:
                        print("Critical Issues:")
                        for issue in score.critical_issues:
                            print(f"  ⚠️  {issue}")
            except (ValueError, IndexError):
                print("❌ Invalid selection!")
                
        elif choice == "3":
            json_path = reviewer.save_review_json(review)
            print(f"💾 JSON exported: {json_path}")
            
        elif choice == "4":
            print(f"\n🎯 IMPROVEMENT ROADMAP")
            print("=" * 30)
            
            # Prioritize by score
            low_scores = [s for s in review.category_scores if s.score < 7]
            low_scores.sort(key=lambda x: x.score)
            
            if low_scores:
                print("🔥 IMMEDIATE PRIORITIES:")
                for i, score in enumerate(low_scores[:3], 1):
                    category = score.category.value.replace('_', ' ').title()
                    print(f"{i}. {category} (Score: {score.score}/10)")
                    if score.suggestions:
                        print(f"   → {score.suggestions[0]}")
            
            print(f"\n💡 GENERAL RECOMMENDATIONS:")
            for i, rec in enumerate(review.recommendations[:5], 1):
                print(f"{i}. {rec}")
                
        elif choice == "5":
            print("👋 Thanks for using Project Reviewer Agent!")
            break
        else:
            print("❌ Invalid choice! Please select 1-5.")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Project Reviewer Agent - Senior Software Developer & AI Engineer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python review_cli.py --quick                    # Quick review of current directory
  python review_cli.py --interactive              # Interactive review session
  python review_cli.py --path /path/to/project    # Review specific project
  python review_cli.py --name "My Project"        # Review with custom name
        """
    )
    
    parser.add_argument("--quick", "-q", action="store_true", 
                       help="Run quick review of current directory")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Start interactive review session")
    parser.add_argument("--path", "-p", default=".",
                       help="Path to project directory (default: current)")
    parser.add_argument("--name", "-n", 
                       help="Project name")
    parser.add_argument("--output", "-o",
                       help="Output directory for reports")
    parser.add_argument("--silent", "-s", action="store_true",
                       help="Silent mode - minimal output")
    
    args = parser.parse_args()
    
    if not args.silent:
        display_banner()
    
    try:
        if args.interactive:
            interactive_review()
        elif args.quick:
            quick_review()
        else:
            # Standard review
            if not args.silent:
                print(f"🔍 Reviewing project at: {args.path}")
            
            reviewer = ProjectReviewerAgent(args.path)
            review = reviewer.review_project(args.name)
            
            if not args.silent:
                display_review_summary(review)
            
            # Generate reports
            output_dir = args.output or "."
            report_path = reviewer.generate_report(review, 
                os.path.join(output_dir, f"{review.project_name}_review_report.md"))
            json_path = reviewer.save_review_json(review,
                os.path.join(output_dir, f"{review.project_name}_review.json"))
            
            if not args.silent:
                print(f"\n📋 Report saved: {report_path}")
                print(f"💾 JSON saved: {json_path}")
            else:
                print(f"Review completed. Score: {review.overall_score}/10")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Review cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during review: {e}")
        if not args.silent:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
