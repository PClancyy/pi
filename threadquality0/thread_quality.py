import cv2
import numpy as np

def detect_thread_quality(image):
    """
    Detects whether threads are evenly spaced.
    Returns status string and annotated image.
    """

    status = "No threads detected"

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold
    _, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    centers = []

    # Filter contours by area and find centers
    for contour in contours:
        area = cv2.contourArea(contour)
        if 100 < area < 1000:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centers.append((cx, cy))

    # Evaluate spacing
    if len(centers) > 1:
        centers.sort(key=lambda c: c[0])
        distances = [centers[i+1][0] - centers[i][0]
                     for i in range(len(centers)-1)]
        avg_distance = sum(distances) / len(distances)

        if all(abs(d - avg_distance) < 12 for d in distances):
            status = "Good"
            color = (0, 255, 0)
        else:
            status = "Bad"
            color = (0, 0, 255)

        cv2.putText(
            image, f"Status: {status}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0, color, 2
        )

    # Draw detected thread centers
    for center in centers:
        cv2.circle(image, center, 5, (255, 0, 0), -1)

    return status, image


def main():
    # Open camera (libcamera backend)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Camera could not be opened")
        return

    print("Camera opened successfully. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Frame capture failed")
            break

        status, processed = detect_thread_quality(frame)

        cv2.imshow("Thread Inspection", processed)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
