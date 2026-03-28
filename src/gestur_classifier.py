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


def classify(landmarks):
    """
    Main function — takes landmarks from get_landmarks() in handDetection.py.
    Returns a tuple: (gesture_name, confidence, hand_count)

    gesture_name  → string like "OPEN_PALM", "SWIPE_RIGHT", "THUMBS_UP" etc.
    confidence    → float 0.0 to 1.0
    hand_count    → int 1 or 2
    """
    global _swipe_history

    hand_count = len(landmarks)

    # ── No hands detected ───────────────────────────────────────────────────
    if hand_count == 0:
        _swipe_history.clear()
        return ("NONE", 0.0, 0)

    # ── TWO HANDS — check for screenshot gesture first ──────────────────────
    if hand_count == 2:
        fingers_h1 = _get_finger_states(landmarks[0])
        fingers_h2 = _get_finger_states(landmarks[1])
        # Both palms fully open = all 5 fingers up on both hands
        if sum(fingers_h1) == 5 and sum(fingers_h2) == 5:
            return ("BOTH_PALMS", 1.0, 2)

    # ── Single hand classification (use first detected hand) ────────────────
    hand = landmarks[0]
    fingers = _get_finger_states(hand)

    # ── OPEN PALM — all 5 fingers up ────────────────────────────────────────
    if sum(fingers) == 5:
        return ("OPEN_PALM", 0.95, hand_count)

    # ── THUMBS UP — only thumb up, all others curled ────────────────────────
    if fingers[0] and not any(fingers[1:]):
        # Extra check: thumb tip clearly above wrist
        if hand[4].y < hand[0].y:
            return ("THUMBS_UP", 0.95, hand_count)

    # ── INDEX FINGER ONLY — only index up ───────────────────────────────────
    if not fingers[0] and fingers[1] and not fingers[2] \
       and not fingers[3] and not fingers[4]:
        return ("INDEX_UP", 0.92, hand_count)

    # ── PINKY ONLY — only pinky up ──────────────────────────────────────────
    if not fingers[0] and not fingers[1] and not fingers[2] \
       and not fingers[3] and fingers[4]:
        return ("PINKY_UP", 0.92, hand_count)

    # ── SWIPE DETECTION — tracks index fingertip across frames ──────────────
    index_tip_x = hand[8].x   # normalized x position of index fingertip

    _swipe_history.append(index_tip_x)
    if len(_swipe_history) > SWIPE_HISTORY_LENGTH:
        _swipe_history.pop(0)

    if len(_swipe_history) == SWIPE_HISTORY_LENGTH:
        movement = _swipe_history[-1] - _swipe_history[0]  # total x movement

        if movement > SWIPE_THRESHOLD:
            # Moving right in camera = actual swipe right
            _swipe_history.clear()
            return ("SWIPE_RIGHT", 0.90, hand_count)

        elif movement < -SWIPE_THRESHOLD:
            # Moving left in camera = actual swipe left
            _swipe_history.clear()
            return ("SWIPE_LEFT", 0.90, hand_count)

    # ── UNKNOWN — hand detected but no gesture matched ──────────────────────
    return ("UNKNOWN", 0.0, hand_count)
