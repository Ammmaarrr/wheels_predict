"""
Senior Software Developer & AI Engineer Project Reviewer Agent
==============================================================

An intelligent agent that analyzes and reviews software projects with focus on:
- Code quality and architecture
- AI/ML implementation best practices
- Security vulnerabilities
- Performance optimization
- Documentation and testing
- Scalability and maintainability

Author: AI Agent
Version: 2.0.0 (Enhanced with OpenRouter API)
"""

import os
import re
import json
import ast
import time
from pathlib import Path
from openai import OpenAI
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import mimetypes

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from typing import Dict, List, Any
import json
import tempfile
from datetime import datetime
import subprocess
import requests

from config.development.reviewer_config import (
    OPENROUTER_CONFIG, REVIEW_WEIGHTS, SEVERITY_THRESHOLDS,
    FILE_SIZE_LIMITS, COMPLEXITY_THRESHOLDS, LANGUAGE_PATTERNS,
    SECURITY_PATTERNS, DOCUMENTATION_REQUIREMENTS, TESTING_REQUIREMENTS,
    PERFORMANCE_BENCHMARKS, AI_ML_REQUIREMENTS
)


@dataclass
class ReviewIssue:
    """Represents a single review issue"""
    severity: str
    category: str
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    impact_score: float


@dataclass
class ProjectMetrics:
    """Project-wide metrics"""
    total_files: int
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    test_files: int
    documentation_files: int
    languages: Dict[str, int]
    dependencies: List[str]
    file_size_distribution: Dict[str, int]


@dataclass
class ReviewResult:
    """Complete review result"""
    overall_score: float
    category_scores: Dict[str, float]
    issues: List[ReviewIssue]
    metrics: ProjectMetrics
    recommendations: List[str]
    strengths: List[str]
    ai_analysis: Optional[str]
    review_timestamp: str


