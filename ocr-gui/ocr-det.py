
# Create the reader ONCE (huge speed win)
reader = easyocr.Reader(['en'], gpu=False)

