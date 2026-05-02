import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import sys # Add this to your imports at the top

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ── Model path (relative — works on any computer) ──────────────────────────
# MODEL_PATH = resource_path(os.path.join('models', 'hand_landmarker.task'))
# BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'models', 'hand_landmarker.task'))
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = resource_path(os.path.join('models', 'hand_landmarker.task'))

# ── MediaPipe setup ─────────────────────────────────────────────────────────
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)

# ── Hand skeleton connections ───────────────────────────────────────────────
CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),         # Thumb
    (0,5),(5,6),(6,7),(7,8),         # Index
    (0,9),(9,10),(10,11),(11,12),    # Middle
    (0,13),(13,14),(14,15),(15,16),  # Ring
    (0,17),(17,18),(18,19),(19,20),  # Pinky
    (5,9),(9,13),(13,17)             # Palm
]


def get_landmarks(frame):
    """
    Takes a raw BGR camera frame.
    Returns a list of hands, each hand is a list of 21 landmarks.
    Each landmark has .x .y .z (normalized 0-1).
    Returns empty list [] if no hands detected.
    """
    h, w, _ = frame.shape

    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Wrap in MediaPipe Image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Run detection
    result = detector.detect(mp_image)

    if not result.hand_landmarks:
        return []

    return result.hand_landmarks


def draw_landmarks(frame, landmarks):
    """
    Takes a frame and the landmarks returned by get_landmarks().
    Draws dots and skeleton lines on the frame.
    Returns the annotated frame.
    """
    h, w, _ = frame.shape

    for hand in landmarks:
        # Draw skeleton connection lines first (drawn under the dots)
        for start, end in CONNECTIONS:
            x1 = int(hand[start].x * w)
            y1 = int(hand[start].y * h)
            x2 = int(hand[end].x * w)
            y2 = int(hand[end].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 120, 255), 2)

        # Draw landmark dots on top
        for landmark in hand:
            cx = int(landmark.x * w)
            cy = int(landmark.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 180), -1)
            cv2.circle(frame, (cx, cy), 5, (0, 200, 120), 1)  # outline ring

    return frame


def get_hand_count(landmarks):
    """
    Returns how many hands are currently detected (0, 1, or 2).
    Useful for the two-hand screenshot feature.
    """
    return len(landmarks)
