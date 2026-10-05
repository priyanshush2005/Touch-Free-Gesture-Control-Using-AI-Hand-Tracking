<div align="center">

# GestureWave AI
### Touch-Free Gesture Control Using AI Hand Tracking

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=flat-square&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Landmarker-orange?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=flat-square&logo=windows)
![Version](https://img.shields.io/badge/Version-v1.0.0-success?style=flat-square)

**Control your PC with your hands. Real-time, offline, no special hardware.**

[🌐 Live Website & Tutorial](https://gesturewaveai.vercel.app/) · [⬇ Download for Windows](https://gesturewaveai.vercel.app/assets/GestureWaveAI.zip)

</div>

---

## 📌 Overview

GestureWave AI is a Windows desktop application that lets users control media playback, presentations, and screenshots using hand gestures captured by an ordinary webcam. A hand-tracking model locates 21 landmarks per hand in each frame, a rule-based classifier turns those landmarks into gestures, and a mode-aware action layer maps each gesture to a system command.

**Why it matters:** touch-free control is useful when your hands are busy, dirty, or out of reach of the keyboard, such as presenting while walking around a room, cooking with a video tutorial, or working in sterile or accessibility-sensitive settings. Everything runs **locally**: no cloud calls, no accounts, and no video leaves the machine.

---

## 🚀 Quick Start

### Option A: Run the packaged app (no Python needed)
1. Download the zip from the [project website](https://gesturewaveai.vercel.app/).
2. Extract it and run `GestureWaveAI.exe`.
3. If Windows SmartScreen appears, click **More info → Run anyway**. The app is unsigned because it's a student project built with PyInstaller.

### Option B: Run from source
```bash
git clone https://github.com/priyanshush2005/Touch-Free-Gesture-Control-Using-AI-Hand-Tracking.git
cd Touch-Free-Gesture-Control-Using-AI-Hand-Tracking
pip install -r requirements.txt
python src/main.py          # run from the repository root
```

> **Note:** run from the repository root so the app can find `models/hand_landmarker.task`.
> **Requirements:** Windows 10/11, Python 3.9+, a working webcam.

---

## 🖐 Gesture Map

The app has two modes. Switch between them using the sidebar buttons.

| Gesture | Media Mode | Presentation Mode |
|---|---|---|
| ☝️ Index finger up | Volume up (hold) | Next slide |
| 🤙 Pinky up | Volume down (hold) | Previous slide |
| ✋ Open palm | Play / Pause | Hold 4 s → toggle slideshow (F5 / Esc) |
| ✊ Closed fist | Toggle fullscreen (`F`) | — |
| 👍 Thumbs up | Screenshot | Screenshot |
| 🙌 Both palms open | Screenshot | Screenshot |

Screenshots are saved to `Pictures/GestureWave/`.

---

## 🏗 Architecture

```
Webcam frame (OpenCV)
        ↓
Hand landmark detection (MediaPipe, 21 points × up to 2 hands)
        ↓
Gesture classification (finger-state rules + temporal swipe tracking)
        ↓
Mode check (Media / Presentation)
        ↓
Action execution (PyAutoGUI / pycaw) with cooldowns
        ↓
HUD overlay (gesture, confidence, mode, hold-progress bar)
```

```
src/
├── main.py                 # CustomTkinter GUI + threaded camera loop
├── handDetection.py        # MediaPipe Hand Landmarker wrapper, skeleton drawing
├── gesture_classifier.py   # Landmarks → gesture name
├── mode_manager.py         # Media / Presentation state with switch cooldown
├── action_handler.py       # Gesture → system action, per mode
└── overlay.py              # HUD rendering on the video frame
models/hand_landmarker.task # MediaPipe model bundled with the app
```

---

## 🧠 Engineering Highlights

- **Clear separation of concerns.** Detection, classification, mode state, actions, and rendering each live in their own module with a small interface, so any stage can be swapped or tested independently.
- **Non-blocking UI.** The camera and inference loop runs on a background thread, and frames are pushed to the CustomTkinter UI through `after()`, so the interface stays responsive.
- **Safe, deliberate triggering.**
  - Per-action cooldowns (0.6 s) stop one gesture from firing repeatedly.
  - Fullscreen needs a **4-second palm hold**, with an on-screen progress bar, so it can't be triggered by accident.
  - A 3 s screenshot cooldown and a 2 s mode-switch cooldown add further protection.
  - PyAutoGUI's fail-safe is enabled: move the mouse to the top-left corner to abort.
- **Smooth volume control.** The app talks to the Windows audio endpoint directly through `pycaw` for fine-grained steps, and falls back to media keys if the audio API is unavailable.
- **Two-hand gestures.** The classifier checks for the two-palm screenshot gesture before single-hand rules, so both hands are used when present.
- **Privacy by design.** Inference is fully on-device, with no network access required.
- **Real distribution.** Packaged as a standalone `.exe` with PyInstaller, including MediaPipe assets and a `resource_path()` helper that resolves the model path in both dev and bundled builds.

---

## ⚠️ Known Limitations & Roadmap

I'd rather be upfront about the current limits:

- **Windows only.** Audio control uses `pycaw`; the app would need a platform abstraction layer for macOS or Linux.
- **Rule-based classifier.** Finger "up" is decided by landmark position comparisons, so it is sensitive to hand rotation, camera angle, and lighting. A learned classifier (for example, a small MLP on normalized landmarks) would be more robust.
- **Handedness.** Thumb detection currently assumes one hand orientation; MediaPipe's handedness output should be used to support left and right hands equally.
- **Confidence is rule-based.** The HUD percentage is a fixed certainty per gesture rule, not a model probability.
- **Mode switching is via the sidebar.** A gesture-based mode toggle and more reliable swipe navigation are planned.
- **Single-hand gestures use the first detected hand.**

**Planned next:** landmark-based ML classifier, handedness-aware logic, configurable gesture-to-action mapping, unit tests with synthetic landmark data, and a signed installer.

---

## 🛠 Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.9+ |
| Computer vision | OpenCV |
| Hand tracking | MediaPipe Hand Landmarker (21 landmarks per hand) |
| UI | CustomTkinter, Pillow |
| System control | PyAutoGUI, pycaw / comtypes |
| Packaging | PyInstaller |

---

## 👥 Team

| Name | Role |
|---|---|
| **Priyanshu Sharma** (Team Leader) | Architecture, gesture classifier, action handler and mode manager, integration in `main.py`, PyInstaller packaging, and the website and release. |
| Vanshika | CustomTkinter GUI, HUD overlay (`overlay.py`), and UI/UX testing. |
| Harshit Sharma | MediaPipe detection module (`handDetection.py`), landmark visualization, gesture testing in different lighting, and documentation. |

Built at **GLA University, Mathura**.

📫 **Contact:** [sharma.priyanshush2005@gmail.com](mailto:sharma.priyanshush2005@gmail.com) · [LinkedIn](https://www.linkedin.com/in/priyanshu-sharma-548351282) · [GitHub](https://github.com/priyanshush2005)

---

## 📄 License

Developed as an academic project at GLA University, Mathura.

---

<div align="center">
Made with Python + MediaPipe · <a href="https://gesturewaveai.vercel.app/">gesturewaveai.vercel.app</a>
</div>
