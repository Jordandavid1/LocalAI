Write-Host "LocalAI Setup Script" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Host "ERROR: Python not found. Install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

Write-Host "Python: $pythonPath" -ForegroundColor Green

Write-Host ""
Write-Host "Checking Ollama..." -ForegroundColor Yellow
$ollamaPath = (Get-Command ollama -ErrorAction SilentlyContinue).Source
if (-not $ollamaPath) {
    Write-Host "Ollama not found. Installing..." -ForegroundColor Yellow
    Write-Host "Download from: https://ollama.ai/download" -ForegroundColor Cyan
    Write-Host "After installing Ollama, run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Ollama: $ollamaPath" -ForegroundColor Green

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start Ollama: ollama serve" -ForegroundColor White
Write-Host "2. In another terminal, pull Mixtral: ollama pull dolphin-mixtral" -ForegroundColor White
Write-Host "3. Start the backend: python backend.py" -ForegroundColor White
Write-Host "4. Open http://localhost:8000/ui in your browser" -ForegroundColor White
