from tkinter import *
import cv2
from PIL import Image, ImageTk
from picamera2 import Picamera2
from thread_quality import detect_thread_quality

root = Tk()
root.title("Industrial Vision App")
root.geometry("1200x800")
root.configure(bg="blue")

def close_window():
    picam2.stop()
    root.destroy()

Label(root, text="KMAKGA Corporation Ltd",
      borderwidth=5, relief="ridge",
      font=("Arial Black", 24), fg="red", bg="dark blue").pack(fill="x", padx=20, pady=10)

main_frame = Frame(root, bg="blue")
main_frame.pack(padx=10, pady=10)

video_canvas1 = Canvas(main_frame, borderwidth=2, width=500, height=400, bg="black")
video_canvas1.grid(row=0, column=0, padx=10, pady=10)

video_canvas2 = Canvas(main_frame, borderwidth=2, width=500, height=400, bg="black")
video_canvas2.grid(row=0, column=1, padx=10, pady=10)

status_frame = Frame(root, bg="blue")
status_frame.pack(pady=10)

Label(status_frame, text="Thread Quality", font=("Helvetica", 18), fg="black", bg="blue").grid(row=0, column=0, padx=10)
status_text = StringVar(value="...")
Label(status_frame, textvariable=status_text, font=("Helvetica", 18), fg="white", bg="blue").grid(row=0, column=1, padx=10)

Button(root, width=15, height=2, borderwidth=2, relief="ridge", text="Exit", command=close_window).pack(pady=20)

# ---- Camera setup (Pi 5 compatible) ----
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}))
picam2.start()

def update():
    frame_rgb = picam2.capture_array()   # RGB
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    # Original feed
    img1 = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
    video_canvas1.create_image(0, 0, image=img1, anchor=NW)
    video_canvas1.image = img1

    # Processed feed
    status, processed_bgr = detect_thread_quality(frame_bgr)
    processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

    img2 = ImageTk.PhotoImage(Image.fromarray(processed_rgb))
    video_canvas2.create_image(0, 0, image=img2, anchor=NW)
    video_canvas2.image = img2

    status_text.set(status)

    root.after(30, update)  # ~33fps

update()
root.mainloop()
