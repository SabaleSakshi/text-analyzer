$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $Root "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$BackendPort = 8001
$BackendEnvPath = Join-Path $Root "backend\.env"

if (Test-Path $BackendEnvPath) {
    $portLine = (Get-Content $BackendEnvPath | Where-Object { $_ -match "^PORT=" } | Select-Object -First 1)
    if ($portLine -match "^PORT=(\d+)") {
        $BackendPort = [int]$Matches[1]
    }
}

function Start-If-Port-Free {
    param (
        [int]$Port,
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$OutLog,
        [string]$ErrLog
    )

    $existing = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue

    if ($existing) {
        Write-Host "$Name already running on port $Port"
        return
    }

    Start-Process `
        -FilePath $FilePath `
        -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $OutLog `
        -RedirectStandardError $ErrLog `
        -WindowStyle Hidden | Out-Null

    Write-Host "Started $Name on port $Port"
}

Start-If-Port-Free `
    -Port 5173 `
    -Name "frontend" `
    -FilePath "npm" `
    -Arguments @("run", "dev") `
    -WorkingDirectory (Join-Path $Root "frontend") `
    -OutLog (Join-Path $LogDir "frontend.out.log") `
    -ErrLog (Join-Path $LogDir "frontend.err.log")

Start-If-Port-Free `
    -Port 8000 `
    -Name "ai-service" `
    -FilePath (Join-Path $Root "ai-service\.venv\Scripts\python.exe") `
    -Arguments @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory (Join-Path $Root "ai-service") `
    -OutLog (Join-Path $LogDir "ai-service.out.log") `
    -ErrLog (Join-Path $LogDir "ai-service.err.log")

Start-If-Port-Free `
    -Port $BackendPort `
    -Name "backend" `
    -FilePath (Join-Path $Root "backend\.venv\Scripts\python.exe") `
    -Arguments @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $BackendPort) `
    -WorkingDirectory (Join-Path $Root "backend") `
    -OutLog (Join-Path $LogDir "backend.out.log") `
    -ErrLog (Join-Path $LogDir "backend.err.log")

Write-Host ""
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host "Backend:  http://127.0.0.1:$BackendPort"
Write-Host "AI:       http://127.0.0.1:8000"
Write-Host ""
Write-Host "AI startup can take 1-3 minutes while the model loads."
