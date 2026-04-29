import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import pyautogui
import subprocess
from PIL import ImageGrab

from mode_manager import get_mode, switch_mode, is_presentation_mode, is_media_mode

# ── PyAutoGUI safety settings ────────────────────────────────────────────────
pyautogui.FAILSAFE = True    # move mouse to top-left corner to emergency stop
pyautogui.PAUSE   = 0.05    # small delay between pyautogui actions

# ── Volume control settings ──────────────────────────────────────────────────
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    VOLUME_CONTROL_AVAILABLE = True
except Exception:
    VOLUME_CONTROL_AVAILABLE = False
    print("[ActionHandler] pycaw not available — volume control disabled")

# ── Internal state
_last_action_time      = 0      # timestamp of last action fired
_palm_hold_start       = 0      # when open palm gesture started
_palm_holding          = False  # is palm currently being held
_fullscreen_active     = False  # is presentation fullscreen on or off
_screenshot_cooldown   = 0      # timestamp of last screenshot
_last_gesture          = "NONE" # previous frame's gesture

#Cooldown settings (seconds)
ACTION_COOLDOWN       = 0.6    # general cooldown between actions
PALM_HOLD_DURATION    = 4.0    # seconds to hold palm for fullscreen toggle
SCREENSHOT_COOLDOWN   = 3.0    # seconds between screenshots
VOLUME_STEP           = 0.05   # volume change per frame when holding (5%)


#Volume Helpers

def _volume_up():
    if VOLUME_CONTROL_AVAILABLE:
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = min(1.0, current + VOLUME_STEP)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
    else:
        pyautogui.press('volumeup')


def _volume_down():
    if VOLUME_CONTROL_AVAILABLE:
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, current - VOLUME_STEP)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
    else:
        pyautogui.press('volumedown')


def get_volume_percent():
    """Returns current system volume as integer 0-100.
    Used by overlay.py to display volume on HUD.
    """
    if VOLUME_CONTROL_AVAILABLE:
        return int(volume.GetMasterVolumeLevelScalar() * 100)
    return -1   # -1 means unavailable

#Presentation Actions 

def _next_slide():
    pyautogui.press('right')
    print("[Action] Next slide")


def _prev_slide():
    pyautogui.press('left')
    print("[Action] Previous slide")


def _toggle_fullscreen():
    """
    Pressing F5 in PowerPoint starts the slideshow from current slide.
    Pressing Escape exits it. We track state with _fullscreen_active.
    """
    global _fullscreen_active
    if not _fullscreen_active:
        pyautogui.press('f5')
        _fullscreen_active = True
        print("[Action] Fullscreen ON")
    else:
        pyautogui.press('escape')
        _fullscreen_active = False
        print("[Action] Fullscreen OFF")


#Media Actions 

def _play_pause():
    pyautogui.press('space')
    print("[Action] Play / Pause")

#Screenshot 
def _take_screenshot():
    global _screenshot_cooldown

    now = time.time()
    if now - _screenshot_cooldown < SCREENSHOT_COOLDOWN:
        return   # still in cooldown, skip

    # Save to user's Pictures folder
    pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures", "GestureWave")
    os.makedirs(pictures_dir, exist_ok=True)

    filename = f"screenshot_{int(now)}.png"
    filepath = os.path.join(pictures_dir, filename)

    screenshot = ImageGrab.grab()
    screenshot.save(filepath)

    _screenshot_cooldown = now
    print(f"[Action] Screenshot saved → {filepath}")

#Palm Hold Timer - for fullscreen(Presentaion Mode only)
def get_palm_hold_progress():
    """
    Returns float 0.0 to 1.0 showing how long palm has been held.
    0.0 = just started, 1.0 = 4 seconds reached.
    Used by overlay.py to draw the progress bar.
    """
    if not _palm_holding:
        return 0.0
    elapsed = time.time() - _palm_hold_start
    return min(1.0, elapsed / PALM_HOLD_DURATION)

#Main Execution Function 

def execute(gesture, confidence, hand_count):
    """
    Main function — called every frame by main.py.
    Takes gesture name, confidence score, and hand count.
    Decides what action to fire based on current mode.
    """
    global _last_action_time, _palm_hold_start
    global _palm_holding, _last_gesture

    now  = time.time()
    mode = get_mode()

    #GLOBAL GESTURES — work in any mode

    # Screenshot — two hands both open
    if gesture == "BOTH_PALMS" and hand_count == 2:
        _take_screenshot()
        return
    
    
    