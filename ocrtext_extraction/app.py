from tkinter import *
import cv2
from PIL import Image, ImageTk
from picamera2 import Picamera2
from ocr_det import ocr_det
import threading

# -----------------------------
# Tkinter Window Setup
# -----------------------------
root = Tk()
root.title("Industrial Vision App")
root.geometry("1600x1000")
root.configure(bg="blue")


def close_window():
    root.destroy()


company_label = Label(root, text="ProcureInt Ltd",
                      borderwidth=5, relief="ridge",
                      font=("Arial Black", 24), fg="red", bg="dark blue")
company_label.grid(row=0, column=0, columnspan=4, padx=30, pady=0, sticky="ew")

version_label = Label(root, text="Version 1.0", bg="blue")
version_label.grid(row=1, column=2, padx=0, pady=0, sticky="e")

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

video_canvas1.create_text(80, 10, text="Video Feed", font=("Helvetica", 10), anchor="ne")
video_canvas2.create_text(110, 10, text="Text detection", font=("Helvetica", 10), anchor="ne")

entry_frame = Frame(root, width=200, height=400, bg="blue")
entry = Text(entry_frame, borderwidth=2, relief="ridge", height=10, width=40)
label = Label(entry_frame, text='Detected Text', font=("Helvetica", 18), fg="black", bg="blue")
label.grid(row=0, column=0, padx=5, pady=25, sticky="n")
entry.grid(row=1, column=0, padx=5, pady=25, sticky="w")
entry_frame.grid(row=3, column=1, padx=5, pady=5)

close_button = Button(root, width=15, height=2, borderwidth=2,
                      relief="ridge", text="Exit", command=close_window)
close_button.grid(row=4, column=0, columnspan=2, padx=0, pady=50, sticky="n")

# -----------------------------
# Camera Setup (VIDEO MODE)
# -----------------------------
camera = Picamera2()
config = camera.create_video_configuration(main={"size": (640, 480)})
camera.configure(config)
camera.start()


# -----------------------------
# Smooth Video Loop (30 FPS)
# -----------------------------
def update_video_canvas():
    frame = camera.capture_array()

    # Convert to Tk image
    img = ImageTk.PhotoImage(Image.fromarray(frame))

    # Draw on canvas
    video_canvas1.create_image(0, 0, image=img, anchor=NW)
    video_canvas1.photo = img

    # Schedule next frame
    root.after(30, update_video_canvas)


# -----------------------------
# OCR Loop (runs in background)
# -----------------------------
def ocr_loop():
    frame = camera.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Run OCR (heavy)
    img_bgr, t = ocr_det(frame_bgr)

    # Convert for Tk
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    tk_img = ImageTk.PhotoImage(Image.fromarray(img_rgb))

    # Update OCR canvas
    video_canvas2.create_image(0, 0, image=tk_img, anchor=NW)
    video_canvas2.photo = tk_img

    # Update text box
    entry.delete("1.0", END)
    entry.insert(END, str(t))

    # Run OCR again in 1 second
    threading.Timer(1.0, ocr_loop).start()


# -----------------------------
# Start Loops
# -----------------------------
update_video_canvas()
ocr_loop()

root.mainloop()
