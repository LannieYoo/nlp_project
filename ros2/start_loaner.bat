@echo off
REM ============================================================
REM NLP RAG ROS 2 Pipeline - Loaner Laptop Launcher (from Windows)
REM ============================================================
REM 1. Sync latest code to laptop via SCP
REM 2. Rebuild ROS 2 workspace
REM 3. Launch all nodes in tmux and attach (see all panes)

set "LAPTOP=aisd@192.168.2.33"

echo ==========================================
echo   NLP RAG ROS 2 Pipeline (Loaner Laptop)
echo ==========================================
echo   Target : %LAPTOP%
echo ==========================================

REM ── Step 1: Sync latest source files ──────────────────────
echo.
echo [📦 SYNC] Syncing source files to laptop...
scp -o StrictHostKeyChecking=no "%~dp0..\aisd-vision-zhizhunbao\aisd_hearing\aisd_hearing\recording_publisher.py" %LAPTOP%:~/ros2_ws/src/aisd-vision-zhizhunbao/aisd_hearing/aisd_hearing/recording_publisher.py
scp -o StrictHostKeyChecking=no "%~dp0..\aisd-vision-zhizhunbao\aisd_hearing\aisd_hearing\words_publisher.py" %LAPTOP%:~/ros2_ws/src/aisd-vision-zhizhunbao/aisd_hearing/aisd_hearing/words_publisher.py
scp -o StrictHostKeyChecking=no "%~dp0..\aisd-vision-zhizhunbao\aisd_hearing\aisd_hearing\ollama_publisher.py" %LAPTOP%:~/ros2_ws/src/aisd-vision-zhizhunbao/aisd_hearing/aisd_hearing/ollama_publisher.py
scp -o StrictHostKeyChecking=no "%~dp0..\aisd-vision-zhizhunbao\aisd_hearing\aisd_hearing\speak_client.py" %LAPTOP%:~/ros2_ws/src/aisd-vision-zhizhunbao/aisd_hearing/aisd_hearing/speak_client.py
scp -o StrictHostKeyChecking=no "%~dp0run_loaner.sh" %LAPTOP%:~/run_loaner.sh
scp -o StrictHostKeyChecking=no "%~dp0stop_loaner.sh" %LAPTOP%:~/stop_loaner.sh
scp -o StrictHostKeyChecking=no "%~dp0knowledge.txt" %LAPTOP%:~/ros2_ws/knowledge/knowledge.txt
echo [✅ SYNC] Files synced (including knowledge.txt)

REM ── Step 2: Stop existing nodes ───────────────────────────
echo.
echo [🛑 STOP] Stopping existing nodes...
ssh -o StrictHostKeyChecking=no %LAPTOP% "bash ~/stop_loaner.sh"
echo [✅ STOP] Old nodes stopped

REM ── Step 3: Rebuild workspace ─────────────────────────────
echo.
echo [🔨 BUILD] Rebuilding ROS 2 workspace...
ssh -o StrictHostKeyChecking=no %LAPTOP% "source /opt/ros/humble/setup.bash && cd ~/ros2_ws && colcon build --symlink-install --packages-select aisd_hearing 2>&1"
echo [✅ BUILD] Build complete

REM ── Step 4: Launch nodes and attach to tmux ───────────────
echo.
echo [🚀 LAUNCH] Launching all nodes...
echo.
echo   Entering tmux session with 5 panes. Controls:
echo     Ctrl+B then D   = detach (nodes keep running)
echo     Ctrl+B then [   = scroll mode
echo     Ctrl+C          = stop current pane's node
echo.
ssh -t -o StrictHostKeyChecking=no %LAPTOP% "bash ~/run_loaner.sh"

echo.
echo [🏁 DONE] Disconnected from laptop. Nodes may still be running.
echo   To re-attach:  ssh -t %LAPTOP% "tmux attach -t nlp_rag"
echo   To stop all:   ssh %LAPTOP% "bash ~/stop_loaner.sh"
pause
