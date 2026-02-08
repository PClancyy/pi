from tkinter import *
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import datetime
from picamera2 import Picamera2
from ocr_det import ocr_det
# Create the main application window
root = Tk()
root.title("Industrial Vision App")
root.geometry("1600x1000")
root.configure(bg="blue")
# Function to close the window
def close_window():
    root.destroy()
# Create labels
company_label = Label(root, text="ProcureInt Ltd",
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
video_canvas2.create_text(110, 10, text="Text detection", font=("Helvetica", 10), anchor="ne")
# Create a frame to display the extracted text
entry_frame = Frame(root, width = 200, height = 400, bg="blue")
entry = Text(entry_frame, borderwidth=2, relief="ridge", height=10, width=40)
label = Label(entry_frame, text='Detected Text', font=("Helvetica", 18), fg="black", bg="blue")
label.grid(row=0, column=0, padx=5, pady=25, sticky="n")
entry.grid(row=1, column=0, padx=5, pady=25, sticky="w")
entry_frame.grid(row=3, column=1, padx=5, pady=5)
# create a close button
close_button = Button(root, width=15, height=2, borderwidth=2, relief="ridge", text="Exit", command = close_window)
close_button.grid(row=4, column=0, columnspan=2, padx=0, pady=50, sticky="n")
# Function to update the video canvas with webcam feed
def update_video_canvas():
   for frame in camera.capture_continuous(cap, format='bgr', use_video_port=True):
        # Display original video in the first canvas
        orig_photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
        video_canvas1.create_image(0, 30, image=orig_photo, anchor=NW)
        video_canvas1.photo = orig_photo
        # Text detection using easyocr
        img, t = ocr_det(frame)
        text_photo = ImageTk.PhotoImage(image = Image.fromarray(img))
        video_canvas2.create_image(0, 30, image=text_photo, anchor=NW)
        video_canvas2.photo = text_photo
    # Update the detected text to the text entry widget
   entry.delete(0.0, END)
   entry.insert(END, t)
   video_canvas1.after(10, update_video_canvas)
   cap.truncate(0)
# Open the Pi cam
camera = PiCamera()
cap = PiRGBArray(camera)
# Call the update_video_canvas function to start displaying the video feed
update_video_canvas()
# Start the tkinter main loop
root.mainloop()