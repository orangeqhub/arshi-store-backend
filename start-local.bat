@echo off
echo Starting Arshi local development stack...
echo.

echo [1/3] Starting PostgreSQL (requires Administrator)...
net start postgresql-x64-18
if errorlevel 1 (
    echo WARNING: Could not start PostgreSQL. Run this script as Administrator,
    echo or start "postgresql-x64-18" manually from services.msc
)

echo.
echo [2/3] Starting Backend API on http://localhost:8000 ...
cd /d "%~dp0"
call env\Scripts\activate.bat
start "Arshi API" cmd /k uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo [3/3] Frontends - run in separate terminals:
echo   Store:  cd ..\ARSHI-STORE  ^&^& npm run dev   ^(http://localhost:3000^)
echo   Admin:  cd ..\ARSHI-ADMIN  ^&^& npm run dev   ^(http://localhost:3001^)
echo.
echo API URLs configured:
echo   Store .env:  http://localhost:8000/
echo   Admin .env:  http://localhost:8000/api/v1
pause
