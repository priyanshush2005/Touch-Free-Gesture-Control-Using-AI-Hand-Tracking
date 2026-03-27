<div align="center">

# GestureWave AI
### Touch-Free Gesture Control Using AI Hand Tracking

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=flat-square&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=flat-square)

> Control your computer with just your hands — no touch required.

</div>

---

## 📌 Overview

GestureWave AI is a touch-free gesture control desktop application that uses 
AI-powered hand tracking to let users control their computer without any 
physical contact. Using a standard webcam, the system detects hand gestures 
in real time and maps them to system actions like controlling presentations, 
adjusting volume, and taking screenshots.

Built with Python, OpenCV, and MediaPipe — no special hardware required.

---

## ✨ Features

| Feature | Description | Status |
|---|---|---|
| Live Camera Overlay | Real-time hand landmark visualization on webcam feed | ✅ Done |
| Gesture HUD | Displays detected gesture name and confidence % on screen | 🔨 In Progress |
| Presentation Control | Swipe gestures to navigate slides | 🔨 In Progress |
| Media Control | Volume up/down and play/pause via gestures | 🔨 In Progress |
| Mode Switching | Switch between Presentation and Media mode with a gesture | 🔨 In Progress |
| Two-Hand Screenshot | Both palms open simultaneously takes a screenshot | 🔨 In Progress |

---

## 🗂 Project Structure
```
GestureWave-AI/
│
├── src/
│   ├── main.py                 # Entry point — runs the app
│   ├── handDetection.py        # MediaPipe hand landmark detection
│   ├── gesture_classifier.py   # Classifies gestures from landmarks
│   ├── action_handler.py       # Executes system commands
│   ├── mode_manager.py         # Manages current mode (media/presentation)
│   └── overlay.py              # Draws HUD and landmarks on screen
│
├── models/
│   └── hand_landmarker.task    # MediaPipe hand landmark model
│
├── assets/                     # Screenshots and demo GIFs
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🛠 Tech Stack

- **Python 3.9+** — Core language
- **OpenCV** — Webcam capture and frame rendering
- **MediaPipe** — AI hand landmark detection (21 points per hand)
- **PyAutoGUI** — System control (keyboard, mouse)
- **pycaw** — Windows audio control
- **Pillow** — Screenshot functionality

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/priyanshush2005/Touch-Free-Gesture-Control-Using-AI-Hand-Tracking.git
cd Touch-Free-Gesture-Control-Using-AI-Hand-Tracking
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
cd src
python main.py
```

> **Requirements:** Python 3.9+, Windows OS, a working webcam

---

## 🖐 Gesture Map

| Gesture | Media Mode | Presentation Mode |
|---|---|---|
| Swipe Right | Volume Up | Next Slide |
| Swipe Left | Volume Down | Previous Slide |
| Open Palm | Play / Pause | — |
| Thumbs Up | Switch to Presentation | Switch to Media |
| Both Palms Open | Screenshot | Screenshot |

---

## 🏗 How It Works
```
Webcam Frame
     ↓
Hand Landmark Detection (MediaPipe — 21 points)
     ↓
Gesture Classification (finger angles + positions)
     ↓
Mode Check (Media or Presentation?)
     ↓
Action Execution (PyAutoGUI system command)
     ↓
HUD Overlay (gesture name + confidence on screen)
```

---

## 📈 Development Progress

- [x] Project structure setup
- [x] Hand landmark detection with live overlay
- [ ] Gesture classifier
- [ ] Mode manager
- [ ] Action handler (presentation control)
- [ ] Action handler (media control)
- [ ] Two-hand screenshot
- [ ] HUD overlay
- [ ] Final integration in main.py
- [ ] Package as .exe with PyInstaller

---

## 👥 Team

| Name | Roll Number | Role |
|---|---|---|
| Priyanshu Sharma | 2315510155 | Team Leader |
| Vanshika | 2315510235 | Team Member |
| Harshit Sharma | 2315510084 | Team Member |

---

## 📄 License

This project is for educational purposes — GLA University, Mathura.

---

<div align="center">
Made with Python + MediaPipe
</div>