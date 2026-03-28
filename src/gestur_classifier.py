import math


# ── Finger tip and base landmark indices ────────────────────────────────────
FINGER_TIPS  = [4, 8, 12, 16, 20]   # Thumb, Index, Middle, Ring, Pinky
FINGER_BASES = [2, 6, 10, 14, 18]   # Base knuckle of each finger

# ── Swipe detection state (tracked across frames) ───────────────────────────
_swipe_history = []          # stores recent x positions of index finger tip
SWIPE_HISTORY_LENGTH = 12    # how many frames to track
SWIPE_THRESHOLD = 0.12       # minimum normalized x movement to count as swipe


def _get_finger_states(hand):
    """
    Returns a list of 5 booleans — one per finger.
    True = finger is up/extended, False = finger is curled down.
    [Thumb, Index, Middle, Ring, Pinky]
    """
    fingers = []

    # Thumb — compare x axis (thumb moves sideways, not up/down)
    if hand[4].x < hand[3].x:
        fingers.append(True)   # thumb extended left
    else:
        fingers.append(False)

    # Other 4 fingers — compare y axis (tip above base = extended)
    for tip, base in zip(FINGER_TIPS[1:], FINGER_BASES[1:]):
        if hand[tip].y < hand[base].y:
            fingers.append(True)
        else:
            fingers.append(False)

    return fingers


def _get_distance(p1, p2):
    """
    Returns Euclidean distance between two landmarks.
    """
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)



