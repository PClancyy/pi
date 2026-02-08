from tkinter import *
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import easyocr

# -----------------------------
# OCR FUNCTION (your original)
# -----------------------------
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

# -----------------------------
# GUI SETUP
# -----------------------------
root = Tk()
root.title("OCR Vision App")
root.geometry("1200x700")
root.configure(bg="blue")

# Canvases
canvas_img = Canvas(root, width=500, height=500, bg="black")
canvas_img.grid(row=0, column=0, padx=20, pady=20)

canvas_text = Canvas(root, width=500, height=500, bg="black")
canvas_text.grid(row=0, column=1, padx=20, pady=20)

# -----------------------------
# LOAD + OCR FUNCTION
# -----------------------------
def load_and_ocr():
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
    )

    if not file_path:
        return

    # Load image with OpenCV
    img = cv2.imread(file_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Run OCR
    processed_img, text = ocr_det(img_rgb)

    # Resize for display
    processed_img = cv2.resize(processed_img, (500, 500))

    # Convert to Tkinter image
    tk_img = ImageTk.PhotoImage(Image.fromarray(processed_img))
    canvas_img.create_image(0, 0, image=tk_img, anchor=NW)
    canvas_img.image = tk_img

    # Display text
    canvas_text.delete("all")
    canvas_text.create_text(10, 10, text=text, anchor=NW, fill="white", font=("Arial", 14))

# -----------------------------
# BUTTON
# -----------------------------
btn = Button(root, text="Load Image + Run OCR", font=("Arial", 16),
             command=load_and_ocr, width=25, height=2)
btn.grid(row=1, column=0, columnspan=2, pady=20)

root.mainloop()
