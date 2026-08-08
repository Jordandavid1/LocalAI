Write-Host "LocalAI Launcher" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host ""

$ollamaPath = (Get-Command ollama -ErrorAction SilentlyContinue).Source
if (-not $ollamaPath) {
    Write-Host "ERROR: Ollama not installed" -ForegroundColor Red
    Write-Host "Install from https://ollama.ai/download" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Ollama service..." -ForegroundColor Yellow
Start-Process ollama -ArgumentList "serve" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "Checking for Mixtral model..." -ForegroundColor Yellow
$models = ollama list 2>&1
if ($models -notmatch "dolphin-mixtral") {
    Write-Host "Pulling dolphin-mixtral (uncensored)..." -ForegroundColor Yellow
    ollama pull dolphin-mixtral
}

Write-Host ""
Write-Host "Starting LocalAI backend..." -ForegroundColor Yellow
python backend.py
