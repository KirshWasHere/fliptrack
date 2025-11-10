@echo off
echo ========================================
echo Reselling Profit Tracker
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import textual" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Create necessary directories
if not exist "data\images" mkdir data\images
if not exist "reports" mkdir reports

REM Run the application
echo Starting application...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
