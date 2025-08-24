@echo off
echo Cleaning up corrupted virtual environment...

echo.
echo Stopping any running Python processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul

echo.
echo Removing corrupted virtual environment...
cd backend
if exist venv (
    echo Attempting to remove venv directory...
    rmdir /s /q venv 2>nul
    if exist venv (
        echo Failed to remove venv. You may need to restart your computer and try again.
        echo Or manually delete the 'backend\venv' folder.
    ) else (
        echo Successfully removed corrupted virtual environment.
    )
) else (
    echo No venv directory found.
)

echo.
echo Cleanup complete!
echo You can now run 'start.bat' to start the application without virtual environment.
echo.
pause
