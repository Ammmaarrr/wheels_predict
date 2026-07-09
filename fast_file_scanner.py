#!/usr/bin/env python3
"""
Fast File Scanner and Frontend Analyzer
Quick analysis of all files to identify issues and multiple frontends
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import mimetypes

# Use D: drive for logs
D_LOGS = Path("D:/pakwheels_analysis_logs")
D_LOGS.mkdir(exist_ok=True)

class FastFileScanner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.files_by_type = defaultdict(list)
        self.frontends_found = []
        self.issues = []
        self.total_files = 0
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def quick_scan(self):
        """Quick scan of all files"""
        self.log("🔍 Starting fast file scan...")
        
        # Skip these directories for speed
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.vscode', '.idea', '.env'}
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove skip directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                self.total_files += 1
                
                # Categorize by extension
                ext = file_path.suffix.lower()
                self.files_by_type[ext or 'no_extension'].append(str(file_path))
                
                # Check for frontend files
                if ext in ['.html', '.htm']:
                    self.analyze_html_file(file_path)
                elif 'web' in str(file_path).lower() or 'frontend' in str(file_path).lower():
                    self.files_by_type['web_related'].append(str(file_path))
                
                # Check for issues
                self.check_file_issues(file_path)
        
        self.log(f"✅ Scanned {self.total_files} files")
    
    def analyze_html_file(self, file_path):
        """Quick HTML analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract basic info
            title = "No title"
            if '<title>' in content:
                start = content.find('<title>') + 7
                end = content.find('</title>', start)
                if end > start:
                    title = content[start:end].strip()
            
            # Determine framework
            framework = 'basic'
            if 'bootstrap' in content.lower():
                framework = 'bootstrap'
            elif 'vue' in content.lower():
                framework = 'vue'
            elif 'react' in content.lower():
                framework = 'react'
            elif 'angular' in content.lower():
                framework = 'angular'
            
            self.frontends_found.append({
                'path': str(file_path),
                'title': title,
                'framework': framework,
                'size': file_path.stat().st_size
            })
            
        except Exception as e:
            self.issues.append(f"Error reading HTML file {file_path}: {e}")
    
    def check_file_issues(self, file_path):
        """Check for common issues"""
        try:
            # Check file size
            size = file_path.stat().st_size
            
            # Very large files (>50MB)
            if size > 50 * 1024 * 1024:
                self.issues.append(f"Very large file: {file_path} ({size/1024/1024:.1f}MB)")
            
            # Empty files
            if size == 0:
                self.issues.append(f"Empty file: {file_path}")
            
            # Temporary/backup files
            if any(file_path.name.endswith(ext) for ext in ['.tmp', '.bak', '.old', '.orig', '~']):
                self.issues.append(f"Temporary/backup file: {file_path}")
            
            # Log files
            if file_path.suffix.lower() == '.log' and size > 10 * 1024 * 1024:  # >10MB
                self.issues.append(f"Large log file: {file_path} ({size/1024/1024:.1f}MB)")
                
        except Exception:
            pass  # Skip if can't access file
    
    def find_duplicate_names(self):
        """Find files with same names in different directories"""
        name_to_paths = defaultdict(list)
        
        for file_list in self.files_by_type.values():
            for file_path in file_list:
                name = Path(file_path).name
                name_to_paths[name].append(file_path)
        
        duplicates = []
        for name, paths in name_to_paths.items():
            if len(paths) > 1:
                duplicates.append({'name': name, 'paths': paths})
        
        return duplicates
    
    def analyze_frontends(self):
        """Analyze frontend structure"""
        self.log(f"\n📱 FRONTEND ANALYSIS:")
        self.log(f"Found {len(self.frontends_found)} HTML files")
        
        if not self.frontends_found:
            self.log("No HTML files found")
            return
        
        # Group by framework
        by_framework = defaultdict(list)
        for frontend in self.frontends_found:
            by_framework[frontend['framework']].append(frontend)
        
        for framework, files in by_framework.items():
            self.log(f"\n{framework.upper()} Frontend ({len(files)} files):")
            for file_info in files:
                self.log(f"  - {Path(file_info['path']).name}")
                self.log(f"    Title: {file_info['title']}")
                self.log(f"    Path: {file_info['path']}")
        
        # Check for multiple frontend issue
        if len(by_framework) > 2:
            issue = f"Multiple frontend frameworks detected: {list(by_framework.keys())}"
            self.issues.append(issue)
            self.log(f"\n⚠️ {issue}")
            
            self.log(f"\n💡 RECOMMENDATIONS:")
            self.log(f"   - Consider standardizing on one frontend framework")
            self.log(f"   - Remove unused frontend implementations")
            self.log(f"   - Consolidate similar functionality")
    
    def find_web_servers(self):
        """Find web server implementations"""
        web_servers = []
        
        # Check Python files for web frameworks
        for file_path in self.files_by_type.get('.py', []):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if 'from flask import' in content or 'import flask' in content:
                    web_servers.append((file_path, 'Flask'))
                elif 'from fastapi import' in content or 'import fastapi' in content:
                    web_servers.append((file_path, 'FastAPI'))
                elif 'from django' in content:
                    web_servers.append((file_path, 'Django'))
                    
            except Exception:
                continue
        
        if web_servers:
            self.log(f"\n🌐 WEB SERVERS FOUND:")
            for server_file, server_type in web_servers:
                self.log(f"  - {server_type}: {Path(server_file).name}")
        
        return web_servers
    
    def generate_quick_report(self):
        """Generate quick analysis report"""
        self.log(f"\n📊 QUICK FILE ANALYSIS REPORT")
        self.log(f"=" * 50)
        
        # File statistics
        self.log(f"Total files: {self.total_files}")
        
        # Top file types
        self.log(f"\n📁 TOP FILE TYPES:")
        sorted_types = sorted(self.files_by_type.items(), key=lambda x: len(x[1]), reverse=True)
        for ext, files in sorted_types[:10]:
            self.log(f"  {ext}: {len(files)} files")
        
        # Find duplicates
        duplicates = self.find_duplicate_names()
        if duplicates:
            self.log(f"\n🔄 DUPLICATE FILE NAMES ({len(duplicates)}):")
            for dup in duplicates[:10]:  # Show first 10
                self.log(f"  {dup['name']}: {len(dup['paths'])} copies")
                for path in dup['paths']:
                    self.log(f"    - {path}")
        
        # Analyze frontends
        self.analyze_frontends()
        
        # Find web servers
        web_servers = self.find_web_servers()
        
        # Issues
        if self.issues:
            self.log(f"\n⚠️ ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues[:20], 1):  # Show first 20
                self.log(f"  {i}. {issue}")
        else:
            self.log(f"\n✅ No major issues found!")
        
        # Frontend investigation
        if len(self.frontends_found) > 1:
            self.log(f"\n🔍 FRONTEND INVESTIGATION:")
            self.log(f"Multiple frontend files detected - investigating why...")
            
            # Group by directory
            dirs = defaultdict(list)
            for frontend in self.frontends_found:
                dir_path = str(Path(frontend['path']).parent)
                dirs[dir_path].append(frontend)
            
            self.log(f"Frontend files found in {len(dirs)} directories:")
            for dir_path, files in dirs.items():
                self.log(f"  📁 {dir_path}: {len(files)} HTML files")
            
            if len(dirs) > 1:
                self.log(f"\n💡 LIKELY REASONS FOR MULTIPLE FRONTENDS:")
                self.log(f"   1. Different development phases (MVP vs Production)")
                self.log(f"   2. A/B testing different designs")
                self.log(f"   3. Admin vs User interfaces")
                self.log(f"   4. Legacy code not yet cleaned up")
                self.log(f"   5. Different developers working on separate features")
        
        # Save summary
        self.save_summary()
    
    def save_summary(self):
        """Save analysis summary"""
        try:
            report_file = D_LOGS / f"fast_file_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_files': self.total_files,
                'files_by_type': {k: len(v) for k, v in self.files_by_type.items()},
                'frontends_found': self.frontends_found,
                'issues_count': len(self.issues),
                'issues': self.issues[:50]  # Limit to first 50 issues
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            self.log(f"\n💾 Summary saved to: {report_file}")
            
        except Exception as e:
            self.log(f"❌ Could not save summary: {e}")
    
    def run_fast_analysis(self):
        """Run complete fast analysis"""
        start_time = datetime.now()
        
        self.log("🚀 Starting Fast PakWheels File Analysis")
        
        # Quick scan
        self.quick_scan()
        
        # Generate report
        self.generate_quick_report()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log(f"\n✅ Fast analysis completed in {duration:.2f} seconds")

def main():
    """Main function"""
    print("⚡ Fast PakWheels File Scanner")
    print("Quick analysis of all files and frontend investigation\n")
    
    scanner = FastFileScanner()
    scanner.run_fast_analysis()

if __name__ == "__main__":
    main()
