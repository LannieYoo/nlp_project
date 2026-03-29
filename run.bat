@echo off
title RAG App Launcher
echo ============================================
echo   AI Textbook Q^&A - RAG App Launcher
echo ============================================
echo.

:: Kill existing processes on port 8000 (backend)
echo [1/5] Checking port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)
echo   Port 8000 cleared.

:: Kill existing processes on port 5173 (frontend)
echo [2/5] Checking port 5173 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a on port 5173...
    taskkill /F /PID %%a >nul 2>&1
)
echo   Port 5173 cleared.

:: Kill orphaned node.exe processes (leftover Vite/npm dev servers)
echo [3/5] Cleaning up orphaned node processes...
taskkill /F /IM node.exe >nul 2>&1
echo   Node processes cleared.
echo.

:: Start backend server
echo [4/5] Starting Backend (uvicorn on port 8000)...
cd /d %~dp0
start "RAG Backend" /min cmd /k "cd /d %~dp0 && python -m uvicorn backend.api.server:app --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak >nul

:: Start frontend dev server
echo [5/5] Starting Frontend (Vite on port 5173)...
start "RAG Frontend" /min cmd /k "cd /d %~dp0\frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo   Both servers are starting!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ============================================
echo.
echo Opening browser...
start http://localhost:5173
echo.
echo You can close this window. The servers run in separate windows.
timeout /t 3 /nobreak >nul
exit
