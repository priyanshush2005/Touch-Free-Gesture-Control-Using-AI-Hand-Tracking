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
        
     

        #Status bar
        self.statusbar = ctk.CTkFrame(
            self.main_area,
            height=36,
            fg_color="#16213e",
            corner_radius=8
        )
        self.statusbar.pack(padx=12, pady=(0, 10), fill="x")
        self.statusbar.pack_propagate(False)

        # Camera dot + label
        self.status_cam = ctk.CTkLabel(
            self.statusbar,
            text="⬤  Camera off",
            font=ctk.CTkFont(size=11),
            text_color="#4a5568"
        )
        self.status_cam.pack(side="left", padx=14)

        # MediaPipe dot + label
        self.status_mp = ctk.CTkLabel(
            self.statusbar,
            text="⬤  MediaPipe ready",
            font=ctk.CTkFont(size=11),
            text_color="#818cf8"
        )
        self.status_mp.pack(side="left", padx=8)

        # Last action label
        self.status_action = ctk.CTkLabel(
            self.statusbar,
            text="Last action: —",
            font=ctk.CTkFont(size=11),
            text_color="#4a5568"
        )
        self.status_action.pack(side="right", padx=14)


    def _sidebar_divider(self):
        """Draws a thin divider line in the sidebar."""
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color="#1e2a3a"
        ).pack(fill="x", padx=12, pady=8)
    
    #MODE CONTROL
    

    def _set_media_mode(self):
        from mode_manager import _current_mode
        if get_mode() != "media":
            switch_mode()
        self._update_mode_buttons()

    def _set_presentation_mode(self):
        if get_mode() != "presentation":
            switch_mode()
        self._update_mode_buttons()

    def _update_mode_buttons(self):
        """Updates sidebar button colors to reflect current mode."""
        mode = get_mode()
        if mode == "media":
            self.btn_media.configure(
                fg_color="#1e3a2f", text_color="#34d399"
            )
            self.btn_pres.configure(
                fg_color="#1a1a2e", text_color="#6b7280"
            )
        else:
            self.btn_pres.configure(
                fg_color="#2d1f4a", text_color="#a5b4fc"
            )
            self.btn_media.configure(
                fg_color="#1a1a2e", text_color="#6b7280"
            )
    #Camera Control

    def start_camera(self):
        if self.camera_running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.cam_status_label.configure(
                text="  Camera not found", text_color="#f87171"
            )
            return
        self.camera_running = True
        self.cam_status_label.configure(
            text="  Active — 30fps", text_color="#34d399"
        )
        self.status_cam.configure(
            text="⬤  Camera running", text_color="#34d399"
        )
        # Run camera loop in a separate thread so UI doesn't freeze
        self.cam_thread = threading.Thread(
            target=self._camera_loop, daemon=True
        )
        self.cam_thread.start()

    def stop_camera(self):
        self.camera_running = False
        if self.cap:
            self.cap.release()
        self.cam_status_label.configure(
            text="  Stopped", text_color="#f59e0b"
        )
        self.status_cam.configure(
            text="⬤  Camera off", text_color="#4a5568"
        )
        # Clear camera feed display
        self.cam_label.configure(image=None, text="Camera stopped")
    
    # Main Camera Loop - Runs in the background 

    def _camera_loop(self):
        """
        Runs in a separate thread.
        Reads frames, detects gestures, executes actions,
        draws overlay, and pushes frame to UI label.
        """
        while self.camera_running:
            success, frame = self.cap.read()
            if not success:
                break

            #Flip frame (mirror effect — feels natural)
            frame = cv2.flip(frame, 1)

            #FPS calculation
            self._fps_counter += 1
            if time.time() - self._fps_timer >= 1.0:
                self.fps       = self._fps_counter
                self._fps_counter = 0
                self._fps_timer   = time.time()

            #Hand detection
            landmarks = get_landmarks(frame)

            #Gesture classification 
            gesture, confidence, hand_count = classify(landmarks)
            self.current_gesture = gesture
            self.current_conf    = confidence
            self.current_hands   = hand_count

            #Execute action
            execute(gesture, confidence, hand_count)

            #Update last action in status bar 
            if gesture not in ("NONE", "UNKNOWN"):
                self.last_action = gesture.replace("_", " ").title()
                self.after(0, self._update_status_bar)

            #Update mode buttons if mode changed
            self.after(0, self._update_mode_buttons)

            # Draw landmarks on frame
            frame = draw_landmarks(frame, landmarks)

            #Draw HUD overlay
            frame = draw_all(
                frame,
                gesture,
                confidence,
                hand_count,
                self.fps
            )

            #Convert OpenCV frame → CustomTkinter image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img   = Image.fromarray(frame_rgb)

            # Resize to fit the camera label
            label_w = self.cam_label.winfo_width()
            label_h = self.cam_label.winfo_height()
            if label_w > 10 and label_h > 10:
                pil_img = pil_img.resize(
                    (label_w, label_h), Image.LANCZOS
                )

            ctk_img = ctk.CTkImage(
                light_image=pil_img,
                dark_image=pil_img,
                size=(label_w, label_h)
            )

            # Push to UI — must use after() since we're in a thread
            self.after(0, self._update_cam_label, ctk_img)

        # Loop ended — camera stopped
        if self.cap:
            self.cap.release()


    def _update_cam_label(self, ctk_img):
        """Updates camera feed label with new frame — called from main thread."""
        self.cam_label.configure(image=ctk_img, text="")
        self.cam_label.image = ctk_img   # keep reference to prevent GC


    def _update_status_bar(self):
        """Updates last action text in status bar."""
        self.status_action.configure(
            text=f"Last action: {self.last_action}"
        )

    #Cleanup 

    def on_close(self):
        """Called when user closes the window."""
        self.camera_running = False
        if self.cap:
            self.cap.release()
        self.destroy()


#Entry point 
if __name__ == "__main__":
    reset()   # reset mode manager to defaults
    app = GestureWaveApp()
    app.mainloop()