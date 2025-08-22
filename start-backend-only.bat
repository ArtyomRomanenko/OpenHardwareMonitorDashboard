@echo off
echo Starting Open Hardware Monitor Dashboard Backend Only...

echo.
echo Starting Backend...
cd backend
start "Backend" cmd /k "venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Backend is starting...
echo Backend will be available at: http://localhost:8000
echo API documentation will be available at: http://localhost:8000/docs
echo.
echo Press any key to exit this window...
pause > nul