class ProjectReviewerAgent:
    """Senior Software Developer & AI Engineer Project Reviewer"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues: List[ReviewIssue] = []
        self.metrics = ProjectMetrics(
            total_files=0, total_lines=0, code_lines=0, comment_lines=0,
            blank_lines=0, test_files=0, documentation_files=0,
            languages={}, dependencies=[], file_size_distribution={}
        )
        
        # Initialize OpenRouter client
        self.api_config = OPENROUTER_CONFIG
        self.openai_client = OpenAI(
            base_url=self.api_config['base_url'],
            api_key=self.api_config['api_key']
        )
        
        # File extensions to analyze
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
            '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.swift', '.scala'
        }
        
        self.text_extensions = {
            '.md', '.txt', '.rst', '.yml', '.yaml', '.json', '.xml',
            '.toml', '.ini', '.cfg', '.conf'
        }
        
        print(f"🤖 Senior Project Reviewer Agent initialized")
        print(f"📁 Project: {self.project_path}")
        print(f"🧠 AI Model: {self.api_config['model']}")
    
    def analyze_project(self) -> ReviewResult:
        """Main method to analyze the entire project"""
        print("\n🔍 Starting comprehensive project analysis...")
        
        # Phase 1: File discovery and metrics
        print("📊 Phase 1: Collecting project metrics...")
        self._collect_metrics()
        
        # Phase 2: Static analysis
        print("🔧 Phase 2: Performing static code analysis...")
        self._analyze_code_quality()
        self._analyze_architecture()
        self._analyze_security()
        self._analyze_performance()
        
        # Phase 3: AI/ML specific analysis
        print("🤖 Phase 3: Analyzing AI/ML implementation...")
        self._analyze_ai_ml_implementation()
        
        # Phase 4: Documentation and testing
        print("📚 Phase 4: Evaluating documentation and testing...")
        self._analyze_documentation()
        self._analyze_testing()
        
        # Phase 5: AI-powered deep analysis
        print("🧠 Phase 5: Performing AI-powered deep analysis...")
        ai_analysis = self._perform_ai_analysis()
        
        # Phase 6: Calculate scores and generate report
        print("📋 Phase 6: Calculating scores and generating report...")
        category_scores = self._calculate_category_scores()
        overall_score = self._calculate_overall_score(category_scores)
        
        recommendations = self._generate_recommendations()
        strengths = self._identify_strengths()
        
        result = ReviewResult(
            overall_score=overall_score,
            category_scores=category_scores,
            issues=self.issues,
            metrics=self.metrics,
            recommendations=recommendations,
            strengths=strengths,
            ai_analysis=ai_analysis,
            review_timestamp=datetime.now().isoformat()
        )
        
        print("✅ Project analysis completed!")
        return result
    
    def _collect_metrics(self):
        """Collect basic project metrics"""
        for file_path in self._get_all_files():
            if self._should_analyze_file(file_path):
                self._analyze_file_metrics(file_path)
    
    def _get_all_files(self) -> List[Path]:
        """Get all files in the project"""
        files = []
        for root, dirs, filenames in os.walk(self.project_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      {'node_modules', '__pycache__', 'venv', 'env', 'build', 'dist'}]
            
            for filename in filenames:
                if not filename.startswith('.'):
                    files.append(Path(root) / filename)
        return files
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""
        return (file_path.suffix in self.code_extensions or 
                file_path.suffix in self.text_extensions)
    
    def _analyze_file_metrics(self, file_path: Path):
        """Analyze metrics for a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            self.metrics.total_files += 1
            self.metrics.total_lines += len(lines)
            
            # Count different types of lines
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    self.metrics.blank_lines += 1
                elif stripped.startswith('#') or stripped.startswith('//'):
                    self.metrics.comment_lines += 1
                else:
                    self.metrics.code_lines += 1
            
            # Track languages
            ext = file_path.suffix
            self.metrics.languages[ext] = self.metrics.languages.get(ext, 0) + 1
            
            # Track file sizes
            size_kb = len(content) // 1024
            if size_kb < 1:
                self.metrics.file_size_distribution['<1KB'] = \
                    self.metrics.file_size_distribution.get('<1KB', 0) + 1
            elif size_kb < 10:
                self.metrics.file_size_distribution['1-10KB'] = \
                    self.metrics.file_size_distribution.get('1-10KB', 0) + 1
            elif size_kb < 100:
                self.metrics.file_size_distribution['10-100KB'] = \
                    self.metrics.file_size_distribution.get('10-100KB', 0) + 1
            else:
                self.metrics.file_size_distribution['>100KB'] = \
                    self.metrics.file_size_distribution.get('>100KB', 0) + 1
            
            # Check if it's a test file
            if 'test' in file_path.name.lower() or 'spec' in file_path.name.lower():
                self.metrics.test_files += 1
            
            # Check if it's documentation
            if file_path.suffix in {'.md', '.rst', '.txt'}:
                self.metrics.documentation_files += 1
            
        except Exception as e:
            self._add_issue("medium", "file_analysis", str(file_path), None,
                          f"Could not analyze file: {str(e)}", 
                          "Ensure file encoding is UTF-8 or add proper encoding", 3.0)
    
    def _analyze_code_quality(self):
        """Analyze code quality issues"""
        for file_path in self._get_all_files():
            if file_path.suffix == '.py':
                self._analyze_python_file(file_path)
            elif file_path.suffix in {'.js', '.ts', '.jsx', '.tsx'}:
                self._analyze_javascript_file(file_path)
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze Python file for quality issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                self._analyze_python_ast(tree, file_path, lines)
            except SyntaxError as e:
                self._add_issue("high", "code_quality", str(file_path), e.lineno,
                              f"Syntax error: {str(e)}", 
                              "Fix syntax errors before deployment", 7.0)
            
            # Check for code smells
            self._check_python_code_smells(file_path, lines)
            
        except Exception as e:
            self._add_issue("medium", "code_quality", str(file_path), None,
                          f"Could not analyze Python file: {str(e)}", 
                          "Ensure file is valid Python code", 4.0)
    
    def _analyze_python_ast(self, tree: ast.AST, file_path: Path, lines: List[str]):
        """Analyze Python AST for complex issues"""
        for node in ast.walk(tree):
            # Check function complexity
            if isinstance(node, ast.FunctionDef):
                func_lines = self._count_function_lines(node, lines)
                if func_lines > COMPLEXITY_THRESHOLDS['function_length']['critical']:
                    self._add_issue("high", "code_quality", str(file_path), node.lineno,
                                  f"Function '{node.name}' is too long ({func_lines} lines)",
                                  "Break down into smaller functions", 6.0)
                elif func_lines > COMPLEXITY_THRESHOLDS['function_length']['warning']:
                    self._add_issue("medium", "code_quality", str(file_path), node.lineno,
                                  f"Function '{node.name}' is quite long ({func_lines} lines)",
                                  "Consider breaking down into smaller functions", 4.0)
                
                # Check parameter count
                if len(node.args.args) > PERFORMANCE_BENCHMARKS['max_parameters']:
                    self._add_issue("medium", "code_quality", str(file_path), node.lineno,
                                  f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                                  "Use data classes or reduce parameter count", 4.0)
    
    def _count_function_lines(self, func_node: ast.FunctionDef, lines: List[str]) -> int:
        """Count lines in a function"""
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            return func_node.end_lineno - func_node.lineno + 1
        return 1
    
    def _check_python_code_smells(self, file_path: Path, lines: List[str]):
        """Check for Python code smells"""
        for i, line in enumerate(lines, 1):
            # Check for hardcoded values
            if re.search(r'password\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                self._add_issue("critical", "security", str(file_path), i,
                              "Hardcoded password detected",
                              "Use environment variables or config files", 9.0)
            
            # Check for long lines
            if len(line) > 120:
                self._add_issue("low", "code_quality", str(file_path), i,
                              f"Line too long ({len(line)} characters)",
                              "Break line or refactor to improve readability", 2.0)
    
    def _analyze_javascript_file(self, file_path: Path):
        """Analyze JavaScript/TypeScript files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Basic JavaScript analysis
            for i, line in enumerate(lines, 1):
                # Check for console.log in production code
                if 'console.log' in line and 'test' not in str(file_path).lower():
                    self._add_issue("low", "code_quality", str(file_path), i,
                                  "Console.log statement found in production code",
                                  "Remove debug statements before deployment", 2.0)
                
                # Check for potentially unsafe patterns (excluding legitimate uses)
                if 'eval(' in line and 'test' not in str(file_path).lower() and 'demo' not in str(file_path).lower():
                    self._add_issue("critical", "security", str(file_path), i,
                                  "eval() usage detected - security risk",
                                  "Replace eval() with safer alternatives", 9.0)
        
        except Exception as e:
            pass  # Skip files that can't be read
    
    def _analyze_architecture(self):
        """Analyze project architecture"""
        # Check project structure
        required_dirs = ['tests', 'docs', 'src']
        missing_dirs = []
        
        for req_dir in required_dirs:
            if not (self.project_path / req_dir).exists():
                missing_dirs.append(req_dir)
        
        if missing_dirs:
            self._add_issue("medium", "architecture", str(self.project_path), None,
                          f"Missing recommended directories: {', '.join(missing_dirs)}",
                          "Create proper project structure", 4.0)
        
        # Check for configuration files
        config_files = ['requirements.txt', 'package.json', 'pyproject.toml', 'setup.py']
        has_config = any((self.project_path / cf).exists() for cf in config_files)
        
        if not has_config:
            self._add_issue("high", "architecture", str(self.project_path), None,
                          "No dependency management files found",
                          "Add requirements.txt, package.json, or pyproject.toml", 6.0)
    
    def _analyze_security(self):
        """Analyze security vulnerabilities"""
        for file_path in self._get_all_files():
            if file_path.suffix in self.code_extensions:
                self._check_security_patterns(file_path)
    
    def _check_security_patterns(self, file_path: Path):
        """Check for security patterns in code"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            for category, patterns in SECURITY_PATTERNS.items():
                for pattern in patterns:
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            severity = "critical" if category in ["sql_injection", "unsafe_deserialization"] else "high"
                            self._add_issue(severity, "security", str(file_path), i,
                                          f"Potential {category.replace('_', ' ')} vulnerability",
                                          f"Review and secure {category.replace('_', ' ')} implementation", 
                                          8.0 if severity == "critical" else 6.0)
        
        except Exception:
            pass  # Skip files that can't be read
    
    def _analyze_performance(self):
        """Analyze performance issues"""
        large_files = []
        
        for file_path in self._get_all_files():
            if self._should_analyze_file(file_path):
                try:
                    size = file_path.stat().st_size
                    if size > FILE_SIZE_LIMITS['large_file_critical']:
                        large_files.append((file_path, size))
                        self._add_issue("high", "performance", str(file_path), None,
                                      f"Very large file ({size/1024/1024:.1f}MB)",
                                      "Consider breaking into smaller modules", 6.0)
                    elif size > FILE_SIZE_LIMITS['large_file_warning']:
                        self._add_issue("medium", "performance", str(file_path), None,
                                      f"Large file ({size/1024:.0f}KB)",
                                      "Monitor file size and consider refactoring", 3.0)
                except Exception:
                    pass
    
    def _analyze_ai_ml_implementation(self):
        """Analyze AI/ML specific implementation"""
        ml_files = []
        has_ml_libs = False
        
        for file_path in self._get_all_files():
            if file_path.suffix == '.py':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check for ML libraries
                    for lib in LANGUAGE_PATTERNS['python']['ml_libraries']:
                        if f'import {lib}' in content or f'from {lib}' in content:
                            has_ml_libs = True
                            ml_files.append(file_path)
                            break
                    
                    # Check for model files
                    if any(keyword in content.lower() for keyword in 
                          ['model', 'neural', 'training', 'prediction', 'classifier']):
                        ml_files.append(file_path)
                
                except Exception:
                    pass
        
        if has_ml_libs:
            # Check for ML best practices
            self._check_ml_best_practices(ml_files)
    
    def _check_ml_best_practices(self, ml_files: List[Path]):
        """Check ML implementation best practices"""
        # Check for data validation
        has_data_validation = False
        has_model_versioning = False
        has_experiment_tracking = False
        
        for file_path in ml_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if any(keyword in content.lower() for keyword in 
                      ['validate', 'schema', 'check_data']):
                    has_data_validation = True
                
                if any(keyword in content.lower() for keyword in 
                      ['version', 'mlflow', 'wandb', 'tensorboard']):
                    has_experiment_tracking = True
                
                if any(keyword in content.lower() for keyword in 
                      ['save_model', 'load_model', 'pickle', 'joblib']):
                    has_model_versioning = True
            
            except Exception:
                pass
        
        # Add issues for missing ML best practices
        if not has_data_validation:
            self._add_issue("medium", "ai_ml_implementation", str(self.project_path), None,
                          "No data validation found in ML code",
                          "Add data validation and schema checking", 5.0)
        
        if not has_experiment_tracking:
            self._add_issue("low", "ai_ml_implementation", str(self.project_path), None,
                          "No experiment tracking detected",
                          "Consider using MLflow, Wandb, or similar tools", 3.0)
        
        if not has_model_versioning:
            self._add_issue("medium", "ai_ml_implementation", str(self.project_path), None,
                          "No clear model versioning strategy",
                          "Implement model versioning and persistence", 4.0)
    
    def _analyze_documentation(self):
        """Analyze documentation quality"""
        # Check for README
        readme_files = list(self.project_path.glob('README*'))
        if not readme_files:
            self._add_issue("high", "documentation", str(self.project_path), None,
                          "No README file found",
                          "Add a comprehensive README.md file", 6.0)
        else:
            self._analyze_readme_quality(readme_files[0])
        
        # Check comment ratio
        if self.metrics.code_lines > 0:
            comment_ratio = self.metrics.comment_lines / self.metrics.code_lines
            if comment_ratio < DOCUMENTATION_REQUIREMENTS['code_comment_ratio']:
                self._add_issue("medium", "documentation", str(self.project_path), None,
                              f"Low comment ratio ({comment_ratio:.1%})",
                              "Add more code comments and documentation", 4.0)
    
    def _analyze_readme_quality(self, readme_path: Path):
        """Analyze README file quality"""
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            required_sections = DOCUMENTATION_REQUIREMENTS['readme_sections']
            missing_sections = []
            
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                self._add_issue("medium", "documentation", str(readme_path), None,
                              f"README missing sections: {', '.join(missing_sections)}",
                              "Add missing README sections for better documentation", 3.0)
        
        except Exception:
            pass
    
    def _analyze_testing(self):
        """Analyze testing implementation"""
        if self.metrics.test_files == 0:
            self._add_issue("high", "testing", str(self.project_path), None,
                          "No test files found",
                          "Add unit tests and integration tests", 7.0)
        else:
            # Check test coverage ratio
            if self.metrics.total_files > 0:
                test_ratio = self.metrics.test_files / self.metrics.total_files
                if test_ratio < TESTING_REQUIREMENTS['test_to_code_ratio']:
                    self._add_issue("medium", "testing", str(self.project_path), None,
                                  f"Low test coverage ratio ({test_ratio:.1%})",
                                  "Add more comprehensive tests", 5.0)
    
    def _perform_ai_analysis(self) -> Optional[str]:
        """Perform AI-powered deep analysis using OpenRouter"""
        try:
            # Prepare project summary for AI analysis
            project_summary = self._prepare_project_summary()
            
            prompt = f"""
            As a senior software developer and AI engineer, analyze this project and provide insights:

            PROJECT SUMMARY:
            {project_summary}

            CURRENT ISSUES FOUND:
            {self._format_issues_for_ai()}

            Please provide:
            1. Overall assessment of the project
            2. Key architectural concerns
            3. Specific recommendations for improvement
            4. AI/ML implementation evaluation (if applicable)
            5. Production readiness assessment

            Focus on actionable insights that a senior developer would provide.
            """
            
            completion = self.openai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/wheels-predict",
                    "X-Title": "Wheels Predict Project Reviewer",
                },
                model=self.api_config['model'],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software developer and AI engineer with 10+ years of experience reviewing enterprise projects."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=self.api_config['max_tokens'],
                temperature=self.api_config['temperature']
            )
            
            return completion.choices[0].message.content
                
        except Exception as e:
            print(f"⚠️ AI analysis error: {str(e)}")
            return None
    
    def _prepare_project_summary(self) -> str:
        """Prepare a concise project summary for AI analysis"""
        return f"""
        Files: {self.metrics.total_files} ({self.metrics.code_lines} code lines)
        Languages: {dict(list(self.metrics.languages.items())[:5])}
        Tests: {self.metrics.test_files} test files
        Documentation: {self.metrics.documentation_files} docs
        Dependencies detected: {len(self.metrics.dependencies)}
        Issues found: {len(self.issues)} ({len([i for i in self.issues if i.severity == 'critical'])} critical)
        """
    
    def _format_issues_for_ai(self) -> str:
        """Format issues for AI analysis"""
        if not self.issues:
            return "No issues found."
        
        critical_issues = [i for i in self.issues if i.severity == 'critical']
        high_issues = [i for i in self.issues if i.severity == 'high']
        
        summary = f"Critical: {len(critical_issues)}, High: {len(high_issues)}, Total: {len(self.issues)}\n"
        
        if critical_issues:
            summary += "\nCRITICAL ISSUES:\n"
            for issue in critical_issues[:3]:  # Show top 3
                summary += f"- {issue.category}: {issue.description}\n"
        
        return summary
    
    def _calculate_category_scores(self) -> Dict[str, float]:
        """Calculate scores for each review category"""
        category_scores = {}
        
        for category in REVIEW_WEIGHTS.keys():
            category_issues = [i for i in self.issues if i.category == category]
            
            if not category_issues:
                category_scores[category] = 10.0
            else:
                # Calculate average impact and convert to score
                avg_impact = sum(i.impact_score for i in category_issues) / len(category_issues)
                category_scores[category] = max(0.0, 10.0 - avg_impact)
        
        return category_scores
    
    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        weighted_sum = sum(
            score * REVIEW_WEIGHTS[category] 
            for category, score in category_scores.items()
        )
        return round(weighted_sum, 2)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Critical issues first
        critical_issues = [i for i in self.issues if i.severity == 'critical']
        for issue in critical_issues[:3]:
            recommendations.append(f"🚨 CRITICAL: {issue.recommendation}")
        
        # High priority issues
        high_issues = [i for i in self.issues if i.severity == 'high']
        for issue in high_issues[:3]:
            recommendations.append(f"⚠️ HIGH: {issue.recommendation}")
        
        # General recommendations based on metrics
        if self.metrics.test_files == 0:
            recommendations.append("📋 Add comprehensive test suite")
        
        if self.metrics.documentation_files == 0:
            recommendations.append("📚 Improve project documentation")
        
        return recommendations[:10]  # Limit to top 10
    
    def _identify_strengths(self) -> List[str]:
        """Identify project strengths"""
        strengths = []
        
        if self.metrics.test_files > 0:
            test_ratio = self.metrics.test_files / max(1, self.metrics.total_files)
            if test_ratio > 0.3:
                strengths.append("✅ Good test coverage")
        
        if self.metrics.documentation_files > 0:
            strengths.append("✅ Documentation present")
        
        comment_ratio = self.metrics.comment_lines / max(1, self.metrics.code_lines)
        if comment_ratio > 0.15:
            strengths.append("✅ Well-commented code")
        
        if len([i for i in self.issues if i.severity == 'critical']) == 0:
            strengths.append("✅ No critical security issues")
        
        if self.metrics.total_files < 50:
            strengths.append("✅ Manageable project size")
        
        return strengths
    
    def _add_issue(self, severity: str, category: str, file_path: str, 
                   line_number: Optional[int], description: str, 
                   recommendation: str, impact_score: float):
        """Add a review issue"""
        issue = ReviewIssue(
            severity=severity,
            category=category,
            file_path=file_path,
            line_number=line_number,
            description=description,
            recommendation=recommendation,
            impact_score=impact_score
        )
        self.issues.append(issue)
    
    def generate_report(self, result: ReviewResult, output_path: Optional[str] = None) -> str:
        """Generate a comprehensive review report"""
        report = f"""
# 🚀 Project Review Report
**Generated by Senior Software Developer & AI Engineer Agent**
**Timestamp:** {result.review_timestamp}

## 📊 Overall Assessment
**Score: {result.overall_score}/10.0**

### Category Breakdown
"""
        
        for category, score in result.category_scores.items():
            emoji = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"
            report += f"- {emoji} **{category.replace('_', ' ').title()}**: {score:.1f}/10\n"
        
        report += f"""
## 📈 Project Metrics
- **Total Files**: {result.metrics.total_files}
- **Lines of Code**: {result.metrics.code_lines:,}
- **Test Files**: {result.metrics.test_files}
- **Documentation Files**: {result.metrics.documentation_files}
- **Languages**: {', '.join(f"{ext}({count})" for ext, count in result.metrics.languages.items())}

## ✅ Strengths
"""
        for strength in result.strengths:
            report += f"- {strength}\n"
        
        report += "\n## ⚠️ Issues Found\n"
        
        # Group issues by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_issues = [i for i in result.issues if i.severity == severity]
            if severity_issues:
                emoji = {"critical": "🚨", "high": "⚠️", "medium": "📝", "low": "💡"}[severity]
                report += f"\n### {emoji} {severity.upper()} Issues ({len(severity_issues)})\n"
                
                for issue in severity_issues[:5]:  # Limit to top 5 per severity
                    report += f"""
**{issue.category.replace('_', ' ').title()}**: {issue.description}
- **File**: `{issue.file_path}`{f" (Line {issue.line_number})" if issue.line_number else ""}
- **Recommendation**: {issue.recommendation}
- **Impact Score**: {issue.impact_score}/10
"""
        
        report += "\n## 🎯 Priority Recommendations\n"
        for i, rec in enumerate(result.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        if result.ai_analysis:
            report += f"""
## 🧠 AI Analysis
{result.ai_analysis}
"""
        
        report += f"""
## 📋 Next Steps
1. Address critical issues immediately
2. Fix high-priority security vulnerabilities
3. Improve test coverage
4. Enhance documentation
5. Consider architectural improvements

---
*Review completed by Senior Software Developer & AI Engineer Agent*
*For questions or detailed guidance, consult the development team.*
"""
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved to: {output_path}")
        
        return report


def main():
    """Main CLI interface for the Project Reviewer Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Senior Software Developer & AI Engineer Project Reviewer")
    parser.add_argument("project_path", help="Path to the project to review")
    parser.add_argument("--output", "-o", help="Output file for the report")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", 
                       help="Output format")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_path):
        print(f"❌ Error: Project path '{args.project_path}' does not exist")
        return
    
    print("🤖 Initializing Senior Project Reviewer Agent...")
    reviewer = ProjectReviewerAgent(args.project_path)
    
    # Perform the review
    result = reviewer.analyze_project()
    
    # Generate report
    if args.format == "json":
        report_data = asdict(result)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        else:
            print(json.dumps(report_data, indent=2, default=str))
    else:
        report = reviewer.generate_report(result, args.output)
        if not args.output:
            print(report)
    
    print(f"\n🎉 Review completed! Overall Score: {result.overall_score}/10")


if __name__ == "__main__":
    main()
