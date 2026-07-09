#!/usr/bin/env python3
"""
Ultra Fast File Scanner
Lightning fast analysis of ALL project files
Optimized for speed - can scan thousands of files in seconds
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import hashlib
import mimetypes

class UltraFastScanner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'extensions': Counter(),
            'directories': 0
        }
        self.frontends = []
        self.duplicates = []
        self.issues = []
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def quick_file_hash(self, file_path, max_bytes=8192):
        """Super fast file hash - only reads first 8KB"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read(max_bytes)).hexdigest()[:8]
        except:
            return "error"
    
    def lightning_scan(self):
        """Lightning fast scan of entire project"""
        self.log("🚀 Starting ULTRA FAST scan...")
        start_time = datetime.now()
        
        # Skip these for speed
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.vscode', '.idea'}
        file_hashes = defaultdict(list)
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            self.stats['directories'] += 1
            
            for file in files:
                file_path = Path(root) / file
                self.stats['total_files'] += 1
                
                # Quick stats
                try:
                    size = file_path.stat().st_size
                    self.stats['total_size'] += size
                    ext = file_path.suffix.lower()
                    self.stats['extensions'][ext or 'no_ext'] += 1
                    
                    # Quick duplicate check (first 8KB only)
                    if size > 0:
                        quick_hash = self.quick_file_hash(file_path)
                        file_hashes[quick_hash].append(str(file_path))
                    
                    # Quick frontend detection
                    if ext in ['.html', '.htm']:
                        self.frontends.append({
                            'path': str(file_path),
                            'name': file.lower(),
                            'size': size
                        })
                    
                    # Quick issue detection
                    if size == 0:
                        self.issues.append(f"Empty: {file}")
                    elif size > 100 * 1024 * 1024:  # >100MB
                        self.issues.append(f"Huge: {file} ({size/1024/1024:.0f}MB)")
                    elif file.endswith(('.tmp', '.bak', '.old')):
                        self.issues.append(f"Temp: {file}")
                        
                except:
                    self.issues.append(f"Access error: {file}")
                
                # Progress update every 1000 files
                if self.stats['total_files'] % 1000 == 0:
                    self.log(f"  Scanned {self.stats['total_files']} files...")
        
        # Find duplicates
        for hash_val, paths in file_hashes.items():
            if len(paths) > 1 and hash_val != "error":
                self.duplicates.append({
                    'hash': hash_val,
                    'count': len(paths),
                    'paths': paths[:10]  # Limit to first 10
                })
        
        duration = (datetime.now() - start_time).total_seconds()
        self.log(f"✅ Scanned {self.stats['total_files']} files in {duration:.2f} seconds!")
        self.log(f"   Speed: {self.stats['total_files']/duration:.0f} files/second")
    
    def analyze_frontends(self):
        """Quick frontend analysis"""
        if not self.frontends:
            self.log("📱 No HTML files found")
            return
        
        self.log(f"📱 FRONTEND ANALYSIS: {len(self.frontends)} HTML files found")
        
        # Group by directory
        by_dir = defaultdict(list)
        for frontend in self.frontends:
            dir_path = str(Path(frontend['path']).parent)
            by_dir[dir_path].append(frontend)
        
        self.log(f"   Found in {len(by_dir)} directories:")
        for dir_path, files in by_dir.items():
            self.log(f"   📁 {dir_path}: {len(files)} HTML files")
            for f in files[:3]:  # Show first 3 files
                self.log(f"      - {Path(f['path']).name}")
        
        # Quick framework detection
        frameworks = set()
        for frontend in self.frontends:
            name = frontend['name']
            if 'bootstrap' in name or 'bs' in name:
                frameworks.add('Bootstrap')
            elif 'vue' in name:
                frameworks.add('Vue')
            elif 'react' in name:
                frameworks.add('React')
            elif 'angular' in name:
                frameworks.add('Angular')
            elif 'admin' in name:
                frameworks.add('Admin')
            elif 'dashboard' in name:
                frameworks.add('Dashboard')
        
        if frameworks:
            self.log(f"   🔧 Detected frameworks: {', '.join(frameworks)}")
        
        if len(by_dir) > 1:
            self.log(f"   ⚠️ Multiple frontend locations detected!")
            self.log(f"   💡 Possible reasons:")
            self.log(f"      - Different UI versions (MVP vs Full)")
            self.log(f"      - Admin vs User interfaces")
            self.log(f"      - Legacy code not cleaned up")
    
    def find_web_servers(self):
        """Quick web server detection"""
        servers = []
        
        # Quick scan of .py files for web frameworks
        for ext_count in [('.py', 'Python')]:
            if ext_count[0] in self.stats['extensions']:
                # Just check common server files
                common_files = [
                    'app.py', 'main.py', 'server.py', 'api.py', 
                    'web.py', 'flask_app.py', 'fastapi_app.py'
                ]
                
                for root, dirs, files in os.walk(self.project_root):
                    if any(skip in root for skip in ['.git', '__pycache__']):
                        continue
                    
                    for file in files:
                        if file.lower() in common_files or 'server' in file.lower():
                            servers.append(f"{Path(root).name}/{file}")
        
        if servers:
            self.log(f"🌐 Potential web servers found:")
            for server in servers[:10]:  # Show first 10
                self.log(f"   - {server}")
    
    def generate_ultra_fast_report(self):
        """Generate lightning fast report"""
        self.log(f"\n⚡ ULTRA FAST ANALYSIS REPORT")
        self.log(f"=" * 50)
        
        # File statistics
        self.log(f"📊 PROJECT STATISTICS:")
        self.log(f"   Total files: {self.stats['total_files']:,}")
        self.log(f"   Total size: {self.stats['total_size']/1024/1024:.1f} MB")
        self.log(f"   Directories: {self.stats['directories']:,}")
        
        # Top file types
        self.log(f"\n📁 TOP FILE TYPES:")
        for ext, count in self.stats['extensions'].most_common(15):
            percentage = (count / self.stats['total_files']) * 100
            self.log(f"   {ext or 'no_ext'}: {count:,} files ({percentage:.1f}%)")
        
        # Quick duplicate analysis
        if self.duplicates:
            self.log(f"\n🔄 POTENTIAL DUPLICATES: {len(self.duplicates)} groups")
            for dup in self.duplicates[:5]:  # Show first 5 groups
                self.log(f"   {dup['count']} files with hash {dup['hash']}:")
                for path in dup['paths'][:3]:  # Show first 3 paths
                    self.log(f"      - {Path(path).name}")
        
        # Frontend analysis
        self.analyze_frontends()
        
        # Web servers
        self.find_web_servers()
        
        # Issues summary
        if self.issues:
            self.log(f"\n⚠️ ISSUES FOUND: {len(self.issues)}")
            issue_types = Counter()
            for issue in self.issues:
                issue_type = issue.split(':')[0]
                issue_types[issue_type] += 1
            
            for issue_type, count in issue_types.most_common():
                self.log(f"   {issue_type}: {count} files")
        else:
            self.log(f"\n✅ No major issues detected!")
        
        # Quick recommendations
        self.log(f"\n💡 QUICK RECOMMENDATIONS:")
        
        # Python project recommendations
        if '.py' in self.stats['extensions']:
            py_count = self.stats['extensions']['.py']
            self.log(f"   🐍 Python project with {py_count} files")
            
            if py_count > 50:
                self.log(f"   📦 Consider organizing into packages")
            
            if self.stats['extensions'].get('.pyc', 0) > 0:
                self.log(f"   🧹 Remove .pyc files (add to .gitignore)")
        
        # Frontend recommendations
        if len(self.frontends) > 5:
            self.log(f"   🌐 Multiple HTML files - consider frontend framework")
        
        # File cleanup recommendations
        temp_files = sum(1 for issue in self.issues if issue.startswith('Temp:'))
        if temp_files > 0:
            self.log(f"   🧹 Clean up {temp_files} temporary files")
        
        empty_files = sum(1 for issue in self.issues if issue.startswith('Empty:'))
        if empty_files > 0:
            self.log(f"   📄 Remove {empty_files} empty files")
        
        # Save quick summary
        try:
            summary_file = Path("D:/pakwheels_ultra_fast_summary.txt")
            with open(summary_file, 'w') as f:
                f.write(f"PakWheels Ultra Fast Scan Summary\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write(f"Total files: {self.stats['total_files']:,}\n")
                f.write(f"Total size: {self.stats['total_size']/1024/1024:.1f} MB\n")
                f.write(f"HTML files: {len(self.frontends)}\n")
                f.write(f"Issues found: {len(self.issues)}\n")
                f.write(f"Duplicate groups: {len(self.duplicates)}\n")
            
            self.log(f"\n💾 Summary saved to: {summary_file}")
        except:
            self.log(f"\n❌ Could not save summary file")

def main():
    """Main function"""
    print("⚡ ULTRA FAST PakWheels Scanner")
    print("Lightning speed analysis for large projects\n")
    
    scanner = UltraFastScanner()
    
    total_start = datetime.now()
    
    # Lightning scan
    scanner.lightning_scan()
    
    # Quick analysis
    scanner.generate_ultra_fast_report()
    
    total_duration = (datetime.now() - total_start).total_seconds()
    print(f"\n🏁 COMPLETE! Total time: {total_duration:.2f} seconds")

if __name__ == "__main__":
    main()
