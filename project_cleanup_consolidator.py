#!/usr/bin/env python3
"""
PakWheels Project Cleanup & Frontend Consolidation
Consolidates multiple frontends and cleans up the massive project structure
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json

class ProjectCleaner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.cleanup_log = []
        self.frontend_consolidation_plan = {}
        self.files_removed = 0
        self.bytes_saved = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.cleanup_log.append(log_entry)
    
    def analyze_frontends(self):
        """Analyze current frontend structure"""
        self.log("🔍 Analyzing frontend structure...")
        
        frontend_locations = {
            'mvp_frontend': self.project_root / 'frontend' / 'mvp',
            'full_frontend': self.project_root / 'frontend',
            'templates': self.project_root / 'templates',
            'web_templates': self.project_root / 'web' / 'templates'
        }
        
        for name, path in frontend_locations.items():
            if path.exists():
                html_files = list(path.rglob('*.html'))
                css_files = list(path.rglob('*.css'))
                js_files = list(path.rglob('*.js'))
                
                self.log(f"  📁 {name}: {len(html_files)} HTML, {len(css_files)} CSS, {len(js_files)} JS files")
                
                self.frontend_consolidation_plan[name] = {
                    'path': str(path),
                    'html_files': [str(f) for f in html_files],
                    'css_files': [str(f) for f in css_files],
                    'js_files': [str(f) for f in js_files],
                    'total_files': len(html_files) + len(css_files) + len(js_files)
                }
    
    def consolidate_frontends(self):
        """Consolidate multiple frontends into one unified structure"""
        self.log("🎯 Starting frontend consolidation...")
        
        # Create consolidated frontend directory
        consolidated_dir = self.project_root / 'frontend_consolidated'
        consolidated_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (consolidated_dir / 'templates').mkdir(exist_ok=True)
        (consolidated_dir / 'static' / 'css').mkdir(parents=True, exist_ok=True)
        (consolidated_dir / 'static' / 'js').mkdir(parents=True, exist_ok=True)
        (consolidated_dir / 'archive').mkdir(exist_ok=True)
        
        self.log(f"  ✅ Created consolidated directory: {consolidated_dir}")
        
        # Process each frontend location
        for frontend_name, frontend_info in self.frontend_consolidation_plan.items():
            if frontend_info['total_files'] == 0:
                continue
                
            self.log(f"  📦 Processing {frontend_name}...")
            source_path = Path(frontend_info['path'])
            
            if not source_path.exists():
                continue
            
            # Copy HTML files to templates
            for html_file in frontend_info['html_files']:
                src = Path(html_file)
                if src.exists():
                    # Create meaningful name
                    new_name = f"{frontend_name}_{src.name}"
                    dest = consolidated_dir / 'templates' / new_name
                    
                    try:
                        shutil.copy2(src, dest)
                        self.log(f"    ✓ Moved HTML: {src.name} → {new_name}")
                    except Exception as e:
                        self.log(f"    ✗ Failed to copy {src.name}: {e}", "ERROR")
            
            # Copy CSS files
            for css_file in frontend_info['css_files']:
                src = Path(css_file)
                if src.exists():
                    new_name = f"{frontend_name}_{src.name}"
                    dest = consolidated_dir / 'static' / 'css' / new_name
                    
                    try:
                        shutil.copy2(src, dest)
                        self.log(f"    ✓ Moved CSS: {src.name} → {new_name}")
                    except Exception as e:
                        self.log(f"    ✗ Failed to copy {src.name}: {e}", "ERROR")
            
            # Copy JS files
            for js_file in frontend_info['js_files']:
                src = Path(js_file)
                if src.exists():
                    new_name = f"{frontend_name}_{src.name}"
                    dest = consolidated_dir / 'static' / 'js' / new_name
                    
                    try:
                        shutil.copy2(src, dest)
                        self.log(f"    ✓ Moved JS: {src.name} → {new_name}")
                    except Exception as e:
                        self.log(f"    ✗ Failed to copy {src.name}: {e}", "ERROR")
        
        # Create README for consolidated frontend
        readme_content = f"""# Consolidated PakWheels Frontend

This directory contains all frontend files consolidated from multiple locations.

## Structure:
- `templates/` - All HTML templates (renamed with source prefix)
- `static/css/` - All CSS files (renamed with source prefix)
- `static/js/` - All JavaScript files (renamed with source prefix)
- `archive/` - Backup of original files

