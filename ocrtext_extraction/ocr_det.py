import easyocr
import cv2

# Create the reader ONCE
reader = easyocr.Reader(['en'], gpu=False)

def ocr_det(img):
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
