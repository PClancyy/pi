
import cv2
import easyocr

# Create the reader ONCE (global). This is the speed fix.
READER = easyocr.Reader(['en'], gpu=False)


def ocr_det(img_bgr):
    """
    Runs OCR on an image and draws boxes + text on a copy.
    Input:  BGR image
    Output: (annotated_bgr, text_string)
    """

    # Work on a copy so you don't mutate original frame
    out = img_bgr.copy()

    # EasyOCR is generally happier with RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    results = READER.readtext(img_rgb, paragraph=True)

    t_lines = []

    for item in results:
        # Depending on easyocr version, paragraph=True can return different shapes.
        # Common shapes:
        # 1) (bbox, text, conf)
        # 2) (bbox, text)
        if len(item) == 3:
            bbox, text, _conf = item
        else:
            bbox, text = item

        t_lines.append(text)

        # bbox is 4 points: tl,tr,br,bl (floats)
        tl, tr, br, bl = bbox
        tl = (int(tl[0]), int(tl[1]))
        br = (int(br[0]), int(br[1]))

        cv2.rectangle(out, tl, br, (0, 0, 255), 2)
        cv2.putText(out, text, (tl[0], max(0, tl[1] - 5)),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

    t = "\n".join(t_lines)
    return out, t