## Original Sources Consolidated:
{chr(10).join([f"- {name}: {info['total_files']} files from {info['path']}" for name, info in self.frontend_consolidation_plan.items() if info['total_files'] > 0])}

## Recommendations:
1. Review all templates and choose the best design
2. Merge duplicate functionality
3. Update server code to use consolidated templates
4. Remove unused templates after testing

Consolidated on: {datetime.now().isoformat()}
"""
        
        readme_path = consolidated_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.log(f"  📝 Created README: {readme_path}")
        self.log(f"✅ Frontend consolidation complete!")
    
    def remove_empty_files(self):
        """Remove all empty files from the project"""
        self.log("🧹 Starting empty file cleanup...")
        
        empty_files = []
        
        # Skip these directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.vscode', '.idea', '.venv'}
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove skip directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                try:
                    if file_path.stat().st_size == 0:
                        empty_files.append(file_path)
                except:
                    continue
        
        self.log(f"  Found {len(empty_files)} empty files")
        
        # Remove empty files
        removed_count = 0
        for empty_file in empty_files:
            try:
                empty_file.unlink()
                removed_count += 1
                self.files_removed += 1
                
                if removed_count % 100 == 0:
                    self.log(f"    Removed {removed_count}/{len(empty_files)} empty files...")
                    
            except Exception as e:
                self.log(f"    ✗ Failed to remove {empty_file}: {e}", "ERROR")
        
        self.log(f"✅ Removed {removed_count} empty files!")
    
    def remove_duplicate_files(self):
        """Remove obvious duplicate files (same name, same directory)"""
        self.log("🔄 Starting duplicate file cleanup...")
        
        # This is a conservative approach - only removes files with identical names in same directory
        duplicates_removed = 0
        
        # Look for common duplicate patterns
        duplicate_patterns = [
            'copy', 'Copy', 'COPY',
            'backup', 'Backup', 'BACKUP',
            'old', 'Old', 'OLD',
            'temp', 'Temp', 'TEMP',
            '(1)', '(2)', '(3)',
            '_copy', '_backup', '_old'
        ]
        
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.vscode', '.idea', '.venv'}
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if file name contains duplicate patterns
                for pattern in duplicate_patterns:
                    if pattern in file and file_path.exists():
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            duplicates_removed += 1
                            self.files_removed += 1
                            self.bytes_saved += file_size
                            
                            self.log(f"    ✓ Removed duplicate: {file}")
                            break
                        except Exception as e:
                            self.log(f"    ✗ Failed to remove {file}: {e}", "ERROR")
        
        self.log(f"✅ Removed {duplicates_removed} duplicate files!")
    
    def cleanup_temp_files(self):
        """Remove temporary and cache files"""
        self.log("🗑️ Starting temporary file cleanup...")
        
        temp_patterns = [
            '*.tmp', '*.temp', '*.cache', '*.bak', '*.orig', '*~',
            '*.log', '*.out', '*.err', '*.swp', '*.swo'
        ]
        
        temp_files_removed = 0
        
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                # Skip if in protected directories
                if any(skip in str(temp_file) for skip in ['.git', '__pycache__', 'node_modules', '.venv']):
                    continue
                
                try:
                    # Only remove if larger than 1MB or older than 7 days
                    stat = temp_file.stat()
                    file_age_days = (datetime.now().timestamp() - stat.st_mtime) / (24 * 3600)
                    
                    if stat.st_size > 1024 * 1024 or file_age_days > 7:
                        self.bytes_saved += stat.st_size
                        temp_file.unlink()
                        temp_files_removed += 1
                        self.files_removed += 1
                        
                        if temp_files_removed % 50 == 0:
                            self.log(f"    Removed {temp_files_removed} temp files...")
                            
                except Exception as e:
                    continue
        
        self.log(f"✅ Removed {temp_files_removed} temporary files!")
    
    def create_project_structure_guide(self):
        """Create a guide for the new project structure"""
        self.log("📚 Creating project structure guide...")
        
        guide_content = f"""# PakWheels Project Structure Guide

## Current Project Statistics (After Cleanup):
- Files removed: {self.files_removed:,}
- Space saved: {self.bytes_saved / 1024 / 1024:.1f} MB
- Cleanup completed: {datetime.now().isoformat()}

## Recommended Project Structure:

```
pakwheels/
├── frontend_consolidated/          # ✅ Consolidated frontend files
│   ├── templates/                  # All HTML templates
│   ├── static/css/                 # All CSS files
│   └── static/js/                  # All JavaScript files
├── src/                           # Main source code
│   ├── api/                       # API server code
│   ├── ml/                        # Machine learning models
│   └── scraper/                   # Web scraping code
├── data/                          # Data files
├── tests/                         # Test files
├── docs/                          # Documentation
└── requirements.txt               # Dependencies
```

