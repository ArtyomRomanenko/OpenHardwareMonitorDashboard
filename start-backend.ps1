# PowerShell script to start the backend
Write-Host "Starting Open Hardware Monitor Dashboard Backend..." -ForegroundColor Green

Write-Host "`nStarting Backend..." -ForegroundColor Yellow
Set-Location backend

# Activate virtual environment and start server
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated successfully" -ForegroundColor Green
    
    Write-Host "Starting uvicorn server..." -ForegroundColor Yellow
    & ".\venv\Scripts\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host "Error starting backend: $_" -ForegroundColor Red
    Write-Host "Make sure the virtual environment exists and is properly configured" -ForegroundColor Yellow
}

Write-Host "`nBackend stopped. Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
