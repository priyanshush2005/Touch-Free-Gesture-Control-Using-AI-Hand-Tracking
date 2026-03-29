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

        #Window setup
        self.title("GestureWave AI")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(fg_color="#0f0f1a")

        #State variables 
        self.camera_running   = False
        self.cap              = None
        self.current_gesture  = "NONE"
        self.current_conf     = 0.0
        self.current_hands    = 0
        self.fps              = 0
        self._fps_timer       = time.time()
        self._fps_counter     = 0
        self.last_action      = "—"

        #Build UI 
        self._build_sidebar()
        self._build_main_area()

        #Start camera automatically 
        self.after(500, self.start_camera)

        #Handle window close 
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    #UI building 

    def _build_sidebar(self):
        """Builds the left sidebar with all controls."""

        self.sidebar = ctk.CTkFrame(
            self, width=220, fg_color="#16213e",
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        #Logo/Title
        ctk.CTkLabel(
            self.sidebar,
            text="GestureWave AI",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#a5b4fc"
        ).pack(pady=(20, 2), padx=16, anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="Touch-Free Control",
            font=ctk.CTkFont(size=11),
            text_color="#4a5568"
        ).pack(padx=16, anchor="w")

        self._sidebar_divider()

        #Mode Selection
        ctk.CTkLabel(
            self.sidebar, text="MODE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#4a5568"
        ).pack(padx=16, anchor="w", pady=(10, 4))

        self.btn_media = ctk.CTkButton(
            self.sidebar,
            text="  Media Control",
            fg_color="#1e3a2f",
            hover_color="#1a4d3a",
            text_color="#34d399",
            font=ctk.CTkFont(size=13),
            anchor="w",
            command=self._set_media_mode,
            height=38,
            corner_radius=8
        )
        self.btn_media.pack(padx=12, pady=3, fill="x")

        self.btn_pres = ctk.CTkButton(
            self.sidebar,
            text="  Presentation",
            fg_color="#1a1a2e",
            hover_color="#2d2d5e",
            text_color="#6b7280",
            font=ctk.CTkFont(size=13),
            anchor="w",
            command=self._set_presentation_mode,
            height=38,
            corner_radius=8
        )
        self.btn_pres.pack(padx=12, pady=3, fill="x")

        self._sidebar_divider()

        #Camera Status
        ctk.CTkLabel(
            self.sidebar, text="CAMERA",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#4a5568"
        ).pack(padx=16, anchor="w", pady=(10, 4))

        self.cam_status_label = ctk.CTkLabel(
            self.sidebar,
            text="  Starting...",
            font=ctk.CTkFont(size=12),
            text_color="#f59e0b",
            fg_color="#1a1a2e",
            corner_radius=6,
            height=32
        )
        self.cam_status_label.pack(padx=12, fill="x")

        self._sidebar_divider()

        #Gesture Map
        ctk.CTkLabel(
            self.sidebar, text="GESTURE MAP",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#4a5568"
        ).pack(padx=16, anchor="w", pady=(10, 6))

        gestures = [
            ("Open Palm",    "Play/Pause · Fullscreen"),
            ("Swipe Right",  "Next · Vol up"),
            ("Swipe Left",   "Prev · Vol down"),
            ("Index Up",     "Volume up (hold)"),
            ("Pinky Up",     "Volume down (hold)"),
            ("Thumbs Up",    "Switch mode"),
            ("Both Palms",   "Screenshot"),
        ]

        for gesture, action in gestures:
            row = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            row.pack(padx=12, fill="x", pady=1)
            ctk.CTkLabel(
                row, text=gesture,
                font=ctk.CTkFont(size=11),
                text_color="#9ca3af", width=90, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=action,
                font=ctk.CTkFont(size=10),
                text_color="#4a5568", anchor="w"
            ).pack(side="left", padx=(4, 0))

        self._sidebar_divider()

        #Stop button
        self.stop_btn = ctk.CTkButton(
            self.sidebar,
            text="Stop Camera",
            fg_color="#3b0f0f",
            hover_color="#5c1a1a",
            text_color="#fca5a5",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.stop_camera,
            height=38,
            corner_radius=8
        )
        self.stop_btn.pack(padx=12, pady=(8, 6), fill="x", side="bottom")

        self.start_btn = ctk.CTkButton(
            self.sidebar,
            text="Start Camera",
            fg_color="#0f3b1f",
            hover_color="#1a5c2e",
            text_color="#6ee7b7",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_camera,
            height=38,
            corner_radius=8
        )
        self.start_btn.pack(padx=12, pady=(0, 4), fill="x", side="bottom")


    
