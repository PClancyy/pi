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
    gpiozero-only (no pigpio) sweep controller.
    - conservative pulse widths
    - narrower angles to reduce buzz
    - cooldown + non-blocking thread
    - detach after sweep to reduce idle jitter
    """
    def __init__(
        self,
        gpio: int = 18,              # GPIO18 = physical pin 12
        min_angle: int = -60,
        max_angle: int = 60,
        min_pulse_width: float = 0.0010,   # 1.0ms
        max_pulse_width: float = 0.0020,   # 2.0ms
        cooldown_s: float = 2.0,
        keywords=None
    ):
        self.min_angle = int(min_angle)
        self.max_angle = int(max_angle)
        self.cooldown_s = float(cooldown_s)

        self.servo = AngularServo(
            gpio,
            min_angle=self.min_angle,
            max_angle=self.max_angle,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width
        )
        self.servo.angle = 0

        self._lock = threading.Lock()
        self._last_trigger = 0.0

        if keywords is None:
            keywords = ["not ok", "notok", "fail", "reject", "error", "defect", "defct"]
        self.keywords = [k.lower() for k in keywords]

    def center(self):
        try:
            self.servo.angle = 0
        except Exception:
            pass

    def detach(self):
        try:
            self.servo.detach()
        except Exception:
            pass

    def sweep_async(self, step: int = 5, delay: float = 0.06):
        if not self._lock.acquire(blocking=False):
            return

        def run():
            try:
                self.servo.angle = 0
                time.sleep(0.2)

                for a in range(self.min_angle, self.max_angle + 1, int(step)):
                    self.servo.angle = a
                    time.sleep(delay)

                time.sleep(0.15)

                for a in range(self.max_angle, self.min_angle - 1, -int(step)):
                    self.servo.angle = a
                    time.sleep(delay)

                self.servo.angle = 0
                time.sleep(0.2)

                # stop pulses to reduce random idle jitter
                self.detach()
            finally:
                self._lock.release()

        threading.Thread(target=run, daemon=True).start()

    def trigger_from_text(self, text: str):
        t = (text or "").lower()
        if not any(k in t for k in self.keywords):
            return

        now = time.time()
        if now - self._last_trigger < self.cooldown_s:
            return

        self._last_trigger = now
        self.sweep_async()


# =============================
# TKINTER APP
# =============================
root = Tk()
root.title("Industrial Vision App")
root.geometry("1600x1000")
root.configure(bg="blue")

# Create servo controller (PIN 12 => GPIO18)
servo_ctrl = ServoSweepController(gpio=18)

def close_window():
    try:
        camera.stop()
    except Exception:
        pass
    try:
        servo_ctrl.center()
        servo_ctrl.detach()
    except Exception:
        pass
    root.destroy()

# -----------------------------
# UI SETUP (unchanged)
# -----------------------------
company_label = Label(root, text="ProcureInt Ltd",
                      borderwidth=5, relief="ridge",
                      font=("Arial Black", 24), fg="red", bg="dark blue")
company_label.grid(row=0, column=0, columnspan=4, padx=30, pady=0, sticky="ew")

vision_label = Label(root, text="Vision System",
                     font=("Helvetica", 16, "bold"),
                     fg="red", bg="blue")
vision_label.grid(row=2, column=0, columnspan=3, padx=0, pady=10, sticky="ew")

frame = Frame(root, width=800, height=800, relief="ridge", borderwidth=1, bg="blue")
frame.grid(row=3, column=0, padx=10, pady=0)

video_canvas1 = Canvas(frame, borderwidth=2, width=500, height=400, bg="blue")
video_canvas1.grid(row=3, column=0, padx=5, pady=5)

video_canvas2 = Canvas(frame, borderwidth=2, width=500, height=400, bg="blue")
video_canvas2.grid(row=3, column=1, padx=5, pady=5)

entry_frame = Frame(root, width=200, height=400, bg="blue")
entry = Text(entry_frame, borderwidth=2, relief="ridge", height=10, width=40)
entry.grid(row=1, column=0, padx=5, pady=25, sticky="w")
entry_frame.grid(row=3, column=1, padx=5, pady=5)

close_button = Button(root, width=15, height=2, borderwidth=2,
                      relief="ridge", text="Exit", command=close_window)
close_button.grid(row=4, column=0, columnspan=2, padx=0, pady=50, sticky="n")

# -----------------------------
# CAMERA SETUP
# -----------------------------
camera = Picamera2()
config = camera.create_video_configuration(main={"size": (640, 480)})
camera.configure(config)
camera.start()

# -----------------------------
# SMOOTH VIDEO LOOP (30 FPS)
# -----------------------------
def update_video():
    frame_rgb = camera.capture_array()
    img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
    video_canvas1.create_image(0, 0, image=img, anchor=NW)
    video_canvas1.photo = img
    root.after(30, update_video)

# -----------------------------
# OCR LOOP (every 1 second)
# -----------------------------
def ocr_loop():
    frame_rgb = camera.capture_array()
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    img_bgr, t = ocr_det(frame_bgr)

    # Trigger servo on "defect" / "not ok" etc.
    servo_ctrl.trigger_from_text(t)

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    tk_img = ImageTk.PhotoImage(Image.fromarray(img_rgb))
    video_canvas2.create_image(0, 0, image=tk_img, anchor=NW)
    video_canvas2.photo = tk_img

    entry.delete("1.0", END)
    entry.insert(END, t)

    root.after(1000, ocr_loop)

# START LOOPS
update_video()
ocr_loop()
root.mainloop()
