# Windows Task Scheduler Setup for PakWheels Pipeline
# This script creates scheduled tasks for the pipeline

param(
    [string]$Action = "create",
    [string]$TaskName = "PakWheelsPipeline",
    [string]$Schedule = "daily",
    [string]$Time = "02:00"
)

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PipelinePath = Join-Path (Split-Path -Parent $ScriptPath) "pipelines\automated_pipeline.py"
$ConfigPath = Join-Path (Split-Path -Parent $ScriptPath) "config\pipeline_config.json"
$LogPath = Join-Path (Split-Path -Parent $ScriptPath) "logs\scheduled_task.log"

function New-PipelineTask {
    Write-Host "Creating scheduled task: $TaskName" -ForegroundColor Green
    
    # Create the action
    $actionArgs = "$PipelinePath --action run --config $ConfigPath"
    $action = New-ScheduledTaskAction -Execute "python" -Argument $actionArgs -WorkingDirectory (Split-Path -Parent $ScriptPath)
    
    # Create the trigger based on schedule
    switch ($Schedule.ToLower()) {
        "daily" {
            $trigger = New-ScheduledTaskTrigger -Daily -At $Time
        }
        "weekly" {
            $trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Sunday -At $Time
        }
        "hourly" {
            $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddHours(1) -RepetitionInterval (New-TimeSpan -Hours 1)
        }
        default {
            $trigger = New-ScheduledTaskTrigger -Daily -At $Time
        }
    }
    
    # Create task settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    # Create the principal (run as current user)
    $principal = New-ScheduledTaskPrincipal -UserId (whoami) -LogonType Interactive
    
    # Register the task
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "PakWheels automated scraping and cleaning pipeline"
    
    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host "Schedule: $Schedule at $Time" -ForegroundColor Yellow
}

function Remove-PipelineTask {
    Write-Host "Removing scheduled task: $TaskName" -ForegroundColor Yellow
    
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Task removed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Error removing task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Get-PipelineTaskStatus {
    Write-Host "Task Status for: $TaskName" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
        $info = Get-ScheduledTaskInfo -TaskName $TaskName
        
        Write-Host "Task State: $($task.State)" -ForegroundColor $(if ($task.State -eq 'Ready') { 'Green' } else { 'Yellow' })
        Write-Host "Last Run Time: $($info.LastRunTime)" -ForegroundColor Yellow
        Write-Host "Next Run Time: $($info.NextRunTime)" -ForegroundColor Yellow
        Write-Host "Last Task Result: $($info.LastTaskResult)" -ForegroundColor $(if ($info.LastTaskResult -eq 0) { 'Green' } else { 'Red' })
        
        # Show trigger information
        Write-Host "`nTrigger Information:" -ForegroundColor Cyan
        foreach ($trigger in $task.Triggers) {
            Write-Host "  Type: $($trigger.CimClass.CimClassName)" -ForegroundColor Gray
            if ($trigger.StartBoundary) {
                Write-Host "  Start Time: $($trigger.StartBoundary)" -ForegroundColor Gray
            }
            if ($trigger.Repetition.Interval) {
                Write-Host "  Repeat Interval: $($trigger.Repetition.Interval)" -ForegroundColor Gray
            }
        }
        
    } catch {
        Write-Host "Task not found or error accessing task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-PipelineTask {
    Write-Host "Starting scheduled task: $TaskName" -ForegroundColor Green
    
    try {
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Task started successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Error starting task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-PipelineTask {
    Write-Host "Stopping scheduled task: $TaskName" -ForegroundColor Yellow
    
    try {
        Stop-ScheduledTask -TaskName $TaskName
        Write-Host "Task stopped successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Error stopping task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Enable-PipelineTask {
    Write-Host "Enabling scheduled task: $TaskName" -ForegroundColor Green
    
    try {
        Enable-ScheduledTask -TaskName $TaskName
        Write-Host "Task enabled successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Error enabling task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Disable-PipelineTask {
    Write-Host "Disabling scheduled task: $TaskName" -ForegroundColor Yellow
    
    try {
        Disable-ScheduledTask -TaskName $TaskName
        Write-Host "Task disabled successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Error disabling task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-PipelineTaskLogs {
    Write-Host "Recent Pipeline Task Logs:" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    
    # Check task history
    try {
        $events = Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 10 | 
                  Where-Object { $_.Message -like "*$TaskName*" }
        
        if ($events) {
            foreach ($event in $events) {
                Write-Host "[$($event.TimeCreated)] $($event.LevelDisplayName): $($event.Message)" -ForegroundColor Gray
            }
        } else {
            Write-Host "No recent task events found" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Error accessing task logs: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Check pipeline log file
    if (Test-Path $LogPath) {
        Write-Host "`nPipeline Log (last 10 lines):" -ForegroundColor Yellow
        Get-Content $LogPath -Tail 10
    }
}

# Main execution
switch ($Action.ToLower()) {
    "create" { New-PipelineTask }
    "remove" { Remove-PipelineTask }
    "status" { Get-PipelineTaskStatus }
    "start" { Start-PipelineTask }
    "stop" { Stop-PipelineTask }
    "enable" { Enable-PipelineTask }
    "disable" { Disable-PipelineTask }
    "logs" { Show-PipelineTaskLogs }
    default {
        Write-Host "Usage: .\task-scheduler.ps1 -Action [create|remove|status|start|stop|enable|disable|logs]" -ForegroundColor Yellow
        Write-Host "Options:" -ForegroundColor Yellow
        Write-Host "  -Schedule [daily|weekly|hourly] (default: daily)" -ForegroundColor Gray
        Write-Host "  -Time [HH:MM] (default: 02:00)" -ForegroundColor Gray
        Write-Host "  -TaskName [name] (default: PakWheelsPipeline)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\task-scheduler.ps1 -Action create" -ForegroundColor Gray
        Write-Host "  .\task-scheduler.ps1 -Action create -Schedule weekly -Time 03:00" -ForegroundColor Gray
        Write-Host "  .\task-scheduler.ps1 -Action status" -ForegroundColor Gray
        Write-Host "  .\task-scheduler.ps1 -Action start" -ForegroundColor Gray
        Write-Host "  .\task-scheduler.ps1 -Action logs" -ForegroundColor Gray
    }
}
