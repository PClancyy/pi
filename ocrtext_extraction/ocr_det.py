import easyocr
import cv2
def ocr_det(img):
    # create a reader object and extract text from image
    reader = easyocr.Reader(['en'],gpu=False)
    results = reader.readtext(img,paragraph=True)
    # Create bounding box and display extracted text over the image
    t = ''
    for (bbox, text) in results:
        (tl, tr, br, bl) = bbox
        t += text  + '\n'
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        cv2.rectangle(img, tl, br, (0, 0, 255), 2)
        cv2.putText(img, text, (tl[0], tl[1]-5),
                    cv2.FONT_HERSHEY_PLAIN, 1,(0,0,255),2)
    return img, t