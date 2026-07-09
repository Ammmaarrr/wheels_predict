#!/usr/bin/env python3
"""
Comprehensive File Analysis and Testing System
Tests every file in the PakWheels project and analyzes project structure
Identifies duplicates, frontend issues, and validates all components
"""

import os
import sys
import json
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import hashlib
import mimetypes
import re

# Use D: drive for all operations
D_TEMP = Path("D:/temp")
D_LOGS = Path("D:/pakwheels_analysis_logs")
D_TEMP.mkdir(exist_ok=True)
D_LOGS.mkdir(exist_ok=True)

class ComprehensiveFileAnalyzer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.file_analysis = {}
        self.duplicates_found = []
        self.frontends_found = []
        self.issues_found = []
        self.file_stats = {
            'total_files': 0,
            'by_type': {},
            'by_size': {'small': 0, 'medium': 0, 'large': 0},
            'duplicate_files': 0,
            'problematic_files': 0
        }
        
    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Save to log file
        log_file = D_LOGS / f"file_analysis_log_{datetime.now().strftime('%Y%m%d')}.txt"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception:
            pass
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file for imports, functions, classes, etc."""
        analysis = {
            'imports': [],
            'functions': [],
            'classes': [],
            'syntax_errors': [],
            'complexity': 'unknown'
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse AST
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            analysis['imports'].append(f"{module}.{alias.name}")
                    elif isinstance(node, ast.FunctionDef):
                        analysis['functions'].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        analysis['classes'].append(node.name)
                
                # Estimate complexity
                lines = len(content.splitlines())
                if lines < 50:
                    analysis['complexity'] = 'simple'
                elif lines < 200:
                    analysis['complexity'] = 'medium'
                else:
                    analysis['complexity'] = 'complex'
                    
            except SyntaxError as e:
                analysis['syntax_errors'].append(str(e))
                
        except Exception as e:
            analysis['syntax_errors'].append(f"File read error: {str(e)}")
        
        return analysis
    
    def analyze_html_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze HTML file for frontend information"""
        analysis = {
            'title': '',
            'scripts': [],
            'stylesheets': [],
            'forms': [],
            'frontend_type': 'unknown'
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                analysis['title'] = title_match.group(1).strip()
            
            # Find scripts
            script_matches = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', content, re.IGNORECASE)
            analysis['scripts'] = script_matches
            
            # Find stylesheets
            css_matches = re.findall(r'<link[^>]*href=["\']([^"\']+\.css)["\']', content, re.IGNORECASE)
            analysis['stylesheets'] = css_matches
            
            # Find forms
            form_matches = re.findall(r'<form[^>]*>', content, re.IGNORECASE)
            analysis['forms'] = [f"Form {i+1}" for i in range(len(form_matches))]
            
            # Determine frontend type
            if 'bootstrap' in content.lower():
                analysis['frontend_type'] = 'bootstrap'
            elif 'vue' in content.lower():
                analysis['frontend_type'] = 'vue'
            elif 'react' in content.lower():
                analysis['frontend_type'] = 'react'
            elif 'angular' in content.lower():
                analysis['frontend_type'] = 'angular'
            elif any(css in content.lower() for css in ['style.css', 'main.css', 'custom']):
                analysis['frontend_type'] = 'custom'
            else:
                analysis['frontend_type'] = 'basic'
                
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file comprehensively"""
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            
            # Get file info
            analysis = {
                'path': str(file_path),
                'name': file_path.name,
                'size': file_size,
                'extension': file_path.suffix.lower(),
                'mime_type': mimetypes.guess_type(str(file_path))[0] or 'unknown',
                'hash': self.get_file_hash(file_path),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'issues': [],
                'content_analysis': {}
            }
            
            # Size categorization
            if file_size < 1024:  # < 1KB
                analysis['size_category'] = 'small'
            elif file_size < 100 * 1024:  # < 100KB
                analysis['size_category'] = 'medium'
            else:
                analysis['size_category'] = 'large'
            
            # Specific analysis by file type
            if analysis['extension'] == '.py':
                analysis['content_analysis'] = self.analyze_python_file(file_path)
            elif analysis['extension'] in ['.html', '.htm']:
                analysis['content_analysis'] = self.analyze_html_file(file_path)
                self.frontends_found.append(analysis)
            elif analysis['extension'] in ['.js']:
                analysis['content_analysis'] = {'type': 'javascript', 'framework': 'unknown'}
            elif analysis['extension'] in ['.css']:
                analysis['content_analysis'] = {'type': 'stylesheet'}
            elif analysis['extension'] in ['.json']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_content = json.load(f)
                    analysis['content_analysis'] = {'type': 'json', 'valid': True, 'keys': list(json_content.keys()) if isinstance(json_content, dict) else []}
                except Exception as e:
                    analysis['content_analysis'] = {'type': 'json', 'valid': False, 'error': str(e)}
                    analysis['issues'].append(f"Invalid JSON: {str(e)}")
            
            # Check for common issues
            self.check_file_issues(file_path, analysis)
            
            return analysis
            
        except Exception as e:
            return {
                'path': str(file_path),
                'name': file_path.name,
                'error': str(e),
                'issues': [f"Analysis failed: {str(e)}"]
            }
    
    def check_file_issues(self, file_path: Path, analysis: Dict[str, Any]):
        """Check for common file issues"""
        
        # Check for empty files
        if analysis.get('size', 0) == 0:
            analysis['issues'].append("Empty file")
        
        # Check for very large files (>10MB)
        if analysis.get('size', 0) > 10 * 1024 * 1024:
            analysis['issues'].append("Very large file (>10MB)")
        
        # Check for suspicious extensions
        suspicious_extensions = ['.tmp', '.log', '.bak', '.old', '.orig']
        if any(file_path.name.endswith(ext) for ext in suspicious_extensions):
            analysis['issues'].append("Temporary or backup file")
        
        # Check for Python syntax if it's a .py file
        if file_path.suffix.lower() == '.py':
            syntax_errors = analysis.get('content_analysis', {}).get('syntax_errors', [])
            if syntax_errors:
                analysis['issues'].extend([f"Syntax error: {err}" for err in syntax_errors])
        
        # Check for duplicate names in different directories
        if file_path.name in [f.name for f in self.project_root.rglob("*") if f != file_path and f.is_file()]:
            analysis['issues'].append("Duplicate filename in project")
    
    def find_duplicate_files(self):
        """Find files with identical content"""
        hash_to_files = {}
        
        for file_path, analysis in self.file_analysis.items():
            file_hash = analysis.get('hash')
            if file_hash and file_hash != "":
                if file_hash not in hash_to_files:
                    hash_to_files[file_hash] = []
                hash_to_files[file_hash].append(file_path)
        
        # Find duplicates
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.duplicates_found.append({
                    'hash': file_hash,
                    'files': files,
                    'size': self.file_analysis[files[0]].get('size', 0)
                })
    
    def analyze_frontend_structure(self):
        """Analyze frontend structure and identify multiple frontends"""
        frontend_types = {}
        
        for frontend in self.frontends_found:
            frontend_type = frontend.get('content_analysis', {}).get('frontend_type', 'unknown')
            title = frontend.get('content_analysis', {}).get('title', 'No title')
            path = frontend.get('path', '')
            
            if frontend_type not in frontend_types:
                frontend_types[frontend_type] = []
            
            frontend_types[frontend_type].append({
                'path': path,
                'title': title,
                'size': frontend.get('size', 0)
            })
        
        self.log(f"\n📱 FRONTEND ANALYSIS:")
        self.log(f"Found {len(self.frontends_found)} HTML files")
        
        for frontend_type, files in frontend_types.items():
            self.log(f"\n{frontend_type.upper()} Frontend:")
            for file_info in files:
                self.log(f"  - {file_info['path']}")
                self.log(f"    Title: {file_info['title']}")
                self.log(f"    Size: {file_info['size']} bytes")
        
        # Check for multiple frontend frameworks
        if len(frontend_types) > 2:
            issue = f"Multiple frontend frameworks detected: {list(frontend_types.keys())}"
            self.issues_found.append(issue)
            self.log(f"⚠️ {issue}", "WARNING")
    
    def scan_all_files(self):
        """Scan all files in the project"""
        self.log("🔍 Starting comprehensive file analysis...")
        
        # Get all files
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.vscode', '.idea'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)
        
        self.file_stats['total_files'] = len(all_files)
        self.log(f"Found {len(all_files)} files to analyze")
        
        # Analyze each file
        for i, file_path in enumerate(all_files, 1):
            if i % 50 == 0:
                self.log(f"Analyzed {i}/{len(all_files)} files...")
            
            try:
                analysis = self.analyze_single_file(file_path)
                self.file_analysis[str(file_path)] = analysis
                
                # Update statistics
                ext = analysis.get('extension', 'no_extension')
                self.file_stats['by_type'][ext] = self.file_stats['by_type'].get(ext, 0) + 1
                
                size_cat = analysis.get('size_category', 'unknown')
                if size_cat in self.file_stats['by_size']:
                    self.file_stats['by_size'][size_cat] += 1
                
                if analysis.get('issues'):
                    self.file_stats['problematic_files'] += 1
                    
            except Exception as e:
                self.log(f"Error analyzing {file_path}: {e}", "ERROR")
        
        self.log(f"✅ Completed analysis of {len(all_files)} files")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        self.log("\n" + "=" * 80)
        self.log("📊 COMPREHENSIVE FILE ANALYSIS REPORT")
        self.log("=" * 80)
        
        # File statistics
        self.log(f"\n📈 FILE STATISTICS:")
        self.log(f"Total files analyzed: {self.file_stats['total_files']}")
        self.log(f"Problematic files: {self.file_stats['problematic_files']}")
        
        # File types
        self.log(f"\n📁 FILE TYPES:")
        sorted_types = sorted(self.file_stats['by_type'].items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types[:15]:  # Top 15 types
            self.log(f"  {ext or 'no_extension'}: {count} files")
        
        # File sizes
        self.log(f"\n📏 FILE SIZES:")
        for size_cat, count in self.file_stats['by_size'].items():
            self.log(f"  {size_cat}: {count} files")
        
        # Duplicates
        self.find_duplicate_files()
        self.file_stats['duplicate_files'] = len(self.duplicates_found)
        
        self.log(f"\n🔄 DUPLICATE FILES:")
        self.log(f"Found {len(self.duplicates_found)} groups of duplicate files")
        for i, dup_group in enumerate(self.duplicates_found[:10], 1):  # Show first 10
            self.log(f"  Group {i} ({dup_group['size']} bytes):")
            for file_path in dup_group['files']:
                self.log(f"    - {file_path}")
        
        # Frontend analysis
        self.analyze_frontend_structure()
        
        # Issues summary
        self.log(f"\n⚠️ ISSUES FOUND:")
        if self.issues_found:
            for i, issue in enumerate(self.issues_found, 1):
                self.log(f"  {i}. {issue}")
        else:
            self.log("  No major issues found!")
        
        # Problematic files
        problematic_files = [
            (path, analysis) for path, analysis in self.file_analysis.items() 
            if analysis.get('issues')
        ]
        
        if problematic_files:
            self.log(f"\n🚨 PROBLEMATIC FILES ({len(problematic_files)}):")
            for path, analysis in problematic_files[:20]:  # Show first 20
                self.log(f"  {Path(path).name}:")
                for issue in analysis['issues']:
                    self.log(f"    - {issue}")
        
        # Save detailed report
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Save detailed analysis to JSON file"""
        try:
            report_file = D_LOGS / f"comprehensive_file_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'project_root': str(self.project_root),
                'statistics': self.file_stats,
                'duplicates': self.duplicates_found,
                'issues': self.issues_found,
                'frontends': self.frontends_found,
                'file_analysis': self.file_analysis
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.log(f"\n💾 Detailed report saved to: {report_file}")
            
        except Exception as e:
            self.log(f"❌ Could not save detailed report: {e}", "ERROR")
    
    def investigate_multiple_frontends(self):
        """Investigate why there are multiple frontends"""
        self.log("\n" + "=" * 80)
        self.log("🔍 INVESTIGATING MULTIPLE FRONTENDS")
        self.log("=" * 80)
        
        # Find all HTML files and web-related files
        web_files = []
        for file_path, analysis in self.file_analysis.items():
            ext = analysis.get('extension', '')
            if ext in ['.html', '.htm', '.css', '.js'] or 'web' in file_path.lower() or 'frontend' in file_path.lower():
                web_files.append((file_path, analysis))
        
        self.log(f"Found {len(web_files)} web-related files")
        
        # Group by directory
        frontend_dirs = {}
        for file_path, analysis in web_files:
            dir_path = str(Path(file_path).parent)
            if dir_path not in frontend_dirs:
                frontend_dirs[dir_path] = []
            frontend_dirs[dir_path].append((file_path, analysis))
        
        self.log(f"\nWeb files found in {len(frontend_dirs)} directories:")
        
        for dir_path, files in frontend_dirs.items():
            self.log(f"\n📁 {dir_path}:")
            
            html_files = [f for f in files if f[1].get('extension') in ['.html', '.htm']]
            css_files = [f for f in files if f[1].get('extension') == '.css']
            js_files = [f for f in files if f[1].get('extension') == '.js']
            
            self.log(f"  - HTML files: {len(html_files)}")
            self.log(f"  - CSS files: {len(css_files)}")
            self.log(f"  - JS files: {len(js_files)}")
            
            # Show HTML file details
            for file_path, analysis in html_files:
                title = analysis.get('content_analysis', {}).get('title', 'No title')
                frontend_type = analysis.get('content_analysis', {}).get('frontend_type', 'unknown')
                self.log(f"    HTML: {Path(file_path).name} - '{title}' ({frontend_type})")
        
        # Recommendations
        self.log(f"\n💡 FRONTEND ANALYSIS RECOMMENDATIONS:")
        
        if len(frontend_dirs) > 3:
            self.log("⚠️ Multiple frontend directories detected - consider consolidation")
            
        frontend_types = set()
        for frontend in self.frontends_found:
            frontend_type = frontend.get('content_analysis', {}).get('frontend_type', 'unknown')
            frontend_types.add(frontend_type)
        
        if len(frontend_types) > 2:
            self.log(f"⚠️ Multiple frontend frameworks: {list(frontend_types)}")
            self.log("   Consider standardizing on one framework")
        
        # Check for Flask/FastAPI web interfaces
        web_servers = []
        for file_path, analysis in self.file_analysis.items():
            if analysis.get('extension') == '.py':
                content_analysis = analysis.get('content_analysis', {})
                imports = content_analysis.get('imports', [])
                
                if any('flask' in imp.lower() for imp in imports):
                    web_servers.append((file_path, 'Flask'))
                elif any('fastapi' in imp.lower() for imp in imports):
                    web_servers.append((file_path, 'FastAPI'))
        
        if web_servers:
            self.log(f"\n🌐 WEB SERVERS DETECTED:")
            for server_file, server_type in web_servers:
                self.log(f"  - {server_type}: {Path(server_file).name}")
    
    def run_comprehensive_analysis(self):
        """Run complete file analysis"""
        start_time = datetime.now()
        
        self.log("🚀 Starting Comprehensive PakWheels File Analysis")
        self.log(f"Project root: {self.project_root}")
        self.log(f"Analysis logs: {D_LOGS}")
        
        # Scan all files
        self.scan_all_files()
        
        # Generate report
        self.generate_comprehensive_report()
        
        # Investigate frontends
        self.investigate_multiple_frontends()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log(f"\n✅ Analysis completed in {duration:.2f} seconds")
        self.log(f"📊 Summary: {self.file_stats['total_files']} files, {self.file_stats['problematic_files']} issues, {len(self.duplicates_found)} duplicate groups")

def main():
    """Main function"""
    print("🔍 Comprehensive PakWheels File Analysis System")
    print("This will analyze every file in the project and investigate frontend issues")
    print("Using D: drive for analysis logs and reports\n")
    
    analyzer = ComprehensiveFileAnalyzer()
    analyzer.run_comprehensive_analysis()

if __name__ == "__main__":
    main()
