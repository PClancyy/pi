import cv2
import numpy as np

def detect_thread_quality(image_bgr):
    status = "Unknown"

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    valid = []
    for c in contours:
        area = cv2.contourArea(c)
        if 100 < area < 1000:
            valid.append(c)

    centers = []
    for c in valid:
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centers.append((cx, cy))

    centers.sort(key=lambda p: p[0])  # left-to-right

    if len(centers) > 1:
        distances = [centers[i+1][0] - centers[i][0] for i in range(len(centers)-1)]
        avg = sum(distances) / len(distances)
        evenly = all(abs(d - avg) < 12 for d in distances)

        if evenly:
            status = "Good!"
            cv2.putText(image_bgr, "Threads evenly spaced", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            status = "Bad!"
            cv2.putText(image_bgr, "Threads NOT evenly spaced", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    for (x, y) in centers:
        cv2.circle(image_bgr, (x, y), 5, (0, 0, 255), -1)

    return status, image_bgr
