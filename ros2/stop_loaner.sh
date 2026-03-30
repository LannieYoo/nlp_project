#!/bin/bash
# Stop all ROS 2 nodes on loaner laptop
tmux kill-session -t nlp_rag 2>/dev/null && echo "[OK] tmux session killed" || echo "[SKIP] No session"
pkill -9 -f recording_publisher 2>/dev/null
pkill -9 -f words_publisher 2>/dev/null
pkill -9 -f ollama_publisher 2>/dev/null
pkill -9 -f speak_client 2>/dev/null
pkill -9 -f speak 2>/dev/null
pkill -9 -f aisd_ 2>/dev/null
sleep 1
echo "[OK] All ROS 2 processes stopped"
