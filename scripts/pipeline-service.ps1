# PakWheels Pipeline Windows Service
# This PowerShell script helps run the pipeline as a Windows service

param(
    [string]$Action = "install",
    [string]$ServiceName = "PakWheelsPipeline",
    [string]$ConfigPath = "config/pipeline_config.json"
)

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PipelinePath = Join-Path $ScriptPath "pipelines\automated_pipeline.py"
$LogPath = Join-Path $ScriptPath "logs\service.log"

function Install-PipelineService {
    Write-Host "Installing PakWheels Pipeline Service..." -ForegroundColor Green
    
    # Create the service using NSSM (Non-Sucking Service Manager)
    # Download from: https://nssm.cc/download
    
    $nssmPath = "C:\nssm\nssm.exe"
    
    if (-not (Test-Path $nssmPath)) {
        Write-Host "NSSM not found. Please install NSSM from https://nssm.cc/download" -ForegroundColor Red
        Write-Host "Extract nssm.exe to C:\nssm\ or update the path in this script" -ForegroundColor Yellow
        return
    }
    
    # Install service
    & $nssmPath install $ServiceName python
    & $nssmPath set $ServiceName AppDirectory $ScriptPath
    & $nssmPath set $ServiceName AppParameters "$PipelinePath --action schedule --config $ConfigPath"
    & $nssmPath set $ServiceName DisplayName "PakWheels Automated Pipeline"
    & $nssmPath set $ServiceName Description "Automated scraping and cleaning pipeline for PakWheels data"
    & $nssmPath set $ServiceName Start SERVICE_AUTO_START
    & $nssmPath set $ServiceName Type SERVICE_WIN32_OWN_PROCESS
    & $nssmPath set $ServiceName AppStdout $LogPath
    & $nssmPath set $ServiceName AppStderr $LogPath
    
    Write-Host "Service installed successfully!" -ForegroundColor Green
    Write-Host "Use 'Start-Service $ServiceName' to start the service" -ForegroundColor Yellow
}

function Uninstall-PipelineService {
    Write-Host "Uninstalling PakWheels Pipeline Service..." -ForegroundColor Yellow
    
    # Stop service if running
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    
    # Remove service
    $nssmPath = "C:\nssm\nssm.exe"
    if (Test-Path $nssmPath) {
        & $nssmPath remove $ServiceName confirm
    }
    
    Write-Host "Service uninstalled successfully!" -ForegroundColor Green
}

function Start-PipelineService {
    Write-Host "Starting PakWheels Pipeline Service..." -ForegroundColor Green
    Start-Service -Name $ServiceName
    Write-Host "Service started successfully!" -ForegroundColor Green
}

function Stop-PipelineService {
    Write-Host "Stopping PakWheels Pipeline Service..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force
    Write-Host "Service stopped successfully!" -ForegroundColor Green
}

function Get-PipelineStatus {
    Write-Host "PakWheels Pipeline Status:" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    
    # Service status
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "Service Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq 'Running') { 'Green' } else { 'Red' })
    } else {
        Write-Host "Service Status: Not Installed" -ForegroundColor Red
    }
    
    # Last log entries
    if (Test-Path $LogPath) {
        Write-Host "`nRecent Log Entries:" -ForegroundColor Yellow
        Get-Content $LogPath -Tail 10
    }
    
    # Pipeline status via API
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/pipeline/status" -Method GET -ErrorAction SilentlyContinue
        Write-Host "`nPipeline Status:" -ForegroundColor Yellow
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "`nPipeline API not accessible" -ForegroundColor Red
    }
}

function Test-PipelineRun {
    Write-Host "Running test pipeline execution..." -ForegroundColor Green
    
    # Run pipeline once
    python $PipelinePath --action run --config $ConfigPath
    
    Write-Host "Test run completed!" -ForegroundColor Green
}

# Main execution
switch ($Action.ToLower()) {
    "install" { Install-PipelineService }
    "uninstall" { Uninstall-PipelineService }
    "start" { Start-PipelineService }
    "stop" { Stop-PipelineService }
    "status" { Get-PipelineStatus }
    "test" { Test-PipelineRun }
    default {
        Write-Host "Usage: .\pipeline-service.ps1 -Action [install|uninstall|start|stop|status|test]" -ForegroundColor Yellow
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\pipeline-service.ps1 -Action install" -ForegroundColor Gray
        Write-Host "  .\pipeline-service.ps1 -Action start" -ForegroundColor Gray
        Write-Host "  .\pipeline-service.ps1 -Action status" -ForegroundColor Gray
        Write-Host "  .\pipeline-service.ps1 -Action test" -ForegroundColor Gray
    }
}
