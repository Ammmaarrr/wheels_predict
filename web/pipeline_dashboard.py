#!/usr/bin/env python3
"""
Pipeline Dashboard - Web interface for monitoring the automated pipeline
"""

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from pipelines.automated_pipeline import AutomatedPipeline
except ImportError:
    AutomatedPipeline = None

app = Flask(__name__)
app.secret_key = 'wheels-predict-pipeline-dashboard-secret'

# Global pipeline instance
pipeline = None

def init_pipeline():
    """Initialize the pipeline instance"""
    global pipeline
    if pipeline is None and AutomatedPipeline:
        config_path = project_root / "config" / "pipeline_config.json"
        pipeline = AutomatedPipeline(str(config_path))

def get_pipeline_stats():
    """Get pipeline statistics"""
    try:
        init_pipeline()
        if pipeline:
            return pipeline.get_status()
        else:
            return {"error": "Pipeline not available"}
    except Exception as e:
        return {"error": str(e)}

def get_recent_files():
    """Get recent scraped and cleaned files"""
    files = {"raw": [], "cleaned": []}
    
    try:
        # Raw files
        raw_dir = project_root / "data" / "raw"
        if raw_dir.exists():
            for file in sorted(raw_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                files["raw"].append({
                    "name": file.name,
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Cleaned files
        cleaned_dir = project_root / "data" / "cleaned"
        if cleaned_dir.exists():
            for file in sorted(cleaned_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                files["cleaned"].append({
                    "name": file.name,
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
    except Exception as e:
        files["error"] = str(e)
    
    return files

@app.route('/')
def dashboard():
    """Main dashboard page"""
    stats = get_pipeline_stats()
    files = get_recent_files()
    
    return render_template('dashboard.html', stats=stats, files=files)

@app.route('/api/status')
def api_status():
    """API endpoint for pipeline status"""
    return jsonify(get_pipeline_stats())

@app.route('/api/files')
def api_files():
    """API endpoint for recent files"""
    return jsonify(get_recent_files())

@app.route('/api/trigger/<action>')
def api_trigger(action):
    """API endpoint to trigger pipeline actions"""
    try:
        init_pipeline()
        if not pipeline:
            return jsonify({"error": "Pipeline not available"}), 500
        
        if action == "scrape":
            success, result = pipeline.scraping_pipeline.run_scraping()
            return jsonify({"success": success, "result": result})
        elif action == "clean":
            success, result = pipeline.cleaning_pipeline.run_cleaning()
            return jsonify({"success": success, "result": result})
        elif action == "full":
            pipeline.run_full_pipeline()
            return jsonify({"success": True, "message": "Full pipeline started"})
        else:
            return jsonify({"error": "Invalid action"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """API endpoint for recent logs"""
    try:
        log_file = project_root / "logs" / "pipeline.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return jsonify({"logs": lines[-100:]})  # Last 100 lines
        else:
            return jsonify({"logs": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config')
def config_page():
    """Configuration page"""
    try:
        config_file = project_root / "config" / "pipeline_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        return render_template('config.html', config=config)
    except Exception as e:
        flash(f"Error loading config: {e}", "error")
        return redirect(url_for('dashboard'))

@app.route('/config', methods=['POST'])
def save_config():
    """Save configuration"""
    try:
        config_data = request.json
        config_file = project_root / "config" / "pipeline_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        flash("Configuration saved successfully!", "success")
        return jsonify({"success": True})
    except Exception as e:
        flash(f"Error saving config: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/logs')
def logs_page():
    """Logs page"""
    try:
        log_file = project_root / "logs" / "pipeline.log"
        logs = []
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = f.readlines()[-200:]  # Last 200 lines
        
        return render_template('logs.html', logs=logs)
    except Exception as e:
        flash(f"Error loading logs: {e}", "error")
        return redirect(url_for('dashboard'))

# Template for dashboard.html
dashboard_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Wheels Predict Pipeline Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { margin: 0 0 10px 0; color: #2c3e50; }
        .stat-value { font-size: 24px; font-weight: bold; color: #3498db; }
        .status-running { color: #27ae60; }
        .status-stopped { color: #e74c3c; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #219a52; }
        .btn-warning { background: #f39c12; }
        .btn-warning:hover { background: #d68910; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .files-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .file-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .file-item:last-child { border-bottom: none; }
        .nav { margin-bottom: 20px; }
        .nav a { display: inline-block; padding: 10px 20px; background: #34495e; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }
        .nav a:hover { background: #2c3e50; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Wheels Predict Pipeline Dashboard</h1>
            <p>Automated Scraping and Cleaning Pipeline</p>
        </div>
        
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/config">Configuration</a>
            <a href="/logs">Logs</a>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Pipeline Status</h3>
                <div class="stat-value {{ 'status-running' if stats.get('is_running') else 'status-stopped' }}">
                    {{ 'RUNNING' if stats.get('is_running') else 'STOPPED' }}
                </div>
                <p>{{ 'Active and monitoring' if stats.get('is_running') else 'Inactive' }}</p>
            </div>
            
            <div class="stat-card">
                <h3>Next Run</h3>
                <div class="stat-value">
                    {{ stats.get('next_run', 'Not scheduled') }}
                </div>
                <p>Scheduled execution time</p>
            </div>
            
            <div class="stat-card">
                <h3>Recent Runs</h3>
                <div class="stat-value">{{ stats.get('recent_runs', [])|length }}</div>
                <p>Completed in last 24 hours</p>
            </div>
            
            <div class="stat-card">
                <h3>Actions</h3>
                <button class="btn btn-success" onclick="triggerAction('scrape')">Run Scraping</button>
                <button class="btn btn-warning" onclick="triggerAction('clean')">Run Cleaning</button>
                <button class="btn btn-danger" onclick="triggerAction('full')">Full Pipeline</button>
            </div>
        </div>
        
        <div class="files-section">
            <h2>Recent Files</h2>
            
            <h3>Raw Data Files</h3>
            {% if files.raw %}
                {% for file in files.raw %}
                <div class="file-item">
                    <strong>{{ file.name }}</strong> - {{ file.size|filesizeformat }} - {{ file.modified }}
                </div>
                {% endfor %}
            {% else %}
                <p>No raw data files found</p>
            {% endif %}
            
            <h3>Cleaned Data Files</h3>
            {% if files.cleaned %}
                {% for file in files.cleaned %}
                <div class="file-item">
                    <strong>{{ file.name }}</strong> - {{ file.size|filesizeformat }} - {{ file.modified }}
                </div>
                {% endfor %}
            {% else %}
                <p>No cleaned data files found</p>
            {% endif %}
        </div>
        
        <div class="files-section">
            <h2>Recent Pipeline Runs</h2>
            {% if stats.get('recent_runs') %}
                {% for run in stats.recent_runs %}
                <div class="file-item">
                    <strong>{{ run.operation }}</strong> - 
                    <span class="{{ 'status-running' if run.status == 'success' else 'status-stopped' }}">{{ run.status }}</span> - 
                    {{ run.timestamp }} - 
                    {{ run.records_processed }} records
                </div>
                {% endfor %}
            {% else %}
                <p>No recent runs found</p>
            {% endif %}
        </div>
    </div>
    
    <script>
        function triggerAction(action) {
            if (confirm(`Are you sure you want to run ${action}?`)) {
                fetch(`/api/trigger/${action}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(`${action} started successfully!`);
                            location.reload();
                        } else {
                            alert(`Error: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        alert(`Error: ${error}`);
                    });
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
'''

# Create templates directory and save template
templates_dir = project_root / "templates"
templates_dir.mkdir(exist_ok=True)

with open(templates_dir / "dashboard.html", "w") as f:
    f.write(dashboard_template)

if __name__ == '__main__':
    print("🌐 Starting Pipeline Dashboard...")
    print("📊 Dashboard available at: http://localhost:5001")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )
