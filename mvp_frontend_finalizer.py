#!/usr/bin/env python3
"""
MVP Frontend Finalization Script
Sets up clean MVP frontend structure and removes other frontend versions
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json

class MVPFrontendFinalizer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.log_entries = []
        self.files_processed = 0
        self.space_saved = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.log_entries.append(log_entry)
    
    def create_final_mvp_structure(self):
        """Create the final MVP frontend structure"""
        self.log("🎯 Creating final MVP frontend structure...")
        
        # Create the final MVP directory
        mvp_final = self.project_root / 'frontend_mvp'
        mvp_final.mkdir(exist_ok=True)
        
        # Create subdirectories
        (mvp_final / 'templates').mkdir(exist_ok=True)
        (mvp_final / 'static' / 'css').mkdir(parents=True, exist_ok=True)
        (mvp_final / 'static' / 'js').mkdir(parents=True, exist_ok=True)
        (mvp_final / 'static' / 'images').mkdir(parents=True, exist_ok=True)
        
        self.log(f"  ✅ Created MVP structure: {mvp_final}")
        
        # Copy MVP files from consolidated directory
        consolidated_dir = self.project_root / 'frontend_consolidated'
        if consolidated_dir.exists():
            self.log("  📋 Copying MVP files from consolidated directory...")
            
            # Copy MVP HTML templates
            templates_dir = consolidated_dir / 'templates'
            if templates_dir.exists():
                for html_file in templates_dir.glob('mvp_frontend_*.html'):
                    # Remove the mvp_frontend_ prefix
                    new_name = html_file.name.replace('mvp_frontend_', '')
                    dest = mvp_final / 'templates' / new_name
                    shutil.copy2(html_file, dest)
                    self.log(f"    ✓ Copied: {new_name}")
                    self.files_processed += 1
            
            # Copy MVP CSS files
            css_dir = consolidated_dir / 'static' / 'css'
            if css_dir.exists():
                for css_file in css_dir.glob('mvp_frontend_*.css'):
                    new_name = css_file.name.replace('mvp_frontend_', '')
                    dest = mvp_final / 'static' / 'css' / new_name
                    shutil.copy2(css_file, dest)
                    self.log(f"    ✓ Copied CSS: {new_name}")
                    self.files_processed += 1
            
            # Copy essential JS files (not all 33K+)
            js_dir = consolidated_dir / 'static' / 'js'
            if js_dir.exists():
                essential_js = [
                    'mvp_frontend_App.js',
                    'mvp_frontend_index.js'
                ]
                
                for js_pattern in essential_js:
                    for js_file in js_dir.glob(js_pattern):
                        new_name = js_file.name.replace('mvp_frontend_', '')
                        dest = mvp_final / 'static' / 'js' / new_name
                        shutil.copy2(js_file, dest)
                        self.log(f"    ✓ Copied JS: {new_name}")
                        self.files_processed += 1
        
        # Create a simple main template if none exists
        main_template = mvp_final / 'templates' / 'index.html'
        if not main_template.exists():
            self.create_simple_mvp_template(main_template)
        
        return mvp_final
    
    def create_simple_mvp_template(self, template_path):
        """Create a simple MVP template"""
        self.log("  🎨 Creating simple MVP template...")
        
        template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PakWheels MVP - Car Price Prediction</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 90%;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
            font-size: 2rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #555;
            font-weight: 500;
        }
        
        input, select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .result {
            margin-top: 2rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
            display: none;
        }
        
        .price {
            font-size: 2rem;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 0.5rem;
        }
        
        .confidence {
            color: #666;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 PakWheels MVP</h1>
        <h2 style="text-align: center; color: #666; margin-bottom: 2rem;">Car Price Prediction</h2>
        
        <form id="predictionForm">
            <div class="form-group">
                <label for="brand">Brand *</label>
                <select id="brand" name="brand" required>
                    <option value="">Select Brand</option>
                    <option value="Toyota">Toyota</option>
                    <option value="Honda">Honda</option>
                    <option value="Suzuki">Suzuki</option>
                    <option value="BMW">BMW</option>
                    <option value="Mercedes">Mercedes</option>
                    <option value="Audi">Audi</option>
                    <option value="Nissan">Nissan</option>
                    <option value="Hyundai">Hyundai</option>
                    <option value="KIA">KIA</option>
                    <option value="Mitsubishi">Mitsubishi</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="model">Model</label>
                <input type="text" id="model" name="model" placeholder="e.g., Corolla, Civic">
            </div>
            
            <div class="form-group">
                <label for="year">Year</label>
                <input type="number" id="year" name="year" min="2000" max="2025" placeholder="2020">
            </div>
            
            <div class="form-group">
                <label for="mileage">Mileage (km)</label>
                <input type="number" id="mileage" name="mileage" min="0" placeholder="50000">
            </div>
            
            <div class="form-group">
                <label for="engine_capacity">Engine Capacity (L)</label>
                <input type="number" id="engine_capacity" name="engine_capacity" step="0.1" min="0.5" max="8.0" placeholder="1.8">
            </div>
            
            <button type="submit" class="btn">Get Price Prediction</button>
        </form>
        
        <div class="loading" id="loading">
            <p>🔄 Calculating price prediction...</p>
        </div>
        
        <div class="result" id="result">
            <div class="price" id="predictedPrice">PKR 0</div>
            <div class="confidence" id="confidence">Confidence: 0%</div>
        </div>
    </div>

    <script>
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const form = this;
            
            // Show loading
            loading.style.display = 'block';
            result.style.display = 'none';
            
            // Collect form data
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (value) {
                    data[key] = isNaN(value) ? value : Number(value);
                }
            }
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const prediction = await response.json();
                    
                    // Display result
                    document.getElementById('predictedPrice').textContent = 
                        `PKR ${prediction.predicted_price.toLocaleString()}`;
                    document.getElementById('confidence').textContent = 
                        `Confidence: ${(prediction.confidence * 100).toFixed(0)}%`;
                    
                    result.style.display = 'block';
                } else {
                    alert('Error getting prediction. Please try again.');
                }
            } catch (error) {
                alert('Network error. Please check your connection.');
            } finally {
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.log(f"    ✅ Created MVP template: {template_path.name}")
    
    def update_server_for_mvp(self):
        """Update server configuration to use MVP frontend"""
        self.log("🔧 Looking for server files to update...")
        
        # Find server files that might need updating
        server_files = [
            'simple_mvp_server.py',
            'mvp_fastapi_server.py',
            'web_interface.py'
        ]
        
        for server_file in server_files:
            server_path = self.project_root / server_file
            if server_path.exists():
                self.log(f"  📝 Found server file: {server_file}")
                # We'll note this but not modify automatically to avoid breaking changes
        
        # Create a server configuration note
        config_note = self.project_root / 'frontend_mvp' / 'SERVER_CONFIG.md'
        config_content = f"""# MVP Frontend Server Configuration

