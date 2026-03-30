#!/bin/bash
source /opt/ros/humble/setup.bash
source ~/aisd_ws/install/setup.bash

MSG="${1:-What is attention mechanism?}"
echo "Publishing: $MSG"
ros2 topic pub --once /words std_msgs/msg/String "{data: '$MSG'}"
