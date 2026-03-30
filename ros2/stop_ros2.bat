@echo off
REM ============================================================
REM NLP RAG ROS 2 Pipeline - Stop All Services
REM ============================================================

REM ── Configuration ──────────────────────────────────────────
set "WSL_DISTRO=Ubuntu-NLP"
set "WSL_USER=aisd"

echo ==========================================
echo   Stopping NLP RAG ROS 2 Pipeline
echo ==========================================

echo [1/3] Killing tmux session...
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "tmux kill-session -t nlp_rag 2>/dev/null && echo '  [OK] tmux session killed' || echo '  [SKIP] No tmux session found'"

echo [2/3] Killing all ROS 2 and node processes...
REM Kill by specific script/module names (these run as python3 processes)
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "pkill -9 -f speak_client 2>/dev/null; pkill -9 -f speak_service 2>/dev/null; pkill -9 -f ollama_publisher 2>/dev/null; pkill -9 -f aisd_speaking 2>/dev/null; pkill -9 -f aisd_hearing 2>/dev/null; pkill -9 -f 'ros2' 2>/dev/null; echo '  [OK] Kill signals sent'"

REM Wait for processes to die
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "sleep 2"

echo [3/3] Verifying...
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "if ps aux | grep -E 'ros2|speak|ollama|aisd_' | grep -v grep > /dev/null 2>&1; then echo '  [WARN] Some processes still running:'; ps aux | grep -E 'ros2|speak|ollama|aisd_' | grep -v grep; else echo '  [OK] All clean'; fi"

echo.
echo [Done] All ROS 2 services stopped.
pause
