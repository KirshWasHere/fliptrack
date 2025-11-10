@echo off
echo ========================================
echo FlipTrack - Clean for Publishing
echo ========================================
echo.

echo Removing test data and artifacts...

if exist "tracker.db" (
    del /F /Q "tracker.db"
    echo ✓ Removed tracker.db
)

if exist "data" (
    rmdir /S /Q "data"
    echo ✓ Removed data directory
)

if exist "reports" (
    rmdir /S /Q "reports"
    echo ✓ Removed reports directory
)

if exist "__pycache__" (
    rmdir /S /Q "__pycache__"
    echo ✓ Removed __pycache__
)

if exist "temp_preview" (
    rmdir /S /Q "temp_preview"
    echo ✓ Removed temp_preview
)

echo.
echo Removing backup files...
for %%f in (backup_*) do (
    if exist "%%f" (
        rmdir /S /Q "%%f"
        echo ✓ Removed %%f
    )
)

for %%f in (fliptrack_export_*.csv) do (
    if exist "%%f" (
        del /F /Q "%%f"
        echo ✓ Removed %%f
    )
)

for %%f in (fliptrack_backup_*.json) do (
    if exist "%%f" (
        del /F /Q "%%f"
        echo ✓ Removed %%f
    )
)

echo.
echo ========================================
echo ✓ Project cleaned and ready for GitHub!
echo ========================================
echo.
echo Next steps:
echo 1. git init
echo 2. git add .
echo 3. git commit -m "Initial commit: FlipTrack v2.0"
echo 4. Create repository on GitHub
echo 5. git remote add origin https://github.com/yourusername/fliptrack.git
echo 6. git push -u origin main
echo.
echo See GITHUB_SETUP.md for detailed instructions.
echo.
pause
