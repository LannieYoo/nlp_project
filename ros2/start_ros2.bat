@echo off
REM ============================================================
REM NLP RAG ROS 2 Pipeline - Windows Launcher
REM ============================================================
REM 1. 先复制最新代码到 WSL
REM 2. 启动 tmux 多节点环境

REM ── Configuration ──────────────────────────────────────────
REM Change these if your WSL distro name or user is different
set "WSL_DISTRO=Ubuntu-NLP"
set "WSL_USER=aisd"

echo ==========================================
echo   NLP RAG ROS 2 Pipeline Launcher
echo ==========================================
echo   WSL Distro : %WSL_DISTRO%
echo   WSL User   : %WSL_USER%
echo ==========================================

REM Copy latest scripts to WSL
echo [1/3] Syncing scripts to %WSL_DISTRO%...
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "cp /mnt/c/Users/40270/Desktop/workspace/nlp/ros2/run_nodes.sh ~/run_nodes.sh && chmod +x ~/run_nodes.sh"
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "cp -r /mnt/c/Users/40270/Desktop/workspace/nlp/aisd-vision-zhizhunbao/aisd_hearing ~/aisd_ws/src/aisd_hearing"
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "cp -r /mnt/c/Users/40270/Desktop/workspace/nlp/aisd-vision-zhizhunbao/aisd_speaking ~/aisd_ws/src/aisd_speaking"
echo [OK] Scripts synced

REM Rebuild workspace
echo [2/3] Rebuilding ROS 2 workspace...
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash -c "source /opt/ros/humble/setup.bash && cd ~/aisd_ws && colcon build --symlink-install 2>&1"
echo [OK] Build complete

REM Launch nodes
echo [3/3] Launching ROS 2 nodes...
echo.
echo   Entering tmux session. Controls:
echo     Ctrl+B then D   = detach (nodes keep running)
echo     Ctrl+B then [   = scroll mode
echo     Ctrl+C          = stop current node
echo.
wsl -d %WSL_DISTRO% --user %WSL_USER% -- bash ~/run_nodes.sh

echo.
echo [Done] Pipeline stopped.
pause
