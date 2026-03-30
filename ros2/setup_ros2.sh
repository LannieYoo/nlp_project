#!/bin/bash
# ============================================================
# ROS 2 Humble + NLP RAG Workspace Setup Script
# Target: Ubuntu-NLP (WSL Ubuntu 22.04)
# User: peng
# ============================================================
set -e

echo "=========================================="
echo " Step 1: Install ROS 2 Humble"
echo "=========================================="

# Add ROS 2 apt repository
sudo apt-get update -qq
sudo apt-get install -y software-properties-common curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu jammy main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ros-humble-ros-base \
  python3-colcon-common-extensions \
  python3-pip

echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source /opt/ros/humble/setup.bash

echo "[OK] ROS 2 Humble installed"

echo "=========================================="
echo " Step 2: Install system dependencies"
echo "=========================================="

# ffmpeg: Required by pydub (used in aisd_speaking TTS service)
# tmux:   Required by run_nodes.sh to manage multiple ROS 2 nodes
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ffmpeg \
  tmux

echo "[OK] System dependencies installed (ffmpeg, tmux)"

echo "=========================================="
echo " Step 3: Install Python dependencies"
echo "=========================================="

pip3 install requests gtts pydub

echo "[OK] Python dependencies installed"

echo "=========================================="
echo " Step 4: Create ROS 2 workspace"
echo "=========================================="

mkdir -p ~/aisd_ws/src
cd ~/aisd_ws/src

# Create knowledge directory
mkdir -p ~/aisd_ws/knowledge

echo "[OK] Workspace created at ~/aisd_ws"

echo "=========================================="
echo " Step 5: Copy ROS 2 packages"
echo "=========================================="

# Copy the packages from Windows mount
WINDOWS_BASE="/mnt/c/Users/40270/Desktop/workspace/nlp/aisd-vision-zhizhunbao"

for pkg in aisd_hearing aisd_msgs aisd_speaking; do
  PKG_PATH="$WINDOWS_BASE/$pkg"
  if [ -d "$PKG_PATH" ]; then
    cp -r "$PKG_PATH" ~/aisd_ws/src/
    echo "[OK] $pkg package copied"
  else
    echo "[WARN] Package not found at $PKG_PATH, skipping"
  fi
done

echo "=========================================="
echo " Step 6: Build workspace"
echo "=========================================="

cd ~/aisd_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install 2>&1 || echo "[WARN] Build had issues, check output above"

# Source workspace
echo "source ~/aisd_ws/install/setup.bash" >> ~/.bashrc

echo "=========================================="
echo " Step 7: Copy launch scripts"
echo "=========================================="

SCRIPTS_DIR="/mnt/c/Users/40270/Desktop/workspace/nlp/ros2"

cp "$SCRIPTS_DIR/run_nodes.sh" ~/run_nodes.sh && chmod +x ~/run_nodes.sh
cp "$SCRIPTS_DIR/test_publish.sh" ~/test_publish.sh && chmod +x ~/test_publish.sh

echo "[OK] Launch scripts copied to home directory"

echo "=========================================="
echo " DONE! Setup complete."
echo "=========================================="
echo ""
echo "Network Note:"
echo "  Windows host IP is auto-detected via default route gateway."
echo "  Detected: $(ip route show default | awk '{print $3}')"
echo "  If the FastAPI backend is not reachable, check:"
echo "    1. FastAPI is running on Windows: python -m uvicorn ... --host 0.0.0.0 --port 8000"
echo "    2. Windows firewall allows port 8000 from WSL"
echo ""
echo "Usage (from Windows):"
echo ""
echo "  Start all nodes:   ros2\\start_ros2.bat"
echo "  Stop all nodes:    ros2\\stop_ros2.bat"
echo "  Send test message: ros2\\test_ros2.bat \"What is attention?\""
echo ""
echo "Or manually inside WSL:"
echo "  bash ~/run_nodes.sh                  # Start all nodes in tmux"
echo "  tmux attach -t nlp_rag               # View running nodes"
echo "  bash ~/test_publish.sh \"question\"     # Send a test message"
echo ""
