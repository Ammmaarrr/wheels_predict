#!/usr/bin/env python3
"""
Quick Project Review Script
===========================

A simple script to quickly run the project reviewer agent on the current project.
"""

import sys
import os
from pathlib import Path
from project_reviewer_agent import ProjectReviewerAgent

def main():
    """Run a quick project review"""
    print("🚀 Quick Project Review")
    print("=" * 50)
    
    # Get project path (current directory by default)
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Initialize and run the reviewer
    try:
        print(f"📁 Analyzing project: {Path(project_path).absolute()}")
        
        reviewer = ProjectReviewerAgent(project_path)
        result = reviewer.analyze_project()
        
        # Generate and display quick summary
        print("\n" + "="*50)
        print("📊 QUICK SUMMARY")
        print("="*50)
        print(f"🎯 Overall Score: {result.overall_score}/10.0")
        print(f"📈 Total Files: {result.metrics.total_files}")
        print(f"💻 Lines of Code: {result.metrics.code_lines:,}")
        print(f"🧪 Test Files: {result.metrics.test_files}")
        print(f"📚 Documentation Files: {result.metrics.documentation_files}")
        
        # Show critical issues
        critical_issues = [i for i in result.issues if i.severity == 'critical']
        high_issues = [i for i in result.issues if i.severity == 'high']
        
        print(f"\n⚠️ ISSUES SUMMARY:")
        print(f"  🚨 Critical: {len(critical_issues)}")
        print(f"  ⚠️ High: {len(high_issues)}")
        print(f"  📝 Total: {len(result.issues)}")
        
        # Show top 3 recommendations
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec}")
        
        # Show AI analysis if available
        if result.ai_analysis:
            print(f"\n🧠 AI INSIGHTS:")
            # Show first few lines of AI analysis
            ai_lines = result.ai_analysis.split('\n')[:5]
            for line in ai_lines:
                if line.strip():
                    print(f"  {line.strip()}")
            print("  ... (see full report for complete AI analysis)")
        
        # Save detailed report
        report_file = f"project_review_{Path(project_path).name}_{result.review_timestamp[:10]}.md"
        report = reviewer.generate_report(result, report_file)
        
        print(f"\n📄 Full report saved to: {report_file}")
        print("\n✅ Review completed successfully!")
        
        # Return exit code based on critical issues
        if len(critical_issues) > 0:
            print("⚠️ WARNING: Critical issues found - review required before production!")
            return 1
        else:
            return 0
            
    except Exception as e:
        print(f"❌ Error during review: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