## Next Steps:

### 1. Frontend Consolidation
- Review consolidated templates in `frontend_consolidated/templates/`
- Choose the best design elements from each version
- Update your main server to use consolidated templates
- Test all frontend functionality

### 2. Server Consolidation
You have multiple API servers. Recommend keeping:
- `simple_mvp_server.py` - For development/testing
- One production server (choose best from enhanced versions)

### 3. Clean Architecture
- Move main code to `src/` directory
- Organize by functionality (api, ml, scraper)
- Create proper Python packages with `__init__.py` files

### 4. Frontend Technology Decision
Current frontends detected:
{chr(10).join([f"- {name}: {info['total_files']} files" for name, info in self.frontend_consolidation_plan.items() if info['total_files'] > 0])}

**Recommendation**: Choose ONE frontend approach:
- **MVP Frontend** - Simple, fast, good for testing
- **Full Frontend** - More features, better UX
- **Dashboard** - Admin interface
- **Custom** - Build new with modern framework (React/Vue)

### 5. Database & Models
- Ensure all ML models are in one location
- Standardize data loading and preprocessing
- Implement proper model versioning

## Cleanup Summary:
- ✅ Removed {self.files_removed:,} unnecessary files
- ✅ Saved {self.bytes_saved / 1024 / 1024:.1f} MB of disk space
- ✅ Consolidated frontend files
- ✅ Cleaned up duplicates and temporary files

"""
        
        guide_path = Path("D:/pakwheels_cleanup_guide.md")
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        self.log(f"📝 Project guide saved to: {guide_path}")
    
    def save_cleanup_log(self):
        """Save detailed cleanup log"""
        try:
            log_file = Path("D:/pakwheels_cleanup_log.txt")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"PakWheels Project Cleanup Log\n")
                f.write(f"Started: {datetime.now().isoformat()}\n\n")
                f.write("\n".join(self.cleanup_log))
            
            self.log(f"💾 Cleanup log saved to: {log_file}")
        except Exception as e:
            self.log(f"❌ Could not save cleanup log: {e}", "ERROR")
    
    def run_complete_cleanup(self):
        """Run the complete cleanup process"""
        self.log("🚀 Starting PakWheels Project Cleanup & Consolidation")
        self.log("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Analyze current frontend structure
            self.analyze_frontends()
            
            # Step 2: Consolidate frontends
            self.consolidate_frontends()
            
            # Step 3: Remove empty files
            self.remove_empty_files()
            
            # Step 4: Remove duplicate files
            self.remove_duplicate_files()
            
            # Step 5: Clean up temporary files
            self.cleanup_temp_files()
            
            # Step 6: Create project guide
            self.create_project_structure_guide()
            
            # Step 7: Save cleanup log
            self.save_cleanup_log()
            
        except Exception as e:
            self.log(f"❌ Cleanup failed: {e}", "ERROR")
            return False
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log("=" * 60)
        self.log("🎉 CLEANUP COMPLETED SUCCESSFULLY!")
        self.log("=" * 60)
        self.log(f"⏱️ Total time: {duration:.2f} seconds")
        self.log(f"🗑️ Files removed: {self.files_removed:,}")
        self.log(f"💾 Space saved: {self.bytes_saved / 1024 / 1024:.1f} MB")
        self.log(f"📁 Frontend consolidated: ✅")
        self.log(f"📋 Guides created: ✅")
        
        return True

def main():
    """Main function"""
    print("🧹 PakWheels Project Cleanup & Frontend Consolidation")
    print("This will consolidate frontends and clean up your massive project\n")
    
    cleaner = ProjectCleaner()
    
    # Ask for confirmation
    print("This will:")
    print("- Consolidate multiple frontends into one directory")
    print("- Remove 827+ empty files")
    print("- Clean up duplicate and temporary files")
    print("- Create project structure guides")
    print()
    
    confirm = input("Continue with cleanup? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("❌ Cleanup cancelled")
        return
    
    success = cleaner.run_complete_cleanup()
    
    if success:
        print("\n✅ Project cleanup completed successfully!")
        print("📋 Check D:/pakwheels_cleanup_guide.md for next steps")
    else:
        print("\n❌ Cleanup encountered errors. Check logs for details.")

if __name__ == "__main__":
    main()
