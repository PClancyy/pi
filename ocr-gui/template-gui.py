from tkinter import *
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import cv2
import numpy as np
import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
from unmatched_part_detection import unmatched_part_detection
# Create the main application window
root = Tk()
root.title("Industrial Vision App")
root.geometry("1600x1000")
root.configure(bg="blue")

def component_id(frame, template_ok, template_not_ok):
    w_ok, h_ok = template_ok.shape[::-1]
    w_not_ok, h_not_ok = template_not_ok.shape[::-1]
    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Perform template matching for "OK" part
  res_ok = cv2.matchTemplate(gray_frame, template_ok, cv2.TM_CCOEFF_NORMED)
    threshold_ok = 0.8
    loc_ok = np.where(res_ok >= threshold_ok)
    # Perform template matching for "Not OK" part
    res_not_ok = cv2.matchTemplate(gray_frame, template_not_ok, cv2.TM_CCOEFF_NORMED)
    threshold_not_ok = 0.8
    loc_not_ok = np.where(res_not_ok >= threshold_not_ok)
    # Draw rectangles for "OK" part
    for pt in zip(*loc_ok[::-1]):
        cv2.rectangle(frame, pt, (pt[0] + w_ok, pt[1] + h_ok), (0, 255, 0), 2)
        cv2.putText(frame, 'OK', pt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    # Draw rectangles for "Not OK" part
    for pt in zip(*loc_not_ok[::-1]):
        cv2.rectangle(frame, pt, (pt[0] + w_not_ok, pt[1] + h_not_ok), (0, 0, 255), 2)
       cv2.putText(frame, 'Not OK', pt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return  frame
# Function to close the window
def close_window():
    root.destroy()
# Create labels
company_label = Label(root, text="KMAKGA Corporation Ltd",
                borderwidth=5, relief="ridge",
                font=("Arial Black", 24),fg="red", bg="dark blue")
company_label.grid(row=0,column=0,columnspan=4,padx=30,pady=0,sticky="ew")
version_label = Label(root, text="Version 1.0",bg="blue")
version_label.grid(row=1,column=2,padx=0,pady=0,sticky="e")
vision_label = Label(root, text="Vision System", font=("Helvetica", 16,"bold"), fg="red", bg="blue")
vision_label.grid(row=2, column=0, columnspan=3, padx=0, pady=10, sticky="ew")
# Create a frame to hold the canvases
frame = Frame(root, width=800, height=800, relief="ridge", borderwidth=1,bg="blue")
frame.grid(row=3,column=0,padx=10,pady=0)
# Create canvases
video_canvas1 = Canvas(frame, borderwidth=2, width=500, height=400, bg="blue")
video_canvas1.grid(row=3,column=0,padx=5,pady=5)
video_canvas2 = Canvas(frame, borderwidth=2, width=500, height=400, bg="blue")
video_canvas2.grid(row=3,column=1,padx=5,pady=5)
video_canvas1.create_text(80, 10, text="Video Feed", font=("Helvetica", 10), anchor="ne")
video_canvas2.create_text(110, 10, text="Image with detected parts", font=("Helvetica", 10), anchor="ne")
# create a close button
close_button = Button(root, width=15, height=2, borderwidth=2, relief="ridge", text="Exit", command=close_window)
close_button.grid(row=4, column=0, columnspan=2, padx=0, pady=50, sticky="n")
# Load the template images
template_ok = cv2.imread("template_ok.jpg")
template_not_ok = cv2.imread("template_not_ok.jpg")
# Function to update the video canvas with webcam feed
def update_video_canvas():
   for frame in camera.capture_continuous(cap, format='bgr', use_video_port=True):
      # Display original video in the first canvas
      orig_photo = ImageTk.PhotoImage(image= Image.fromarray(frame))
      video_canvas1.create_image(0, 30, image=orig_photo, anchor=NW)
      video_canvas1.photo = orig_photo
      # Matched parts detection
      parts_match_img = unmatched_part_detection(frame, template_ok, template_not_ok)
      parts_img = ImageTk.PhotoImage(image=  Image.fromarray(parts_match_img))
      video_canvas2.create_image(0, 30, image=parts_img, anchor=NW)
      video_canvas2.photo = parts_img
      video_canvas1.after(10, update_video_canvas)
       cap.truncate(0)
# Open the Pi cam
camera = PiCamera()
cap = PiRGBArray(camera)
# Call the update_video_canvas function to start displaying the video feed
update_video_canvas()
# Start the tkinter main loop
root.mainloop()
