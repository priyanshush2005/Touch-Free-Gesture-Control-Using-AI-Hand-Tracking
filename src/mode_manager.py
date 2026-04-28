import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time


PRESENTATION_MODE = "presentation"
MEDIA_MODE        = "media"


#Internal state
_current_mode         = MEDIA_MODE   
_last_switch_time     = 0            
MODE_SWITCH_COOLDOWN  = 2.0          


def get_mode():
    """
    Returns the current mode string.
    Either "presentation" or "media"
    """
    return _current_mode


def switch_mode():
    """
    Toggles between presentation and media mode.
    Has a 2 second cooldown to prevent accidental rapid switching.
    Returns True if switch happened, False if cooldown blocked it.
    """
    global _current_mode, _last_switch_time

    now = time.time()

    # Block switch if cooldown hasn't passed
    if now - _last_switch_time < MODE_SWITCH_COOLDOWN:
        return False

    # Toggle the mode
    if _current_mode == MEDIA_MODE:
        _current_mode = PRESENTATION_MODE
    else:
        _current_mode = MEDIA_MODE

    _last_switch_time = now
    print(f"[ModeManager] Switched to: {_current_mode.upper()}")
    return True

def is_presentation_mode():
    """
    Returns True if currently in presentation mode.
    Convenience function so other files don't have to compare strings.
    """
    return _current_mode == PRESENTATION_MODE


def is_media_mode():
    """
    Returns True if currently in media mode.
    """
    return _current_mode == MEDIA_MODE


def reset():
    """
    Resets back to default media mode.
    Called when app starts or restarts.
    """
    global _current_mode, _last_switch_time
    _current_mode     = MEDIA_MODE
    _last_switch_time = 0