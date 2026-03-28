import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import time
from action_handler import get_palm_hold_progress, get_volume_percent
from mode_manager import get_mode

#Colors (BGR format for OpenCV)
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0  )
GREEN       = (0,   255, 180)
ORANGE      = (0,   165, 255)
PURPLE      = (255, 100, 150)
DARK_BG     = (20,  20,  20 )
GRAY        = (130, 130, 130)
RED         = (0,   0,   220)
YELLOW      = (0,   220, 220)

#Font Settings 
FONT        = cv2.FONT_HERSHEY_SIMPLEX
FONT_SMALL  = 0.5
FONT_MEDIUM = 0.7
FONT_LARGE  = 1.0
THICKNESS   = 2

#Internal State 
_last_gesture_displayed = "NONE"
_gesture_display_timer  = 0
GESTURE_DISPLAY_TIME    = 1.5   # seconds to keep gesture name on screen

