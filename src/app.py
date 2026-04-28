def get_mode():
    """
    Returns the current mode string.
    Either "presentation" or "media"
    """
    return _current_mode

def reset():
    """
    Resets back to default media mode.
    Called when app starts or restarts.
    """
    global _current_mode, _last_switch_time
    _current_mode     = MEDIA_MODE
    _last_switch_time = 0