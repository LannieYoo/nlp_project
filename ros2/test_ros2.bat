@echo off
REM ============================================================
REM NLP RAG ROS 2 Pipeline - Test Script
REM ============================================================

REM ── Configuration ──────────────────────────────────────────
set "WSL_DISTRO=Ubuntu-NLP"
set "WSL_USER=aisd"

echo ==========================================
echo   NLP RAG ROS 2 Pipeline - Test
echo ==========================================

REM Copy test script to WSL
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "cp /mnt/c/Users/40270/Desktop/workspace/nlp/ros2/test_publish.sh ~/test_publish.sh && chmod +x ~/test_publish.sh"

if "%~1"=="" (
    set "MSG=What is attention mechanism?"
) else (
    set "MSG=%~1"
)

echo.
echo Sending test message: "%MSG%"
echo.
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash ~/test_publish.sh "%MSG%"

echo.
echo [Done] Message published. Check the tmux session for responses.
echo   To attach: wsl -d %WSL_DISTRO% --user %WSL_USER% -- tmux attach -t nlp_rag
pause
