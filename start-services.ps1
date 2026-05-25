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

function Wait-For-Http {
    param (
        [string]$Name,
        [string]$Url,
        [int]$TimeoutSeconds = 180
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5 | Out-Null
            Write-Host "$Name is ready"
            return
        }
        catch {
            Start-Sleep -Seconds 5
        }
    }

    throw "$Name did not become ready at $Url within $TimeoutSeconds seconds"
}

Start-If-Port-Free `
    -Port 5173 `
    -Name "frontend" `
    -FilePath "cmd.exe" `
    -Arguments @("/c", "npm.cmd", "run", "dev", "--", "--host", "127.0.0.1") `
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

Wait-For-Http `
    -Name "ai-service" `
    -Url "http://127.0.0.1:8000/health" `
    -TimeoutSeconds 240

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
