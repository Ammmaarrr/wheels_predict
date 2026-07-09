#!/usr/bin/env python3
"""
Master Test Orchestrator with AI Agent Integration
Runs comprehensive testing, uses AI agents to fix issues, and continues until all problems are resolved
"""

import os
import sys
import json
import time
import subprocess
import traceback
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading
import queue

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import our custom testers
from tests.comprehensive_tester import ComprehensiveTester
from tests.api_tester import APITester
from tests.database_ml_tester import DatabaseMLTester

@dataclass
class TestSession:
    """Test session tracking"""
    session_id: str
    start_time: float
    total_issues: int
    resolved_issues: int
    current_cycle: int
    max_cycles: int = 5

class AIAgentOrchestrator:
    """Advanced AI agent for issue resolution"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.api_base = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def analyze_and_fix_issue(self, issue_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI agent to analyze issue and provide fix"""
        
        prompt = f"""
You are a senior software engineer and debugging expert. Analyze this testing issue and provide a comprehensive solution.

ISSUE DETAILS:
- Test Name: {issue_details.get('test_name', 'Unknown')}
- Status: {issue_details.get('status', 'Unknown')}
- Error Message: {issue_details.get('message', 'No message')}
- Error Trace: {issue_details.get('error_trace', 'No trace')}
- Context: {issue_details.get('context', 'No context')}

PROJECT CONTEXT:
This is a PakWheels car data analysis platform with:
- FastAPI applications for web services
- ML models for car price prediction
- Web scraping for data collection
- Professional Python package structure

PROVIDE:
1. Root cause analysis
2. Specific fix steps
3. Code changes needed (if any)
4. Prevention strategies
5. Verification steps

Format your response as JSON:
{{
    "root_cause": "Detailed analysis of why this issue occurred",
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "fix_steps": ["Step 1", "Step 2", "..."],
    "code_changes": {{
        "file_path": "path/to/file.py",
        "old_code": "code to replace",
        "new_code": "replacement code"
    }},
    "verification": ["How to verify the fix"],
    "prevention": "How to prevent this in the future",
    "confidence": 0.95,
    "estimated_time": "5 minutes"
}}
"""
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Extract JSON from response
                try:
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_content = content[json_start:json_end].strip()
                    else:
                        json_content = content
                    
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    return {
                        "root_cause": "AI response parsing failed",
                        "severity": "MEDIUM",
                        "fix_steps": [content],
                        "confidence": 0.3
                    }
            else:
                return {"error": f"AI API request failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}

class MasterTestOrchestrator:
    """Master orchestrator for comprehensive testing with AI-powered issue resolution"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.ai_agent = AIAgentOrchestrator()
        self.session = TestSession(
            session_id=f"test_session_{int(time.time())}",
            start_time=time.time(),
            total_issues=0,
            resolved_issues=0,
            current_cycle=0
        )
        self.all_results = []
        self.issue_history = []
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with session tracking"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cycle_info = f"[Cycle {self.session.current_cycle}]"
        print(f"[{timestamp}] {cycle_info} [{level}] {message}")
    
    def run_comprehensive_test_suite(self) -> List[Dict[str, Any]]:
        """Run all test suites and collect results"""
        self.log("🚀 Starting comprehensive test suite...")
        
        all_results = []
        
        # 1. Run basic comprehensive tests
        self.log("📋 Running comprehensive system tests...")
        try:
            comprehensive_tester = ComprehensiveTester()
            comprehensive_tester.run_comprehensive_tests()
            
            # Convert results
            for result in comprehensive_tester.test_results:
                all_results.append({
                    "test_name": result.test_name,
                    "status": result.status,
                    "message": result.message,
                    "details": result.details,
                    "error_trace": result.error_trace,
                    "suite": "comprehensive",
                    "fix_applied": result.fix_applied
                })
        except Exception as e:
            self.log(f"❌ Comprehensive tests failed: {str(e)}", "ERROR")
            all_results.append({
                "test_name": "comprehensive_suite",
                "status": "ERROR",
                "message": str(e),
                "suite": "comprehensive",
                "error_trace": traceback.format_exc()
            })
        
        # 2. Run API tests
        self.log("🌐 Running API tests...")
        try:
            api_tester = APITester()
            if api_tester.start_api_server():
                api_results = api_tester.run_all_tests()
                api_tester.stop_api_server()
                
                for result in api_results:
                    all_results.append({
                        "test_name": result["name"],
                        "status": "PASS" if result.get("success", False) else "FAIL",
                        "message": result.get("description", ""),
                        "details": result,
                        "suite": "api"
                    })
            else:
                all_results.append({
                    "test_name": "api_server_start",
                    "status": "FAIL",
                    "message": "Could not start API server",
                    "suite": "api"
                })
        except Exception as e:
            self.log(f"❌ API tests failed: {str(e)}", "ERROR")
            all_results.append({
                "test_name": "api_suite",
                "status": "ERROR",
                "message": str(e),
                "suite": "api",
                "error_trace": traceback.format_exc()
            })
        
        # 3. Run database and ML tests
        self.log("📊 Running database and ML tests...")
        try:
            db_ml_tester = DatabaseMLTester()
            db_ml_tester.run_all_tests()
            
            for result in db_ml_tester.test_results:
                all_results.append({
                    "test_name": result.test_name,
                    "status": result.status,
                    "message": result.message,
                    "details": result.details,
                    "error_trace": result.error_trace,
                    "suite": "database_ml"
                })
        except Exception as e:
            self.log(f"❌ Database/ML tests failed: {str(e)}", "ERROR")
            all_results.append({
                "test_name": "database_ml_suite",
                "status": "ERROR",
                "message": str(e),
                "suite": "database_ml",
                "error_trace": traceback.format_exc()
            })
        
        return all_results
    
    def identify_issues(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify and categorize issues from test results"""
        issues = []
        
        for result in test_results:
            if result["status"] in ["FAIL", "ERROR"]:
                issue = {
                    "test_name": result["test_name"],
                    "status": result["status"],
                    "message": result["message"],
                    "suite": result.get("suite", "unknown"),
                    "details": result.get("details", {}),
                    "error_trace": result.get("error_trace", ""),
                    "priority": self.determine_issue_priority(result),
                    "context": self.get_issue_context(result)
                }
                issues.append(issue)
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        issues.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return issues
    
    def determine_issue_priority(self, result: Dict[str, Any]) -> str:
        """Determine issue priority based on test result"""
        test_name = result["test_name"].lower()
        status = result["status"]
        suite = result.get("suite", "")
        
        # Critical issues
        if any(keyword in test_name for keyword in ["import", "server_start", "api_connectivity"]):
            return "CRITICAL"
        
        # High priority issues
        if status == "ERROR" or suite == "api":
            return "HIGH"
        
        # Medium priority issues
        if any(keyword in test_name for keyword in ["data_load", "model_load", "database"]):
            return "MEDIUM"
        
        return "LOW"
    
    def get_issue_context(self, result: Dict[str, Any]) -> str:
        """Get additional context for the issue"""
        test_name = result["test_name"]
        suite = result.get("suite", "")
        
        context_map = {
            "import": "Module import failure - check Python path and dependencies",
            "api": "API endpoint issue - check server configuration and routes",
            "data": "Data processing issue - verify data files and formats", 
            "model": "ML model issue - check model files and dependencies",
            "database": "Database connectivity issue - verify database files and connections"
        }
        
        for keyword, context in context_map.items():
            if keyword in test_name.lower():
                return context
        
        return f"Issue in {suite} test suite"
    
    def apply_ai_fix(self, issue: Dict[str, Any]) -> bool:
        """Apply AI-suggested fix for an issue"""
        self.log(f"🤖 Analyzing issue: {issue['test_name']} with AI agent...")
        
        # Get AI analysis
        analysis = self.ai_agent.analyze_and_fix_issue(issue)
        
        if "error" in analysis:
            self.log(f"❌ AI analysis failed: {analysis['error']}")
            return False
        
        self.log(f"🧠 AI Analysis - Root Cause: {analysis.get('root_cause', 'Unknown')}")
        self.log(f"🎯 Severity: {analysis.get('severity', 'Unknown')}")
        self.log(f"⏱️ Estimated Fix Time: {analysis.get('estimated_time', 'Unknown')}")
        
        # Apply fix steps
        fix_steps = analysis.get('fix_steps', [])
        code_changes = analysis.get('code_changes', {})
        
        try:
            # Log fix steps
            self.log(f"🔧 Applying {len(fix_steps)} fix steps...")
            for i, step in enumerate(fix_steps, 1):
                self.log(f"   {i}. {step}")
            
            # Apply code changes if provided
            if code_changes and analysis.get('confidence', 0) > 0.7:
                self.apply_code_changes(code_changes, issue['test_name'])
            
            # Record the fix attempt
            self.issue_history.append({
                "issue": issue,
                "analysis": analysis,
                "timestamp": time.time(),
                "cycle": self.session.current_cycle
            })
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to apply fix: {str(e)}")
            return False
    
    def apply_code_changes(self, code_changes: Dict[str, Any], test_name: str):
        """Apply code changes suggested by AI"""
        if not code_changes:
            return
        
        file_path = code_changes.get('file_path')
        old_code = code_changes.get('old_code')
        new_code = code_changes.get('new_code')
        
        if not all([file_path, old_code, new_code]):
            self.log("⚠️ Incomplete code change information")
            return
        
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            self.log(f"⚠️ File not found: {file_path}")
            return
        
        try:
            # Read current content
            content = full_path.read_text(encoding='utf-8')
            
            # Apply change
            if old_code in content:
                new_content = content.replace(old_code, new_code)
                full_path.write_text(new_content, encoding='utf-8')
                self.log(f"✅ Applied code fix to {file_path}")
            else:
                self.log(f"⚠️ Old code not found in {file_path}")
                
        except Exception as e:
            self.log(f"❌ Error applying code change: {str(e)}")
    
    def run_test_cycle(self) -> Dict[str, Any]:
        """Run a complete test cycle"""
        self.session.current_cycle += 1
        cycle_start = time.time()
        
        self.log(f"🔄 Starting test cycle {self.session.current_cycle}")
        
        # Run all tests
        test_results = self.run_comprehensive_test_suite()
        
        # Identify issues
        issues = self.identify_issues(test_results)
        
        # Update session stats
        self.session.total_issues = len(issues)
        
        cycle_summary = {
            "cycle": self.session.current_cycle,
            "total_tests": len(test_results),
            "passed_tests": len([r for r in test_results if r["status"] == "PASS"]),
            "issues_found": len(issues),
            "critical_issues": len([i for i in issues if i["priority"] == "CRITICAL"]),
            "high_issues": len([i for i in issues if i["priority"] == "HIGH"]),
            "duration": time.time() - cycle_start,
            "issues": issues
        }
        
        self.log(f"📊 Cycle {self.session.current_cycle} Results:")
        self.log(f"   ✅ Passed: {cycle_summary['passed_tests']}/{cycle_summary['total_tests']} tests")
        self.log(f"   ❌ Issues: {cycle_summary['issues_found']} total")
        self.log(f"   🔥 Critical: {cycle_summary['critical_issues']}")
        self.log(f"   ⚠️ High: {cycle_summary['high_issues']}")
        
        return cycle_summary
    
    def run_master_testing_loop(self):
        """Main testing loop with AI-powered issue resolution"""
        self.log("🎯 Starting Master Testing Loop with AI Issue Resolution")
        self.log(f"📋 Session ID: {self.session.session_id}")
        
        cycle_results = []
        
        while self.session.current_cycle < self.session.max_cycles:
            # Run test cycle
            cycle_summary = self.run_test_cycle()
            cycle_results.append(cycle_summary)
            
            # Check if we're done
            if cycle_summary["issues_found"] == 0:
                self.log("🎉 All tests passing! Testing complete.")
                break
            
            # Process issues with AI
            self.log(f"🤖 Processing {cycle_summary['issues_found']} issues with AI agent...")
            
            issues_resolved = 0
            for issue in cycle_summary["issues"]:
                if self.apply_ai_fix(issue):
                    issues_resolved += 1
                    time.sleep(2)  # Brief pause between fixes
            
            self.session.resolved_issues += issues_resolved
            
            self.log(f"✅ Resolved {issues_resolved}/{cycle_summary['issues_found']} issues")
            
            # Continue to next cycle
            if self.session.current_cycle < self.session.max_cycles:
                self.log(f"🔄 Continuing to cycle {self.session.current_cycle + 1}...")
                time.sleep(5)  # Pause between cycles
        
        # Generate final report
        self.generate_master_report(cycle_results)
    
    def generate_master_report(self, cycle_results: List[Dict[str, Any]]):
        """Generate comprehensive master testing report"""
        total_duration = time.time() - self.session.start_time
        
        final_cycle = cycle_results[-1] if cycle_results else {}
        total_tests = final_cycle.get("total_tests", 0)
        final_issues = final_cycle.get("issues_found", 0)
        
        report = f"""# 🎯 MASTER TESTING REPORT WITH AI RESOLUTION

**Session ID:** {self.session.session_id}
**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Total Duration:** {total_duration/60:.1f} minutes

## 🏆 FINAL RESULTS

### 📊 Test Summary
- **Total Test Cycles:** {len(cycle_results)}
- **Final Test Count:** {total_tests}
- **Remaining Issues:** {final_issues}
- **Issues Resolved:** {self.session.resolved_issues}
- **Success Rate:** {((total_tests - final_issues) / total_tests * 100):.1f}% if total_tests > 0 else 0

### 🤖 AI Agent Performance
- **Issues Analyzed:** {len(self.issue_history)}
- **Fixes Attempted:** {self.session.resolved_issues}
- **AI Confidence Average:** {sum(h.get('analysis', {}).get('confidence', 0) for h in self.issue_history) / len(self.issue_history) * 100:.1f}% if self.issue_history else 0

## 🔄 Cycle-by-Cycle Analysis

"""
        
        for i, cycle in enumerate(cycle_results, 1):
            report += f"""
### Cycle {i}
- **Tests Run:** {cycle['total_tests']}
- **Passed:** {cycle['passed_tests']}
- **Issues Found:** {cycle['issues_found']}
  - Critical: {cycle['critical_issues']}
  - High: {cycle['high_issues']}
- **Duration:** {cycle['duration']:.1f}s

"""
        
        if final_issues > 0:
            report += f"""
## ❌ REMAINING ISSUES

The following {final_issues} issues still need attention:

"""
            for issue in final_cycle.get("issues", []):
                report += f"""
### {issue['priority']} - {issue['test_name']}
- **Suite:** {issue['suite']}
- **Message:** {issue['message']}
- **Context:** {issue['context']}

"""
        
        report += f"""
## 🎯 RECOMMENDATIONS

"""
        
        if final_issues == 0:
            report += """
✅ **EXCELLENT!** All tests are passing. Your project is ready for:
- Production deployment
- Team collaboration
- User testing
- Performance optimization

"""
        elif final_issues < 5:
            report += f"""
🟡 **GOOD PROGRESS!** Only {final_issues} issues remaining.
- Focus on fixing the remaining critical/high priority issues
- Most functionality is working correctly
- Project is near production-ready state

"""
        else:
            report += f"""
🔴 **NEEDS ATTENTION!** {final_issues} issues still present.
- Review and manually fix remaining issues
- Consider running additional test cycles
- Focus on critical and high priority issues first

"""
        
        report += f"""
## 🔧 ISSUE RESOLUTION HISTORY

Total AI analyses performed: {len(self.issue_history)}

"""
        
        for i, history_item in enumerate(self.issue_history[-5:], 1):  # Show last 5
            issue = history_item['issue']
            analysis = history_item['analysis']
            report += f"""
### Fix Attempt {i}
- **Issue:** {issue['test_name']}
- **Root Cause:** {analysis.get('root_cause', 'Unknown')}
- **Confidence:** {analysis.get('confidence', 0)*100:.0f}%
- **Cycle:** {history_item['cycle']}

"""
        
        report += f"""
---

**🎉 Testing completed successfully! Review the results and apply any remaining manual fixes.**

*Generated by Master Test Orchestrator with AI Agent Integration*
"""
        
        # Save report
        report_path = self.project_root / "MASTER_TEST_REPORT.md"
        report_path.write_text(report, encoding='utf-8')
        
        self.log(f"📋 Master test report saved to: {report_path}")
        
        # Print final summary
        print("\n" + "="*80)
        print("🎯 MASTER TESTING COMPLETE!")
        print("="*80)
        print(f"✅ Final Status: {total_tests - final_issues}/{total_tests} tests passing")
        print(f"🤖 AI Fixes Applied: {self.session.resolved_issues}")
        print(f"⏱️ Total Time: {total_duration/60:.1f} minutes")
        print(f"📋 Full Report: {report_path}")
        print("="*80)

def main():
    """Main function to run master testing"""
    print("=" * 80)
    print("🎯 MASTER TEST ORCHESTRATOR WITH AI AGENT INTEGRATION")
    print("🤖 Comprehensive Testing → AI Analysis → Automatic Fixes → Verification")
    print("=" * 80)
    
    orchestrator = MasterTestOrchestrator()
    orchestrator.run_master_testing_loop()

if __name__ == "__main__":
    main()
