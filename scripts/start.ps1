param([int]$Port = 8787)
$ErrorActionPreference = 'Stop'
$atlasRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $atlasRoot
$atlasPython = Join-Path $atlasRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $atlasPython)) { throw 'Create .venv and install requirements first. See README.md.' }
if (-not (Test-Path -LiteralPath (Join-Path $atlasRoot 'frontend\dist\index.html'))) { throw 'Build the frontend first. See README.md.' }
& $atlasPython -m uvicorn vasp_app.main:app --app-dir backend --host 127.0.0.1 --port $Port
