from tkinter import *
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import time
from picamera2 import Picamera2
from thread_count import thread_count
import winsound
# Create the main application window
root = Tk()
root.title("Industrial Vision App")
root.geometry("1600x1000")
root.configure(bg="blue")
# Function to close the window
def close_window():
   root.destroy()
# Create labels
company_label = Label(root, text="ProcureInt Corporation Ltd",
                borderwidth=5, relief="ridge",
                font=("Arial Black", 24),fg="red", bg="dark blue")
company_label.grid(row=0, column=0, columnspan=4, padx=30, pady=0, sticky="ew")
version_label = Label(root, text="Version 1.0",bg="blue")
version_label.grid(row=1,column=2,padx=0,pady=0,sticky="e")
vision_label = Label(root, text="Vision System", font=("Helvetica", 16,"bold"), fg="red", bg="blue")
vision_label.grid(row=2, column=0, columnspan=3, padx=0, pady=10, sticky="ew")
# Create a frame to hold the canvases
frame = Frame(root, width=800, height=800, relief="ridge", borderwidth=1, bg="blue")
frame.grid(row=3,column=0,padx=10,pady=0)
# Create canvases
video_canvas1 = Canvas(frame, borderwidth=2, width=500, height=400, bg="blue")
video_canvas1.grid(row=3,column=0,padx=5,pady=5)
video_canvas2 = Canvas(frame, borderwidth=2, width=500, height=400, bg="blue")
video_canvas2.grid(row=3,column=1,padx=5,pady=5)
video_canvas1.create_text(80, 10, text="Video Feed", font=("Helvetica", 10), anchor="ne")
video_canvas2.create_text(110, 10, text="Thread Image", font=("Helvetica", 10), anchor="ne")
# Create a frame to hold the configuration options
entry_frame = Frame(root, width = 200, height = 400, bg="blue")
label1 = Label(entry_frame, text='Thread Count', font=("Helvetica", 18), fg="black", bg="blue")
entry = Text(entry_frame, borderwidth=2, relief="ridge", height=10, width=40)
label2 = Label(entry_frame, text=' ', font=("Helvetica", 18), fg="black", bg="blue")
label1.grid(row=0, column=0, padx=5, pady=25, sticky="n")
entry.grid(row=0, column=1, padx=5, pady=25, sticky="w")
label2.grid(row=3, column=0, columnspan=2, padx=5, pady=25, sticky="n")
entry_frame.grid(row=3, column=1, padx=5, pady=5)
# create a close button
close_button = Button(root, width=15, height=2, borderwidth=2, relief="ridge", text="Exit", command=close_window)
close_button.grid(row=4,column=0,columnspan=2,padx=0,pady=50,sticky="n")
# Function to update the video canvas with webcam feed
def update_video_canvas():
    # 1) Grab ONE frame from Picamera2
    frame_rgb = camera.capture_array()                 # RGB numpy array
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    # 2) Display original feed on canvas 1 (needs RGB)
    orig_photo = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
    video_canvas1.delete("all")
    video_canvas1.create_image(0, 30, image=orig_photo, anchor=NW)
    video_canvas1.photo = orig_photo  # keep reference

    # 3) Your processing (thread_count expects BGR usually)
    sumt, thresh_img = thread_count(frame_bgr, 202)

    # If thresh_img is grayscale, PIL can display it directly.
    # If it is BGR, convert to RGB first.
    if len(thresh_img.shape) == 3:
        thresh_rgb = cv2.cvtColor(thresh_img, cv2.COLOR_BGR2RGB)
        thresh_to_show = thresh_rgb
    else:
        thresh_to_show = thresh_img

    thread_photo = ImageTk.PhotoImage(Image.fromarray(thresh_to_show))
    video_canvas2.delete("all")
    video_canvas2.create_image(0, 30, image=thread_photo, anchor=NW)
    video_canvas2.photo = thread_photo  # keep reference

    # 4) Update UI status
    entry.delete("1.0", END)
    entry.insert(END, str(sumt))

    if sumt >= 20:
        label2.config(text="No fault is detected", fg="green")
    else:
        label2.config(text="Fault detected", fg="red")
        # winsound is Windows-only. On Pi, use a bell as fallback:
        try:
            import winsound
            winsound.Beep(440, 500)
            winsound.Beep(440, 500)
            winsound.Beep(440, 500)
        except Exception:
            print("\a", end="")  # terminal bell (if enabled)

    # 5) Schedule next frame (10–33ms is typical)
    video_canvas1.after(30, update_video_canvas)

# Open the Pi cam
camera = Picamera2()
camera.configure(camera.create_video_configuration(
    main={"format": "RGB888"}
))
frame_rgb = camera.capture_array()
# Call the update_video_canvas function to start displaying the video feed
update_video_canvas()
# Start the tkinter main loop
root.mainloop()