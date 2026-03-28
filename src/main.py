import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import time
import threading
import customtkinter as ctk
from PIL import Image, ImageTk

from handDetection      import get_landmarks, draw_landmarks, get_hand_count
from gesture_classifier import classify
from action_handler     import execute, get_palm_hold_progress, get_volume_percent
from mode_manager       import get_mode, switch_mode, reset
from overlay            import draw_all

#App theme 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

#Window Size 

WIN_W  = 1100
WIN_H  = 660
CAM_W  = 860
CAM_H  = 580
