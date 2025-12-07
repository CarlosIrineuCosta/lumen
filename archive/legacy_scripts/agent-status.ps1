# Agent Status Script - Windows PowerShell (NO WSL)
$ProjectRoot = "L:\Storage\NVMe\projects\lumen"
$Today = Get-Date -Format "yyyy-MM-dd"

Write-Host ""
Write-Host "====== PROJECT STATUS ======" -ForegroundColor Blue
Write-Host ""

# Check today's tasks
$TaskFile = "$ProjectRoot\tasks\$Today.md"
if (Test-Path $TaskFile) {
    Write-Host "Today's Tasks:" -ForegroundColor Yellow
    Get-Content $TaskFile | Where-Object {$_ -match "^- \["} | Select-Object -First 10
}

# Check TODOs
$TodoFile = "$ProjectRoot\.postbox\todo.md"
if (Test-Path $TodoFile) {
    $Todos = @(Get-Content $TodoFile | Where-Object {$_ -match "^- \[ \]"}).Count
    Write-Host ""
    Write-Host "Pending TODOs: $Todos" -ForegroundColor Yellow
}

# Check completed
$CompletedFile = "$ProjectRoot\.postbox\completed.md"
if (Test-Path $CompletedFile) {
    $Done = @(Get-Content $CompletedFile | Where-Object {$_ -match "^- \[x\]"}).Count
    Write-Host "Completed Tasks: $Done" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================" -ForegroundColor Blue
