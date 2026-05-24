# HSUSMS - Start Harare Smart Urban Security System
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $ProjectRoot "backend"
$Venv = Join-Path $Backend ".venv"

if (-not (Test-Path $Venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv $Venv
    & "$Venv\Scripts\pip.exe" install -r (Join-Path $Backend "requirements.txt")
}

Write-Host "Starting HSUSMS at http://127.0.0.1:8000"
Write-Host "Citizen web app: http://127.0.0.1:8000/citizen.html"
Set-Location $Backend
& "$Venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
