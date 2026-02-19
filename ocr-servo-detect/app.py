from tkinter import *
import cv2
from PIL import Image, ImageTk
from picamera2 import Picamera2
from ocr_det import ocr_det
import threading
import time

# NO pigpio imports
from gpiozero import AngularServo

# =============================
# SERVO CONTROLLER (NO pigpio)
# =============================
class ServoSweepController:
    """
    Silent-start, gpiozero-only servo sweep controller.
    - No twitch at startup (initial_angle=None + detach)
    - Servo only attaches when actually sweeping
    - Conservative pulse widths for MG90S/SG90
    - Cooldown + thread lock to prevent overlap
    """

    def __init__(
        self,
        gpio: int = 18,
        min_angle: int = -60,
        max_angle: int = 60,
        min_pulse_width: float = 0.0009,   # safer for MG90S
        max_pulse_width: float = 0.0021,
        cooldown_s: float = 2.0,
        keywords=None
    ):
        self.min_angle = int(min_angle)
        self.max_angle = int(max_angle)
        self.cooldown_s = float(cooldown_s)

        # Prevent gpiozero from sending ANY initial pulse
        self.servo = AngularServo(
            gpio,
            min_angle=self.min_angle,
            max_angle=self.max_angle,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width,
            initial_angle=None
        )

        # Keep servo silent until needed
        self.servo.detach()

        self._lock = threading.Lock()
        self._last_trigger = 0.0

        if keywords is None:
            keywords = ["not ok", "notok", "fail", "reject", "error", "defect", "defct"]
        self.keywords = [k.lower() for k in keywords]

    def center(self):
        """Attach, move to 0°, then detach again."""
        try:
            self.servo.angle = 0
            time.sleep(0.25)
            self.servo.detach()
        except Exception:
            pass

    def detach(self):
        try:
            self.servo.detach()
        except Exception:
            pass

    def sweep_async(self, step: int = 5, delay: float = 0.06):
        """Non-blocking sweep with auto-detach."""
        if not self._lock.acquire(blocking=False):
            return

        def run():
            try:
                # Attach + stabilise before movement
                self.servo.angle = 0
                time.sleep(0.25)

                # Sweep forward
                for a in range(self.min_angle, self.max_angle + 1, int(step)):
                    self.servo.angle = a
                    time.sleep(delay)

                time.sleep(0.15)

                # Sweep back
                for a in range(self.max_angle, self.min_angle - 1, -int(step)):
                    self.servo.angle = a
                    time.sleep(delay)

                # Return to centre
                self.servo.angle = 0
                time.sleep(0.25)

                # Fully silent again
                self.servo.detach()

            finally:
                self._lock.release()

        threading.Thread(target=run, daemon=True).start()

    def trigger_from_text(self, text: str):
        """Trigger sweep if OCR text contains defect keywords."""
        t = (text or "").lower()
        if not any(k in t for k in self.keywords):
            return

        now = time.time()
        if now - self._last_trigger < self.cooldown_s:
            return

        self._last_trigger = now
        self.sweep_async()
