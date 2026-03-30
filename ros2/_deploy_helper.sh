#!/bin/bash
# Add ollama_publisher entry point to setup.py
SETUP_FILE=~/ros2_ws/src/aisd-vision-zhizhunbao/aisd_hearing/setup.py

# Check if already added
if grep -q "ollama_publisher" "$SETUP_FILE"; then
    echo "ollama_publisher already registered"
else
    sed -i "/speak_client = aisd_hearing.speak_client:main/a\\            'ollama_publisher = aisd_hearing.ollama_publisher:main'," "$SETUP_FILE"
    echo "ollama_publisher entry point added"
fi

echo "=== Current entry_points ==="
grep -A6 "console_scripts" "$SETUP_FILE"

# Build workspace
echo ""
echo "=== Building ROS 2 workspace ==="
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select aisd_hearing 2>&1

echo ""
echo "=== Build complete ==="
