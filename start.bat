@echo off
echo Starting Open Hardware Monitor Dashboard...

echo.
echo Starting Backend...
cd backend
start "Backend" cmd /k "venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Starting Frontend...
cd ..\frontend
start "Frontend" cmd /k "npm install && npm start"

echo.
echo Dashboard is starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul
