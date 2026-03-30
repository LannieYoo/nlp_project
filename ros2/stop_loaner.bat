@echo off
REM ============================================================
REM NLP RAG ROS 2 Pipeline - Loaner Laptop Stopper (from Windows)
REM ============================================================
REM 1. Stop all ROS 2 nodes on loaner laptop
REM 2. Verify no orphan processes remain

set "LAPTOP=aisd@192.168.2.33"

echo ==========================================
echo   Stop NLP RAG Pipeline (Loaner Laptop)
echo ==========================================
echo   Target : %LAPTOP%
echo ==========================================

REM ── Step 1: Test SSH connectivity ─────────────────────────
echo.
echo [1/3] Testing SSH connection...
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 %LAPTOP% "echo SSH OK" 2>nul
if errorlevel 1 (
    echo [FAIL] Cannot reach %LAPTOP%. Is the laptop on?
    pause
    exit /b 1
)
echo [OK] Connected

REM ── Step 2: Stop all nodes ────────────────────────────────
echo.
echo [2/3] Stopping all ROS 2 nodes...
ssh -o StrictHostKeyChecking=no %LAPTOP% "bash ~/stop_loaner.sh"

REM ── Step 3: Verify ────────────────────────────────────────
echo.
echo [3/3] Verifying cleanup...
ssh -o StrictHostKeyChecking=no %LAPTOP% "if ps aux | grep -E 'ros2|speak|ollama|aisd_|recording_pub|words_pub' | grep -v grep > /dev/null 2>&1; then echo '  [WARN] Some processes still running:'; ps aux | grep -E 'ros2|speak|ollama|aisd_' | grep -v grep; else echo '  [OK] All clean'; fi"

echo.
echo [Done] All ROS 2 nodes on loaner laptop stopped.
echo   To restart: run start_loaner.bat
pause
