@echo off
echo Starting Open Hardware Monitor Dashboard Backend...

echo.
echo Starting Backend (without virtual environment)...
cd backend
start "Backend" cmd /k "python -m pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Backend is starting...
echo Backend will be available at: http://localhost:8000
echo.
echo Press any key to exit this window...
pause > nul
