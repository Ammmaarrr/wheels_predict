# PakWheels Pipeline Setup Script
# This script sets up the automated pipeline system

param(
    [switch]$InstallDependencies,
    [switch]$SetupDirectories,
    [switch]$CreateSchedule,
    [switch]$StartDashboard,
    [switch]$All
)

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptPath

Write-Host "🚀 PakWheels Pipeline Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    
    $requirementsFile = Join-Path $ProjectRoot "requirements.pipeline.txt"
    
    if (Test-Path $requirementsFile) {
        python -m pip install -r $requirementsFile
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Requirements file not found: $requirementsFile" -ForegroundColor Red
    }
}

function Setup-Directories {
    Write-Host "📁 Setting up directory structure..." -ForegroundColor Yellow
    
    $directories = @(
        "data/raw",
        "data/cleaned",
        "logs",
        "backups",
        "config",
        "templates"
    )
    
    foreach ($dir in $directories) {
        $fullPath = Join-Path $ProjectRoot $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-Host "  Created: $dir" -ForegroundColor Green
        } else {
            Write-Host "  Exists: $dir" -ForegroundColor Gray
        }
    }
    
    Write-Host "✅ Directory structure created!" -ForegroundColor Green
}

function Test-PipelineSetup {
    Write-Host "🧪 Testing pipeline setup..." -ForegroundColor Yellow
    
    # Test Python import
    $testScript = @"
import sys
import os
sys.path.insert(0, r'$ProjectRoot')

try:
    from pipelines.automated_pipeline import AutomatedPipeline
    print('✅ Pipeline module imported successfully')
    
    # Test configuration
    config_path = r'$ProjectRoot\config\pipeline_config.json'
    if os.path.exists(config_path):
        pipeline = AutomatedPipeline(config_path)
        print('✅ Pipeline configuration loaded successfully')
        
        # Test status
        status = pipeline.get_status()
        print(f'✅ Pipeline status: {status}')
    else:
        print('⚠️  Configuration file not found')
        
except Exception as e:
    print(f'❌ Error: {e}')
"@
    
    $testScript | python
}

function Start-Dashboard {
    Write-Host "🌐 Starting pipeline dashboard..." -ForegroundColor Yellow
    
    $dashboardScript = Join-Path $ProjectRoot "web\pipeline_dashboard.py"
    
    if (Test-Path $dashboardScript) {
        Write-Host "Dashboard starting at: http://localhost:5001" -ForegroundColor Green
        Start-Process -FilePath "python" -ArgumentList $dashboardScript -WorkingDirectory $ProjectRoot
        
        # Wait a moment and open browser
        Start-Sleep -Seconds 3
        Start-Process "http://localhost:5001"
    } else {
        Write-Host "❌ Dashboard script not found: $dashboardScript" -ForegroundColor Red
    }
}

function Show-QuickStart {
    Write-Host ""
    Write-Host "🎯 Quick Start Guide" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Test the pipeline:" -ForegroundColor Yellow
    Write-Host "   python pipelines\automated_pipeline.py --action run" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Set up Windows Task Scheduler:" -ForegroundColor Yellow
    Write-Host "   .\scripts\task-scheduler.ps1 -Action create" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Start the dashboard:" -ForegroundColor Yellow
    Write-Host "   python web\pipeline_dashboard.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. View pipeline status:" -ForegroundColor Yellow
    Write-Host "   python pipelines\automated_pipeline.py --action status" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. Configure pipeline:" -ForegroundColor Yellow
    Write-Host "   Edit config\pipeline_config.json" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 Dashboard: http://localhost:5001" -ForegroundColor Green
    Write-Host "📁 Data Directory: $ProjectRoot\data" -ForegroundColor Green
    Write-Host "📋 Logs Directory: $ProjectRoot\logs" -ForegroundColor Green
    Write-Host ""
}

function Show-SystemInfo {
    Write-Host "🔧 System Information" -ForegroundColor Cyan
    Write-Host "====================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Python Version:" -ForegroundColor Yellow
    python --version
    Write-Host ""
    Write-Host "Project Root:" -ForegroundColor Yellow
    Write-Host $ProjectRoot -ForegroundColor Gray
    Write-Host ""
    Write-Host "Available Scripts:" -ForegroundColor Yellow
    $scripts = @(
        "pipelines\automated_pipeline.py - Main pipeline script",
        "web\pipeline_dashboard.py - Web dashboard",
        "scripts\task-scheduler.ps1 - Windows Task Scheduler",
        "scripts\pipeline-service.ps1 - Windows Service"
    )
    foreach ($script in $scripts) {
        Write-Host "  $script" -ForegroundColor Gray
    }
    Write-Host ""
}

# Main execution
if ($All) {
    $InstallDependencies = $true
    $SetupDirectories = $true
    $CreateSchedule = $true
    $StartDashboard = $true
}

# Show system info
Show-SystemInfo

# Execute requested actions
if ($InstallDependencies) {
    Install-Dependencies
}

if ($SetupDirectories) {
    Setup-Directories
}

if ($CreateSchedule) {
    Write-Host "⏰ Setting up scheduled task..." -ForegroundColor Yellow
    & (Join-Path $ScriptPath "task-scheduler.ps1") -Action create
}

if ($StartDashboard) {
    Start-Dashboard
}

# Always test the setup
Test-PipelineSetup

# Show quick start guide
Show-QuickStart

Write-Host "🎉 Pipeline setup completed!" -ForegroundColor Green
Write-Host "Use the dashboard at http://localhost:5001 to monitor and control the pipeline." -ForegroundColor Yellow
