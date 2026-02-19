from tkinter import *
import cv2
from PIL import Image, ImageTk
from picamera2 import Picamera2
from ocr_det import ocr_det
import threading
import time

# NOTE: no pigpio, no AngularServo
from gpiozero import Servo


root = Tk()
root.title("Industrial Vision App")
root.geometry("1600x1000")
root.configure(bg="blue")

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

# -----------------------------
# SERVO SETUP (NO pigpio) — proven min/mid/max
# -----------------------------
SERVO_GPIO = 18  # physical pin 12
servo = Servo(SERVO_GPIO, min_pulse_width=0.0011, max_pulse_width=0.0019)
servo.detach()  # prevent idle jitter

_sweeping_lock = threading.Lock()
_last_trigger = 0.0
TRIGGER_COOLDOWN_S = 2.0
_last_was_bad = False

def servo_ack():
    """Non-blocking min/mid/max motion, then detach to avoid jitter."""
    if not _sweeping_lock.acquire(blocking=False):
        return

    def run():
        try:
            # Re-enable pulses
            servo.mid()
            time.sleep(0.2)

            servo.min()
            time.sleep(0.35)

            servo.mid()
            time.sleep(0.25)

            servo.max()
            time.sleep(0.35)

            servo.mid()
            time.sleep(0.25)

            # Stop pulses -> reduces random jitter at idle
            servo.detach()
        finally:
            _sweeping_lock.release()

    threading.Thread(target=run, daemon=True).start()

def trigger_servo_if_needed(ocr_text: str):
    """Trigger once when OCR text transitions from OK -> BAD."""
    global _last_trigger, _last_was_bad

    t = (ocr_text or "").lower()
    bad_keywords = ["defect", "defct", "not ok", "notok", "fail", "reject", "error"]
    is_bad = any(k in t for k in bad_keywords)

    if is_bad and not _last_was_bad:
        now = time.time()
        if now - _last_trigger >= TRIGGER_COOLDOWN_S:
            _last_trigger = now
            servo_ack()
            # optional UI flash
            vision_label.config(text="⚠️ DEFECT DETECTED", fg="yellow")
            root.after(1200, lambda: vision_label.config(text="Vision System", fg="red"))

    _last_was_bad = is_bad


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

    trigger_servo_if_needed(t)

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    tk_img = ImageTk.PhotoImage(Image.fromarray(img_rgb))
    video_canvas2.create_image(0, 0, image=tk_img, anchor=NW)
    video_canvas2.photo = tk_img

    entry.delete("1.0", END)
    entry.insert(END, t)

    root.after(1000, ocr_loop)

def close_window():
    try:
        camera.stop()
    except Exception:
        pass
    try:
        servo.mid()
        time.sleep(0.1)
        servo.detach()
    except Exception:
        pass
    root.destroy()

close_button = Button(root, width=15, height=2, borderwidth=2,
                      relief="ridge", text="Exit", command=close_window)
close_button.grid(row=4, column=0, columnspan=2, padx=0, pady=50, sticky="n")

# START LOOPS
update_video()
ocr_loop()
root.mainloop()
