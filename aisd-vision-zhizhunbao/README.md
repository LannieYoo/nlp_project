# AISD Vision, Motion & Hearing - ROS 2 Projects

This repository contains two independent ROS 2 projects:

- **Assignment 2**: Hand Gesture Control System (Vision & Motion)
- **Assignment 3**: Hearing & Speaking System (Audio & Speech)

## 📚 Documentation

Each assignment has its own complete documentation:

- **[Assignment 2 Documentation](README_Assignment2.md)** - Hand gesture recognition and robot motion control
- **[Assignment 3 Documentation](README_Assignment3.md)** - Audio recording, speech-to-text, and text-to-speech

## Quick Overview

### Assignment 2 - Vision & Motion System

A ROS 2-based system that provides hand gesture recognition and robot motion control. The system uses MediaPipe to identify hand poses and converts gestures into robot motion commands.

**Key Features:**
- Real-time hand gesture detection using MediaPipe
- Robot motion control based on hand gestures
- Turtlesim integration for visualization

**Packages:**
- `aisd_vision`: Hand gesture recognition
- `aisd_motion`: Motion control

👉 **[See full Assignment 2 documentation](README_Assignment2.md)**

### Assignment 3 - Hearing & Speaking System

A ROS 2-based system that provides audio recording, speech-to-text transcription, and text-to-speech capabilities. The system records audio from a microphone, transcribes speech using Whisper, and provides voice feedback.

**Key Features:**
- Audio recording from microphone
- Speech-to-text using OpenAI Whisper
- Text-to-speech using Google TTS

**Packages:**
- `aisd_hearing`: Audio recording and speech recognition
- `aisd_speaking`: Text-to-speech service

👉 **[See full Assignment 3 documentation](README_Assignment3.md)**

## Common Prerequisites

Both assignments require:

1. **ROS 2** (Humble or later recommended)
2. **Ubuntu** (20.04 or later)
3. **Python 3** (3.8 or later)
4. **Git**

## Repository Structure

```
aisd-vision-zhizhunbao/
├── README.md                    # This file (index)
├── README_Assignment2.md        # Assignment 2 documentation
├── README_Assignment3.md        # Assignment 3 documentation
├── aisd_vision/                 # Assignment 2: Vision package
├── aisd_motion/                 # Assignment 2: Motion package
├── aisd_hearing/                # Assignment 3: Hearing package
├── aisd_speaking/               # Assignment 3: Speaking package
├── aisd_msgs/                   # Common message definitions
└── docs/                        # Assignment documentation
```

## Getting Started

1. **Clone the repository:**

   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws/src
   git clone https://github.com/gitalg/aisd-vision-zhizhunbao.git
   cd aisd-vision-zhizhunbao
   ```

2. **Choose your assignment:**

   - For **Assignment 2** (Vision & Motion): See [README_Assignment2.md](README_Assignment2.md)
   - For **Assignment 3** (Hearing & Speaking): See [README_Assignment3.md](README_Assignment3.md)

## Notes

- The two assignments are **completely independent** and can be run separately
- Each assignment has its own dependencies and setup instructions
- Refer to the specific assignment documentation for detailed installation and usage instructions

---

**Author**: Wang Peng ([zhizhunbao](https://github.com/zhizhunbao)) (wang1059@algonquinlive.com) | CST8504 - Algonquin College
