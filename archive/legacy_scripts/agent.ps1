# Agent Status PowerShell Script
# Run this directly in Claude Code on Windows - NO WSL REQUIRED

param(
    [string]$Command = "status"
)

$ProjectRoot = "L:\Storage\NVMe\projects\lumen"
$Today = Get-Date -Format "yyyy-MM-dd"

function Show-Status {
    Write-Host "`n====== PROJECT STATUS ======" -ForegroundColor Blue
    
    # Check today's tasks
    $TaskFile = "$ProjectRoot\tasks\$Today.md"
    if (Test-Path $TaskFile) {
        Write-Host "`nToday's Tasks:" -ForegroundColor Yellow
        Get-Content $TaskFile | Where-Object {$_ -match "^- \["} | ForEach-Object {
            if ($_ -match "^\- \[x\]") {
                Write-Host $_ -ForegroundColor Green
            } elseif ($_ -match "^\- \[ \]") {
                Write-Host $_ -ForegroundColor White
            }
        }
    }
    
    # Check TODOs
    $TodoFile = "$ProjectRoot\.postbox\todo.md"
    if (Test-Path $TodoFile) {
        $OpenTodos = (Get-Content $TodoFile | Where-Object {$_ -match "^- \[ \]"}).Count
        $InProgress = (Get-Content $TodoFile | Where-Object {$_ -match "^- \[~\]"}).Count
        Write-Host "`nPostbox Status:" -ForegroundColor Yellow
        Write-Host "  Open TODOs: $OpenTodos"
        Write-Host "  In Progress: $InProgress"
    }
    
    # Check completed
    $CompletedFile = "$ProjectRoot\.postbox\completed.md"
    if (Test-Path $CompletedFile) {
        $Completed = (Get-Content $CompletedFile | Where-Object {$_ -match "^- \[x\]"}).Count
        Write-Host "  Completed: $Completed" -ForegroundColor Green
    }
    
    # Git status
    Write-Host "`nGit Status:" -ForegroundColor Yellow
    Set-Location $ProjectRoot
    $GitStatus = git status --short 2>$null
    if ($GitStatus) {
        $GitStatus | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Host "  Working tree clean" -ForegroundColor Green
    }
    
    Write-Host "`n============================" -ForegroundColor Blue
}

function Run-Verification {
    Write-Host "`nRunning Verification..." -ForegroundColor Blue
    
    Set-Location $ProjectRoot
    $ChangedFiles = git diff --name-only 2>$null
    
    if ($ChangedFiles) {
        Write-Host "Files to verify:" -ForegroundColor Yellow
        $ChangedFiles | ForEach-Object { Write-Host "  - $_" }
        
        # Create verification record
        $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $VerificationFile = "$ProjectRoot\.agents\verification_$Timestamp.json"
        
        $Verification = @{
            timestamp = (Get-Date -Format "o")
            files = $ChangedFiles
            status = "pending"
        } | ConvertTo-Json
        
        $Verification | Out-File -FilePath $VerificationFile -Encoding UTF8
        Write-Host "`nVerification request saved: $VerificationFile" -ForegroundColor Green
        
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "1. Call Gemini CLI to review these files"
        Write-Host "2. Run tests: python -m pytest backend/tests/"
        Write-Host "3. Update .postbox/completed.md when done"
    } else {
        Write-Host "No files changed - nothing to verify" -ForegroundColor Green
    }
}

function Initialize-Structure {
    Write-Host "`nInitializing Agent Structure..." -ForegroundColor Blue
    
    # Create directories
    @("tasks", ".postbox", ".agents", ".agents\messages", "docs\screenshots") | ForEach-Object {
        $Path = "$ProjectRoot\$_"
        if (!(Test-Path $Path)) {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
            Write-Host "Created: $_" -ForegroundColor Green
        }
    }
    
    # Create postbox files
    @("todo.md", "completed.md", "issues.md") | ForEach-Object {
        $Path = "$ProjectRoot\.postbox\$_"
        if (!(Test-Path $Path)) {
            New-Item -ItemType File -Path $Path -Force | Out-Null
            Write-Host "Created: .postbox\$_" -ForegroundColor Green
        }
    }
    
    Write-Host "`n✓ Agent structure initialized!" -ForegroundColor Green
}

# Main command dispatcher
switch ($Command) {
    "status" { Show-Status }
    "verify" { Run-Verification }
    "init" { Initialize-Structure }
    default {
        Write-Host "Usage: agent.ps1 [status|verify|init]" -ForegroundColor Yellow
        Write-Host "  status - Show project status"
        Write-Host "  verify - Run verification on changed files"
        Write-Host "  init   - Initialize directory structure"
    }
}
