import time


# ── Mode constants ───────────────────────────────────────────────────────────
PRESENTATION_MODE = "presentation"
MEDIA_MODE        = "media"

# ── Internal state ───────────────────────────────────────────────────────────
_current_mode         = MEDIA_MODE   # app starts in media mode
_last_switch_time     = 0            # timestamp of last mode switch
MODE_SWITCH_COOLDOWN  = 2.0          # seconds before mode can switch again


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