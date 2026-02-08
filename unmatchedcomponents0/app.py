from tkinter import *
import cv2
from PIL import Image, ImageTk
from picamera2 import Picamera2

from unmatched_part_detection import unmatched_part_detection

# ---------------- UI SETUP ----------------
root = Tk()
root.title("Industrial Vision App")
root.geometry("1600x1000")
root.configure(bg="blue")

def close_window():
    try:
        picam2.stop()
    except Exception:
        pass
    root.destroy()

company_label = Label(
    root,
    text="ProcureInt Ltd",
    borderwidth=5,
    relief="ridge",
    font=("Arial Black", 24),
    fg="red",
    bg="dark blue"
)
company_label.grid(row=0, column=0, columnspan=4, padx=30, pady=0, sticky="ew")

version_label = Label(root, text="Version 1.0", bg="blue")
version_label.grid(row=1, column=2, padx=0, pady=0, sticky="e")

vision_label = Label(
    root,
    text="Vision System",
    font=("Helvetica", 16, "bold"),
    fg="red",
    bg="blue"
)
vision_label.grid(row=2, column=0, columnspan=3, padx=0, pady=10, sticky="ew")

frame_ui = Frame(root, width=800, height=800, relief="ridge", borderwidth=1, bg="blue")
frame_ui.grid(row=3, column=0, padx=10, pady=0)

video_canvas1 = Canvas(frame_ui, borderwidth=2, width=500, height=400, bg="black")
video_canvas1.grid(row=0, column=0, padx=5, pady=5)

video_canvas2 = Canvas(frame_ui, borderwidth=2, width=500, height=400, bg="black")
video_canvas2.grid(row=0, column=1, padx=5, pady=5)

video_canvas1.create_text(80, 10, text="Video Feed", font=("Helvetica", 10), anchor="ne", fill="white")
video_canvas2.create_text(160, 10, text="Image with detected parts", font=("Helvetica", 10), anchor="ne", fill="white")

close_button = Button(
    root,
    width=15,
    height=2,
    borderwidth=2,
    relief="ridge",
    text="Exit",
    command=close_window
)
close_button.grid(row=4, column=0, columnspan=2, padx=0, pady=50, sticky="n")

# ---------------- LOAD TEMPLATES ----------------
template_ok = cv2.imread("template_ok.jpeg", cv2.IMREAD_GRAYSCALE)
template_not_ok = cv2.imread("template_not_ok.jpeg", cv2.IMREAD_GRAYSCALE)

if template_ok is None:
    raise FileNotFoundError("template_ok.jpg not found (must be in same folder as unmatched_app.py)")
if template_not_ok is None:
    raise FileNotFoundError("template_not_ok.jpg not found (must be in same folder as unmatched_app.py)")

# ---------------- CAMERA SETUP (Pi 5) ----------------
picam2 = Picamera2()
picam2.configure(
    picam2.create_video_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
)
picam2.start()

# Keep references so Tkinter doesn't garbage-collect images
img1_ref = None
img2_ref = None

def update_video_canvas():
    global img1_ref, img2_ref

    # Capture RGB frame from camera
    frame_rgb = picam2.capture_array()
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    # Original feed display
    img1_ref = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
    video_canvas1.delete("all")
    video_canvas1.create_image(0, 0, image=img1_ref, anchor=NW)

    status, processed_bgr, detections = unmatched_part_detection(
        frame_bgr, template_ok, template_not_ok
    )

    processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

    img2_ref = ImageTk.PhotoImage(Image.fromarray(processed_rgb))
    video_canvas2.delete("all")
    video_canvas2.create_image(0, 0, image=img2_ref, anchor=NW)

    # Schedule next frame (30ms ~ 33fps)
    root.after(30, update_video_canvas)

# Start loop
update_video_canvas()
root.mainloop()
