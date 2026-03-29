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

class GestureWaveApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        #Window Setup
        self.title("GestureWave AI")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(fg_color="#0f0f1a")

        #State Variable
        self.camera_running   = False
        self.cap              = None
        self.current_gesture  = "NONE"
        self.current_conf     = 0.0
        self.current_hands    = 0
        self.fps              = 0
        self._fps_timer       = time.time()
        self._fps_counter     = 0
        self.last_action      = "—"

        #Building UI
        self._build_sidebar()
        self._build_main_area()

        #Start camera automatically
        self.after(500, self.start_camera)

        #Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
