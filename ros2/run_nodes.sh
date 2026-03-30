#!/bin/bash
# ============================================================
# ROS 2 NLP RAG Pipeline - Launch All Nodes
# Run inside Ubuntu-NLP WSL instance
# ============================================================

# Source ROS 2 and workspace
source /opt/ros/humble/setup.bash
source ~/aisd_ws/install/setup.bash

# Windows host IP (auto-detect from WSL2 default gateway)
# Note: resolv.conf nameserver may differ from the actual Windows host IP.
#       The default route gateway is the reliable way to reach Windows from WSL2.
WIN_HOST=$(ip route show default | awk '{print $3}')
API_URL="${API_URL:-http://${WIN_HOST}:8000/api/search}"
MODEL="${MODEL:-qwen2.5:0.5b}"
TOP_K="${TOP_K:-3}"

echo "=========================================="
echo "  NLP RAG ROS 2 Pipeline"
echo "=========================================="
echo "  API URL : $API_URL"
echo "  Model   : $MODEL"
echo "  Top-K   : $TOP_K"
echo "=========================================="

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "[!] tmux not installed. Installing..."
    sudo apt-get install -y tmux
fi

SESSION="nlp_rag"

# Kill existing session if any
tmux kill-session -t $SESSION 2>/dev/null

# Create new tmux session with 3 panes
tmux new-session -d -s $SESSION -n "nodes"

# ── Pane 0: Ollama Publisher (RAG Node) ──────────────────────
tmux send-keys -t $SESSION:0.0 \
  "source /opt/ros/humble/setup.bash && source ~/aisd_ws/install/setup.bash && echo '[RAG] Ollama Publisher Starting...' && ros2 run aisd_hearing ollama_publisher --ros-args -p api_url:=$API_URL -p model:=$MODEL -p top_k:=$TOP_K" C-m

# ── Pane 1: Speak Service (TTS) ─────────────────────────────
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.1 \
  "source /opt/ros/humble/setup.bash && source ~/aisd_ws/install/setup.bash && echo '[TTS] Speak Service Starting...' && ros2 run aisd_speaking speak" C-m

# ── Pane 2: Speak Client ────────────────────────────────────
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.2 \
  "source /opt/ros/humble/setup.bash && source ~/aisd_ws/install/setup.bash && echo '[SPK] Speak Client Starting...' && ros2 run aisd_hearing speak_client" C-m

# ── Pane 3: Manual test publisher (for testing) ─────────────
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.3 \
  "source /opt/ros/humble/setup.bash && source ~/aisd_ws/install/setup.bash && echo '[TEST] Ready. Send a test message with:' && echo '  ros2 topic pub --once /words std_msgs/msg/String \"{data: \\\"What is attention mechanism?\\\"}\"' && echo '' && echo 'Or monitor all topics:' && echo '  ros2 topic echo /ollama_reply'" C-m

# Balance panes
tmux select-layout -t $SESSION even-vertical

echo ""
echo "[OK] All nodes launched in tmux session '$SESSION'"
echo ""
echo "To attach:  tmux attach -t $SESSION"
echo "To detach:  Ctrl+B then D"
echo "To kill:    tmux kill-session -t $SESSION"
echo ""

# Attach to the session
tmux attach -t $SESSION
