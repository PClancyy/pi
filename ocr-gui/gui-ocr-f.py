from tkinter import *
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

# -------------------------
# Branding / Theme (procureint)
# -------------------------
APP_NAME = "ProcureInt Vision Systems LTD"
BG = "#071A12"  # deep green/black
PANEL = "#0C2A1E"  # dark emerald panel
ACCENT = "#22C55E"  # vivid green
ACCENT2 = "#16A34A"  # darker green
TEXT = "#E8FFF1"  # near-white w/ green tint
MUTED = "#A7F3D0"  # soft mint

# Create the main application window
root = Tk()
root.title(f"{APP_NAME} • Vision OCR")
root.geometry("1600x1000")
root.configure(bg=BG)

def reset_view():
    global zoom_active
    if orig_img is None or annotated_img is None:
        return
    show_on_canvas(video_canvas1, orig_img, CANVAS_W, CANVAS_H, zoom=1.0)
    show_on_canvas(video_canvas2, annotated_img, CANVAS_W, CANVAS_H, zoom=1.0)
    zoom_active = False

def _draw_callout(img, tl, br, text, color=(34, 197, 94)):
    h, w = img.shape[:2]
    x1, y1 = tl
    x2, y2 = br
    anchor = (x2, y1)

    margin = 12
    label_x = x2 + 30
    label_y = y1 - 10

    if label_x > w - 200:
        label_x = max(margin, x1 - 220)
    if label_y < margin:
        label_y = min(h - margin, y2 + 30)

    max_chars = 24
    lines = []
    s = text.strip()
    while len(s) > max_chars:
        cut = s.rfind(" ", 0, max_chars)
        if cut == -1:
            cut = max_chars
        lines.append(s[:cut].strip())
        s = s[cut:].strip()
    if s:
        lines.append(s)

    font = cv2.FONT_HERSHEY_PLAIN
    font_scale = 1.2
    thickness = 2
    pad = 6

    line_sizes = [cv2.getTextSize(line, font, font_scale, thickness)[0] for line in lines]
    text_w = max((sz[0] for sz in line_sizes), default=0)
    text_h = sum((sz[1] for sz in line_sizes), 0) + (len(lines) - 1) * 6

    box_w = text_w + pad * 2
    box_h = text_h + pad * 2

    label_x = min(max(margin, label_x), w - box_w - margin)
    label_y = min(max(margin + box_h, label_y + box_h), h - margin)
    top_left = (label_x, label_y - box_h)
    bottom_right = (label_x + box_w, label_y)

    cv2.rectangle(img, top_left, bottom_right, (4, 17, 11), -1)
    cv2.rectangle(img, top_left, bottom_right, color, 2)

    if anchor[0] >= bottom_right[0]:
        start = (bottom_right[0], (top_left[1] + bottom_right[1]) // 2)
    else:
        start = (top_left[0], (top_left[1] + bottom_right[1]) // 2)

    cv2.arrowedLine(img, start, anchor, color, 2, tipLength=0.25)

    y_cursor = top_left[1] + pad + (line_sizes[0][1] if lines else 12)
    for i, line in enumerate(lines):
        cv2.putText(img, line, (top_left[0] + pad, y_cursor),
                    font, font_scale, color, thickness, cv2.LINE_AA)
        y_cursor += (line_sizes[i][1] if i < len(line_sizes) else 12) + 6


def ocr_det(img_bgr):
    """
    returns:
      annotated_bgr, text(str), boxes(list)
    boxes item: {"tl":(x,y), "br":(x,y), "text":str}
    """
    annotated = img_bgr.copy()
    results = reader.readtext(annotated, paragraph=False)

    color = (34, 197, 94)
    text_out = []
    boxes = []

    for item in results:
        if len(item) == 3:
            bbox, text, conf = item
        else:
            bbox, text = item

        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        br = (int(br[0]), int(br[1]))

        text_out.append(text)
        boxes.append({"tl": tl, "br": br, "text": text})

        cv2.rectangle(annotated, tl, br, color, 2)
        _draw_callout(annotated, tl, br, text, color=color)

    return annotated, "\n".join(text_out), boxes


def close_window():
    root.destroy()


# -------------------------
# Header
# -------------------------
company_label = Label(
    root,
    text=APP_NAME,
    borderwidth=2,
    relief="ridge",
    font=("Arial Black", 30),
    fg=ACCENT,
    bg=PANEL,
    padx=12,
    pady=8
)
company_label.grid(row=0, column=0, columnspan=4, padx=30, pady=(18, 6), sticky="ew")

version_label = Label(root, text="Version 1.0", bg=BG, fg=MUTED, font=("Helvetica", 12))
version_label.grid(row=1, column=2, padx=0, pady=0, sticky="e")

vision_label = Label(
    root,
    text="Vision System • Image OCR",
    font=("Helvetica", 16, "bold"),
    fg=TEXT,
    bg=BG
)
vision_label.grid(row=2, column=0, columnspan=3, padx=0, pady=10, sticky="ew")

# -------------------------
# Main frame holding canvases
# -------------------------
frame = Frame(root, width=800, height=800, relief="ridge", borderwidth=2, bg=PANEL)
frame.grid(row=3, column=0, padx=18, pady=0)

CANVAS_W = 900
CANVAS_H = 700

video_canvas1 = Canvas(
    frame, width=CANVAS_W, height=CANVAS_H,
    bg="#04110B", highlightthickness=2, highlightbackground="#123C2A"
)
video_canvas1.grid(row=0, column=0, padx=12, pady=12)

video_canvas2 = Canvas(
    frame, width=CANVAS_W, height=CANVAS_H,
    bg="#04110B", highlightthickness=2, highlightbackground="#123C2A"
)
video_canvas2.grid(row=0, column=1, padx=12, pady=12)

video_canvas1.create_text(12, 12, text="Original", fill=MUTED, font=("Helvetica", 12, "bold"), anchor="nw")
video_canvas2.create_text(12, 12, text="OCR Annotated", fill=MUTED, font=("Helvetica", 12, "bold"), anchor="nw")

# -------------------------
# Text output panel
# -------------------------
entry_frame = Frame(root, width=200, height=400, bg=BG)
label = Label(entry_frame, text="Detected Text", font=("Helvetica", 18, "bold"), fg=TEXT, bg=BG)
label.grid(row=0, column=0, padx=10, pady=(20, 8), sticky="w")

entry = Text(entry_frame, borderwidth=0, relief="flat", height=14, width=46,
             bg="#04110B", fg=TEXT, insertbackground=TEXT, highlightthickness=2,
             highlightbackground="#123C2A", font=("Consolas", 13))
entry.grid(row=1, column=0, padx=10, pady=10, sticky="w")

entry_frame.grid(row=3, column=1, padx=8, pady=5, sticky="n")

# -------------------------
# Helpers
# -------------------------

# globals to hold current images/results
orig_img = None  # BGR
annotated_img = None  # BGR
ocr_boxes = []  # list of {"tl","br","text"}
zoom_active = False


def canvas_to_image_xy(canvas, cx, cy):
    xf = canvas_xform.get(canvas)
    if not xf:
        return None

    x = cx - xf["ox"]
    y = cy - xf["oy"]
    if x < 0 or y < 0:
        return None

    denom = xf["display_scale"] * xf["zoom"]
    if denom <= 0:
        return None

    ix = int(x / denom)
    iy = int(y / denom)

    # clamp to image
    ix = max(0, min(xf["orig_w"] - 1, ix))
    iy = max(0, min(xf["orig_h"] - 1, iy))
    return ix, iy


def find_box_at(ix, iy, boxes):
    for b in boxes:
        (x1, y1) = b["tl"]
        (x2, y2) = b["br"]
        if x1 <= ix <= x2 and y1 <= iy <= y2:
            return b
    return None


def crop_roi(img_bgr, tl, br, pad=40):
    h, w = img_bgr.shape[:2]
    x1, y1 = tl
    x2, y2 = br
    x1 = max(0, x1 - pad)
    y1 = max(0, y1 - pad)
    x2 = min(w - 1, x2 + pad)
    y2 = min(h - 1, y2 + pad)
    return img_bgr[y1:y2 + 1, x1:x2 + 1]


canvas_xform = {}


def on_annotated_click(event):
    global zoom_active

    if orig_img is None or annotated_img is None or not ocr_boxes:
        return

    pt = canvas_to_image_xy(video_canvas2, event.x, event.y)
    if pt is None:
        return

    ix, iy = pt
    hit = find_box_at(ix, iy, ocr_boxes)
    if not hit:
        return

    # Crop ROI from both original + annotated for consistent zoom view
    roi_orig = crop_roi(orig_img, hit["tl"], hit["br"], pad=60)
    roi_anno = crop_roi(annotated_img, hit["tl"], hit["br"], pad=60)

    # Show zoomed ROI (fill canvases)
    show_on_canvas(video_canvas1, roi_orig, CANVAS_W, CANVAS_H, zoom=1.0)
    show_on_canvas(video_canvas2, roi_anno, CANVAS_W, CANVAS_H, zoom=1.0)

    # Update text panel to the clicked box text
    entry.delete("1.0", END)
    entry.insert(END, hit["text"])

    zoom_active = True


# after you create video_canvas2:
video_canvas2.bind("<Button-1>", on_annotated_click)


def show_on_canvas(canvas, img_bgr, CANVAS_W, CANVAS_H, zoom=1.0):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]

    # display zoom first (inspector zoom)
    zw, zh = int(w * zoom), int(h * zoom)
    img_zoomed = cv2.resize(img_rgb, (zw, zh), interpolation=cv2.INTER_CUBIC)

    # fit to canvas with letterboxing
    scale = min(CANVAS_W / zw, CANVAS_H / zh)
    fw, fh = int(zw * scale), int(zh * scale)
    img_fit = cv2.resize(img_zoomed, (fw, fh), interpolation=cv2.INTER_AREA)

    bg = Image.new("RGB", (CANVAS_W, CANVAS_H), (4, 17, 11))
    pil = Image.fromarray(img_fit)
    ox = (CANVAS_W - fw) // 2
    oy = (CANVAS_H - fh) // 2
    bg.paste(pil, (ox, oy))

    photo = ImageTk.PhotoImage(bg)
    canvas.delete("img")
    canvas.create_image(0, 0, image=photo, anchor="nw", tags="img")
    canvas.photo = photo

    # Store transform: canvas -> zoomed-image -> original image
    # For click mapping, we want canvas -> original image coords:
    # canvas point -> subtract offsets -> divide by (scale*zoom)
    canvas_xform[canvas] = {
        "ox": ox, "oy": oy,
        "display_scale": scale,
        "zoom": zoom,
        "orig_w": w, "orig_h": h,
    }


def run_ocr_on_image(img_bgr):
    """
    Runs ocr_det on the image. Handles common RGB/BGR output differences safely.
    """
    # ocr_det likely expects BGR or RGB depending on your implementation.
    # We'll pass BGR as captured from OpenCV.
    annotated, text = ocr_det(img_bgr)

    # If annotated is RGB (common in PIL pipelines), convert to BGR for show_on_canvas
    # We can detect by assuming it's a numpy array of shape (H,W,3)
    try:
        if annotated is not None and hasattr(annotated, "shape") and annotated.shape[-1] == 3:
            # Heuristic: if it "looks" like RGB already, we can treat it as BGR->RGB conversion will still show,
            # but to be safer: assume annotated is RGB and convert to BGR.
            annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        else:
            annotated_bgr = annotated
    except Exception:
        annotated_bgr = annotated

    return annotated_bgr, text


# -------------------------
# Actions
# -------------------------
def load_image():
    global orig_img, annotated_img, ocr_boxes

    path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"), ("All files", "*.*")]
    )
    if not path:
        return

    img_bgr = cv2.imread(path)
    if img_bgr is None:
        entry.delete("1.0", END)
        entry.insert(END, "Could not load image.")
        return

    # ----- REPLACE YOUR EXISTING DISPLAY/OCR PART WITH THIS -----
    orig_img = img_bgr

    annotated_img, text, ocr_boxes = ocr_det(orig_img)

    show_on_canvas(video_canvas1, orig_img, CANVAS_W, CANVAS_H, zoom=1.0)
    show_on_canvas(video_canvas2, annotated_img, CANVAS_W, CANVAS_H, zoom=1.0)

    entry.delete("1.0", END)
    entry.insert(END, text)


# -------------------------
# Buttons
# -------------------------
btn_frame = Frame(root, bg=BG)
btn_frame.grid(row=4, column=0, columnspan=2, pady=26, sticky="w", padx=18)

load_button = Button(
    btn_frame, text="Load Image",
    width=14, height=2,
    bg=ACCENT2, fg="white",
    activebackground=ACCENT, activeforeground="white",
    borderwidth=0, font=("Helvetica", 14, "bold"),
    command=load_image
)
load_button.grid(row=0, column=0, padx=(0, 12))

close_button = Button(
    btn_frame, text="Exit",
    width=10, height=2,
    bg="#123C2A", fg=TEXT,
    activebackground="#1B5A3F", activeforeground=TEXT,
    borderwidth=0, font=("Helvetica", 14, "bold"),
    command=close_window
)
close_button.grid(row=0, column=1)

reset_button = Button(btn_frame, text="Reset View", command=reset_view)
reset_button.grid(row=0, column=2, padx=(12, 0))

root.mainloop()
