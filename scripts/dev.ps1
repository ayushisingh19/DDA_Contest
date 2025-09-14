param(
  [switch]$NoFrontend,
  [switch]$NoBackend,
  [switch]$SkipMigrations
)

$ErrorActionPreference = 'Stop'

function Start-Frontend {
  Push-Location "$PSScriptRoot/../frontend"
  try {
    if (-not (Test-Path node_modules)) { npm install }
    npm run watch:all
  }
  finally { Pop-Location }
}

function Start-Backend {
  Push-Location "$PSScriptRoot/../src/student_auth"
  try {
    $venvPython = Join-Path $PWD ".venv/Scripts/python.exe"
    if (-not (Test-Path $venvPython)) {
      Write-Host ".venv not found. Creating with system Python..." -ForegroundColor Yellow
      $cmd = Get-Command python -ErrorAction SilentlyContinue
      if (-not $cmd) { $cmd = Get-Command py -ErrorAction SilentlyContinue }
      if (-not $cmd) { throw "No Python interpreter found on PATH." }
      $sysPy = $cmd.Path
      & $sysPy -m venv .venv
      & "$PWD/.venv/Scripts/python.exe" -m pip install --upgrade pip setuptools wheel
    }

    # Ensure backend dev requirements are installed (Django, DRF, Celery, Redis, pytest, ruff, black)
    $backendReq = Join-Path $PWD "../../backend/requirements/dev.txt"
    if (Test-Path $backendReq) {
      Write-Host "Installing backend dev requirements..." -ForegroundColor Cyan
      & "$PWD/.venv/Scripts/pip.exe" install -r $backendReq | Out-Host
    }

    # Run migrations unless skipped
    if (-not $SkipMigrations) {
      Write-Host "Applying migrations..." -ForegroundColor Cyan
      & "$PWD/.venv/Scripts/python.exe" manage.py migrate | Out-Host
    }

    & "$PWD/.venv/Scripts/python.exe" manage.py runserver 127.0.0.1:8000
  }
  finally { Pop-Location }
}

if (-not $NoFrontend) {
  Start-Job -Name frontend -ScriptBlock { & powershell -NoProfile -ExecutionPolicy Bypass -File "$using:PSScriptRoot/dev.ps1" -NoBackend }
}

if (-not $NoBackend) {
  Start-Backend
}

Write-Host "Dev script started. Use 'Get-Job' to see background jobs." -ForegroundColor Green
