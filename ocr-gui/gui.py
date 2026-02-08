from tkinter import *
from tkinter import filedialog
import cv2
import easyocr
from PIL import Image, ImageTk
import datetime

# Create the main application window
root = Tk()
root.title("ProcureInt Vision Systems")
root.geometry("1600x1000")
root.configure(bg="green")


def ocr_det(img):
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(img, paragraph=True)

    t = ''
    for (bbox, text) in results:
        (tl, tr, br, bl) = bbox
        t += text + '\n'

        tl = (int(tl[0]), int(tl[1]))
        br = (int(br[0]), int(br[1]))

        cv2.rectangle(img, tl, br, (0, 0, 255), 2)
        cv2.putText(img, text, (tl[0], tl[1] - 5),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

    return img, t


def close_window():
    root.destroy()


# Labels
company_label = Label(root, text="ProcureInt Vision Systems Ltd",
                      borderwidth=5, relief="ridge",
                      font=("Arial Black", 24), fg="red", bg="green")
company_label.grid(row=0, column=0, columnspan=4, padx=30, pady=0, sticky="ew")

version_label = Label(root, text="Version 1.0", bg="green")
version_label.grid(row=1, column=2, padx=0, pady=0, sticky="e")

vision_label = Label(root, text="Vision System", font=("Helvetica", 16, "bold"),
                     fg="red", bg="black")
vision_label.grid(row=2, column=0, columnspan=3, padx=0, pady=10, sticky="ew")

# Frame for canvases
frame = Frame(root, width=800, height=800, relief="ridge", borderwidth=1, bg="black")
frame.grid(row=3, column=0, padx=10, pady=0)

video_canvas1 = Canvas(frame, borderwidth=2, width=400, height=400, bg="black")
video_canvas1.grid(row=3, column=0, padx=5, pady=5)

video_canvas2 = Canvas(frame, borderwidth=2, width=400, height=400, bg="black")
video_canvas2.grid(row=3, column=1, padx=5, pady=5)

video_canvas1.create_text(80, 10, text="Video Feed", font=("Helvetica", 10), anchor="ne")
video_canvas2.create_text(110, 10, text="Edge detection", font=("Helvetica", 10), anchor="ne")


# Load image into canvas
def click():
    filename = filedialog.askopenfilename(
        initialdir="C:/Users/user/Pictures/",
        title="Select a file",
        filetypes=(("png files", "*.png"), ("all files", "*.*"))
    )
    if not filename:
        return

    img = Image.open(filename)
    img = img.resize((400, 400))
    img_tk = ImageTk.PhotoImage(img)

    video_canvas1.create_image(0, 30, image=img_tk, anchor=NW)
    video_canvas1.photo = img_tk  # prevent garbage collection


# Entry frame
entry_frame = Frame(root, width=200, height=600, bg="green")

mybutton = Button(entry_frame, width=20, height=2, borderwidth=2,
                  relief="ridge", text='Load Reference Image', command=click)
mybutton.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

labels = ["No. of pieces accepted:", "Delay time:", "No. of pieces rejected:"]
entries = [Entry(entry_frame, borderwidth=2, relief="ridge") for _ in range(3)]

for i, label_text in enumerate(labels):
    label = Label(entry_frame, text=label_text, font=("Helvetica", 18),
                  fg="black", bg="green")
    label.grid(row=i + 1, column=0, padx=5, pady=25, sticky="e")

    entry = entries[i]
    entry.grid(row=i + 1, column=1, padx=5, pady=25, sticky="w")

entry_frame.grid(row=3, column=2, padx=5, pady=5)

# Close button
close_button = Button(root, width=15, height=2, borderwidth=2,
                      relief="ridge", text="Exit", command=close_window)
close_button.grid(row=4, column=0, columnspan=2, padx=0, pady=50, sticky="n")


# Webcam feed
def update_video_canvas():
    ret, frame = cap.read()
    if ret:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_frame, 100, 200)

        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        edge_photo = ImageTk.PhotoImage(image=Image.fromarray(edges_rgb))
        video_canvas2.create_image(0, 30, image=edge_photo, anchor=NW)
        video_canvas2.photo = edge_photo

        dt = str(datetime.datetime.now())
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.putText(frame_rgb, dt, (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))

        orig_photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
        video_canvas1.create_image(0, 30, image=orig_photo, anchor=NW)
        video_canvas1.photo = orig_photo

        video_canvas1.after(10, update_video_canvas)


cap = cv2.VideoCapture(0)
update_video_canvas()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