## Update Your Server

To use the new MVP frontend, update your server files to serve templates from:
- **Template directory**: `frontend_mvp/templates/`
- **Static directory**: `frontend_mvp/static/`

## Example FastAPI Configuration:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="frontend_mvp/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="frontend_mvp/templates")
```

## Example Flask Configuration:

```python
from flask import Flask, render_template

app = Flask(__name__, 
           template_folder='frontend_mvp/templates',
           static_folder='frontend_mvp/static')
```

## Files to Update:
{chr(10).join([f"- {f}" for f in server_files if (self.project_root / f).exists()])}

Generated: {datetime.now().isoformat()}
"""
        
        with open(config_note, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        self.log(f"  📝 Created server config guide: SERVER_CONFIG.md")
    
    def clean_old_frontends(self):
        """Clean up old frontend directories"""
        self.log("🧹 Cleaning up old frontend directories...")
        
        # Directories to clean up
        cleanup_dirs = [
            'frontend/mvp',
            'frontend/public',
            'templates',
            'web/templates'
        ]
        
        for cleanup_dir in cleanup_dirs:
            dir_path = self.project_root / cleanup_dir
            if dir_path.exists() and dir_path.is_dir():
                try:
                    # Calculate space before deletion
                    dir_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                    self.space_saved += dir_size
                    
                    shutil.rmtree(dir_path)
                    self.log(f"  ✓ Removed: {cleanup_dir}")
                except Exception as e:
                    self.log(f"  ✗ Failed to remove {cleanup_dir}: {e}", "ERROR")
        
        # Also clean up the consolidated directory after extraction
        consolidated_dir = self.project_root / 'frontend_consolidated'
        if consolidated_dir.exists():
            try:
                dir_size = sum(f.stat().st_size for f in consolidated_dir.rglob('*') if f.is_file())
                self.space_saved += dir_size
                shutil.rmtree(consolidated_dir)
                self.log(f"  ✓ Removed consolidated directory (no longer needed)")
            except Exception as e:
                self.log(f"  ✗ Failed to remove consolidated directory: {e}", "ERROR")
    
    def create_mvp_readme(self, mvp_dir):
        """Create README for MVP frontend"""
        readme_content = f"""# PakWheels MVP Frontend

Clean, simple, and fast frontend for car price prediction.

## 🎯 MVP Features:
- **Simple Interface** - One-page car price prediction
- **Fast Loading** - Minimal dependencies, optimized for speed
- **Mobile Responsive** - Works on all devices
- **Direct API Integration** - Clean communication with backend

## 📁 Structure:
```
frontend_mvp/
├── templates/
│   └── index.html          # Main prediction page
├── static/
│   ├── css/               # Styles
│   ├── js/                # JavaScript
│   └── images/            # Images
└── SERVER_CONFIG.md       # Server setup guide
```

## 🚀 Usage:
1. Update your server to serve from `frontend_mvp/`
2. Navigate to your server URL
3. Fill in car details and get instant price predictions

## 🎨 Design:
- Modern gradient background
- Clean form design
- Smooth animations
- Professional color scheme

## 🔧 API Integration:
- POST `/predict` - Get car price predictions
- Real-time form validation
- Loading states and error handling

## 📱 Browser Support:
- Chrome, Firefox, Safari, Edge
- Mobile browsers
- Responsive design for all screen sizes

Created: {datetime.now().isoformat()}
Files processed: {self.files_processed}
Space optimized: {self.space_saved / 1024 / 1024:.1f} MB
"""
        
        readme_path = mvp_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.log(f"  📝 Created MVP README: {readme_path}")
    
    def run_mvp_finalization(self):
        """Run the complete MVP finalization process"""
        self.log("🎯 Starting MVP Frontend Finalization")
        self.log("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Create final MVP structure
            mvp_dir = self.create_final_mvp_structure()
            
            # Step 2: Update server configuration
            self.update_server_for_mvp()
            
            # Step 3: Clean up old frontends
            self.clean_old_frontends()
            
            # Step 4: Create MVP documentation
            self.create_mvp_readme(mvp_dir)
            
            # Step 5: Save finalization log
            self.save_finalization_log()
            
        except Exception as e:
            self.log(f"❌ Finalization failed: {e}", "ERROR")
            return False
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log("=" * 60)
        self.log("🎉 MVP FRONTEND FINALIZATION COMPLETED!")
        self.log("=" * 60)
        self.log(f"⏱️ Total time: {duration:.2f} seconds")
        self.log(f"📁 MVP directory: frontend_mvp/")
        self.log(f"📄 Files processed: {self.files_processed}")
        self.log(f"💾 Space saved: {self.space_saved / 1024 / 1024:.1f} MB")
        self.log(f"🔧 Next: Update server to use frontend_mvp/templates/")
        
        return True
    
    def save_finalization_log(self):
        """Save finalization log to D: drive"""
        try:
            log_file = Path("D:/pakwheels_mvp_finalization_log.txt")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"PakWheels MVP Frontend Finalization Log\n")
                f.write(f"Started: {datetime.now().isoformat()}\n\n")
                f.write("\n".join(self.log_entries))
            
            self.log(f"💾 Finalization log saved to: {log_file}")
        except Exception as e:
            self.log(f"❌ Could not save finalization log: {e}", "ERROR")

def main():
    """Main function"""
    print("🎯 PakWheels MVP Frontend Finalization")
    print("Setting up clean, fast MVP frontend structure\n")
    
    finalizer = MVPFrontendFinalizer()
    
    # Ask for confirmation
    print("This will:")
    print("- Create clean frontend_mvp/ directory")
    print("- Extract MVP files from consolidated directory")
    print("- Remove old frontend directories")
    print("- Create server configuration guide")
    print("- Generate MVP documentation")
    print()
    
    confirm = input("Continue with MVP finalization? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("❌ MVP finalization cancelled")
        return
    
    success = finalizer.run_mvp_finalization()
    
    if success:
        print("\n✅ MVP frontend finalization completed successfully!")
        print("🔧 Check frontend_mvp/SERVER_CONFIG.md for server setup")
        print("📖 Check frontend_mvp/README.md for usage guide")
    else:
        print("\n❌ MVP finalization encountered errors. Check logs for details.")

if __name__ == "__main__":
    main()
