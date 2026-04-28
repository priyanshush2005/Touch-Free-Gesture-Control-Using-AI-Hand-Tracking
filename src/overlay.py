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


def draw_gesture_hud(frame, gesture, confidence):
    """
    Draws gesture name and confidence % in top-left corner.
    Gesture name stays visible for 1.5 seconds after detection.
    """
    global _last_gesture_displayed, _gesture_display_timer

    # Update displayed gesture if a new real gesture detected
    if gesture not in ("NONE", "UNKNOWN"):
        _last_gesture_displayed = gesture
        _gesture_display_timer  = time.time()

    # Only show if within display time window
    elapsed = time.time() - _gesture_display_timer
    if elapsed > GESTURE_DISPLAY_TIME:
        return

    # Format gesture name nicely
    display_name = _last_gesture_displayed.replace("_", " ").title()
    conf_text    = f"Confidence: {int(confidence * 100)}%"

    # Draw gesture name
    _draw_text_with_bg(frame, display_name, 12, 35, FONT_MEDIUM, GREEN, DARK_BG)

    # Draw confidence below it
    _draw_text_with_bg(frame, conf_text, 12, 65, FONT_SMALL, GRAY, DARK_BG)


def draw_palm_hold_progress(frame):
    """
    Draws a filling progress bar when palm is being held in presentation mode.
    Shows user how close they are to triggering fullscreen (4 seconds).
    Only visible when progress > 0.
    """
    progress = get_palm_hold_progress()

    if progress <= 0:
        return

    h, w, _ = frame.shape

    # Bar position — bottom center of frame
    bar_w     = 300
    bar_h     = 18
    bar_x     = (w - bar_w) // 2
    bar_y     = h - 50

    # Background track
    _draw_filled_rect(frame, bar_x, bar_y, bar_w, bar_h, DARK_BG, alpha=0.7)

    # Filled progress portion
    fill_w = int(bar_w * progress)
    if fill_w > 0:
        color = ORANGE if progress < 0.8 else GREEN
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), color, -1)

    # Border
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), WHITE, 1)

    # Label above bar
    label = "Hold to toggle fullscreen..."
    (lw, lh), _ = cv2.getTextSize(label, FONT, FONT_SMALL, 1)
    lx = (w - lw) // 2
    cv2.putText(frame, label, (lx, bar_y - 8), FONT, FONT_SMALL, WHITE, 1)

    # Percentage text inside bar
    pct_text = f"{int(progress * 100)}%"
    cv2.putText(frame, pct_text, (bar_x + bar_w + 8, bar_y + 13), FONT, FONT_SMALL, WHITE, 1)


def draw_volume_indicator(frame):
    """
    Draws current volume level in bottom-left corner.
    Only shown in media mode.
    """
    mode = get_mode()
    if mode != "media":
        return

    vol = get_volume_percent()
    if vol < 0:
        return   # pycaw not available

    h, w, _ = frame.shape

    # Volume bar — vertical, bottom left
    bar_h     = 100
    bar_w     = 14
    bar_x     = 16
    bar_y     = h - bar_h - 60

    # Background
    _draw_filled_rect(frame, bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4, DARK_BG, alpha=0.6)

    # Filled portion
    fill_h = int(bar_h * (vol / 100))
    if fill_h > 0:
        fill_y = bar_y + (bar_h - fill_h)
        color  = RED if vol > 85 else ORANGE if vol > 60 else GREEN
        cv2.rectangle(frame, (bar_x, fill_y), (bar_x + bar_w, bar_y + bar_h), color, -1)

    # Border
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), WHITE, 1)

    # Volume % text below bar
    vol_text = f"Vol {vol}%"
    cv2.putText(frame, vol_text, (bar_x - 2, bar_y + bar_h + 18),
                FONT, FONT_SMALL, WHITE, 1)


def draw_hand_count(frame, hand_count):
    """
    Shows how many hands are detected at the bottom of the frame.
    Turns yellow when 2 hands detected (screenshot ready).
    """
    h, w, _ = frame.shape

    if hand_count == 0:
        return

    color = YELLOW if hand_count == 2 else GRAY
    label = f"{hand_count} hand{'s' if hand_count > 1 else ''} detected"
    if hand_count == 2:
        label += "  —  both palms = screenshot"

    cv2.putText(frame, label, (12, h - 16), FONT, FONT_SMALL, color, 1)


def draw_fps(frame, fps):
    """
    Draws FPS counter in bottom-right corner.
    """
    h, w, _ = frame.shape
    label    = f"FPS: {int(fps)}"
    (lw, _), _ = cv2.getTextSize(label, FONT, FONT_SMALL, 1)
    cv2.putText(frame, label, (w - lw - 12, h - 16), FONT, FONT_SMALL, GRAY, 1)


def draw_all(frame, gesture, confidence, hand_count, fps):
    """
    Master function — call this once per frame from main.py.
    Draws everything on the frame in the correct order.
    """
    draw_mode_badge(frame, )
    draw_gesture_hud(frame, gesture, confidence)
    draw_palm_hold_progress(frame)
    draw_volume_indicator(frame)
    draw_hand_count(frame, hand_count)
    draw_fps(frame, fps)

    return frame