#!/bin/bash
# ============================================================
# ROS 2 NLP RAG Pipeline - Loaner Laptop Launcher
# Run on the loaner laptop (native Ubuntu 22.04)
# ============================================================

# Source ROS 2 and workspace
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

# Local Ollama configuration
MODEL="${MODEL:-qwen2.5:0.5b}"
RAG_PATH="${RAG_PATH:-$HOME/ros2_ws/knowledge/knowledge.txt}"

echo "=========================================="
echo "  NLP RAG ROS 2 Pipeline (Loaner Laptop)"
echo "=========================================="
echo "  Model    : $MODEL"
echo "  RAG File : $RAG_PATH"
echo "  Ollama   : http://localhost:11434"
echo "=========================================="

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "[!] tmux not installed. Installing..."
    sudo apt-get install -y tmux
fi

SESSION="nlp_rag"

# Kill existing session if any
tmux kill-session -t $SESSION 2>/dev/null

# Create new tmux session with 5 panes in one window
tmux new-session -d -s $SESSION -n "nodes"

# ── Pane 0: Recording Publisher (Microphone) ─────────────────
tmux send-keys -t $SESSION:0.0 \
  "source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash && echo '[MIC] Recording Publisher Starting...' && ros2 run aisd_hearing recording_publisher" C-m

# ── Pane 1: Words Publisher (Whisper STT) ────────────────────
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.1 \
  "source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash && echo '[STT] Words Publisher Starting Whisper STT...' && ros2 run aisd_hearing words_publisher" C-m

# ── Pane 2: Ollama Publisher (RAG Node) ──────────────────────
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.2 \
  "source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash && echo '[RAG] Ollama Publisher Starting...' && ros2 run aisd_hearing ollama_publisher --ros-args -p model:=$MODEL -p rag_path:=$RAG_PATH" C-m

# Rebalance before adding more panes (prevents silent split failure)
tmux select-layout -t $SESSION tiled

# ── Pane 3: Speak Service (TTS) ─────────────────────────────
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.3 \
  "source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash && echo '[TTS] Speak Service Starting...' && ros2 run aisd_speaking speak" C-m

# Rebalance again before final split
tmux select-layout -t $SESSION tiled

# ── Pane 4: Speak Client ────────────────────────────────────
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.4 \
  "source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash && echo '[SPK] Speak Client Starting...' && ros2 run aisd_hearing speak_client" C-m

# Final layout: tiled gives each pane equal space
tmux select-layout -t $SESSION tiled

echo ""
echo "[OK] All 5 nodes launched in tmux session '$SESSION'"
echo ""
echo "  [MIC] recording_publisher  - Microphone input"
echo "  [STT] words_publisher      - Whisper STT"
echo "  [RAG] ollama_publisher     - RAG Q&A"
echo "  [TTS] speak (service)      - TTS engine"
echo "  [SPK] speak_client         - TTS trigger"
echo ""
echo "To attach:  tmux attach -t $SESSION"
echo "To detach:  Ctrl+B then D"
echo "To kill:    tmux kill-session -t $SESSION"
echo ""

# Attach to the session
tmux attach -t $SESSION
