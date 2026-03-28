import time
import pyautogui
import subprocess
from PIL import ImageGrab
import os

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