import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import time
from action_handler import get_palm_hold_progress, get_volume_percent
from mode_manager import get_mode

# ── Colors (BGR format for OpenCV) ───────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0  )
GREEN       = (0,   255, 180)
ORANGE      = (0,   165, 255)
PURPLE      = (255, 100, 150)
DARK_BG     = (20,  20,  20 )
GRAY        = (130, 130, 130)
RED         = (0,   0,   220)
YELLOW      = (0,   220, 220)

# ── Font settings ────────────────────────────────────────────────────────────
FONT        = cv2.FONT_HERSHEY_SIMPLEX
FONT_SMALL  = 0.5
FONT_MEDIUM = 0.7
FONT_LARGE  = 1.0
THICKNESS   = 2

# ── Internal state ───────────────────────────────────────────────────────────
_last_gesture_displayed = "NONE"
_gesture_display_timer  = 0
GESTURE_DISPLAY_TIME    = 1.5   # seconds to keep gesture name on screen


def _draw_filled_rect(frame, x, y, w, h, color, alpha=0.5):
    """
    Draws a semi-transparent filled rectangle on the frame.
    Used for HUD backgrounds so text is readable over the camera feed.
    """
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def _draw_text_with_bg(frame, text, x, y, font_scale, color, bg_color, padding=6):
    """
    Draws text with a semi-transparent background box behind it.
    Makes text readable regardless of what's in the camera feed.
    """
    (text_w, text_h), baseline = cv2.getTextSize(text, FONT, font_scale, THICKNESS)
    _draw_filled_rect(
        frame,
        x - padding,
        y - text_h - padding,
        text_w + padding * 2,
        text_h + baseline + padding * 2,
        bg_color,
        alpha=0.6
    )
    cv2.putText(frame, text, (x, y), FONT, font_scale, color, THICKNESS)


def draw_mode_badge(frame):
    """
    Draws current mode badge in top-right corner.
    Green for Media, Purple for Presentation.
    """
    h, w, _ = frame.shape
    mode = get_mode()

    if mode == "presentation":
        label     = "PRESENTATION MODE"
        bg_color  = (139, 0, 139)   # dark purple
        txt_color = PURPLE
    else:
        label     = "MEDIA MODE"
        bg_color  = (0, 100, 0)     # dark green
        txt_color = GREEN

    (text_w, text_h), _ = cv2.getTextSize(label, FONT, FONT_SMALL, THICKNESS)
    x = w - text_w - 24
    y = 30

    _draw_filled_rect(frame, x - 8, y - text_h - 8, text_w + 16, text_h + 16, bg_color, alpha=0.7)
    cv2.putText(frame, label, (x, y), FONT, FONT_SMALL, txt_color, THICKNESS)


# Draws the name of the detected gesture in the center of the screen for a brief moment.
# This provides immediate feedback to the user about which gesture was recognized.