import cv2
import numpy as np


def unmatched_part_detection(frame_bgr, template_ok_gray, template_not_ok_gray,
                 threshold_ok=0.80, threshold_not_ok=0.80,
                 max_detections=10):
    """
    Template-match 'OK' and 'Not OK' components in a frame.

    Inputs:
      - frame_bgr:        BGR image (numpy array)
      - template_ok_gray: grayscale template image for OK part (numpy array)
      - template_not_ok_gray: grayscale template image for Not OK part (numpy array)

    Returns:
      - status: "OK", "NOT_OK", or "NONE"
      - annotated_frame_bgr: frame with boxes/labels
      - detections: list of dicts {label, x, y, w, h, score}
    """

    if frame_bgr is None:
        raise ValueError("frame_bgr is None")

    if template_ok_gray is None or template_not_ok_gray is None:
        raise ValueError("Templates must not be None (load them with cv2.imread(..., 0))")

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    detections = []

    # Helper to run template match and collect top hits
    def _match_and_collect(template_gray, label, thresh, box_color):
        h, w = template_gray.shape[:2]

        res = cv2.matchTemplate(gray_frame, template_gray, cv2.TM_CCOEFF_NORMED)

        # Get candidate locations above threshold
        ys, xs = np.where(res >= thresh)

        # Build list with scores
        scored = []
        for (x, y) in zip(xs, ys):
            scored.append((float(res[y, x]), x, y))

        # Sort by score desc and keep top N (simple suppression)
        scored.sort(reverse=True, key=lambda t: t[0])

        picked = []
        for score, x, y in scored:
            # naive overlap suppression (keeps boxes from stacking heavily)
            overlap = False
            for _, px, py in picked:
                if abs(x - px) < w * 0.5 and abs(y - py) < h * 0.5:
                    overlap = True
                    break
            if not overlap:
                picked.append((score, x, y))
            if len(picked) >= max_detections:
                break

        # Draw + store detections
        for score, x, y in picked:
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), box_color, 2)
            cv2.putText(frame_bgr, f"{label} {score:.2f}",
                        (x, max(0, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            detections.append({
                "label": label,
                "x": int(x), "y": int(y),
                "w": int(w), "h": int(h),
                "score": score
            })

    # Run both matches
    _match_and_collect(template_ok_gray, "OK", threshold_ok, (0, 255, 0))
    _match_and_collect(template_not_ok_gray, "NOT_OK", threshold_not_ok, (0, 0, 255))

    # Decide overall status
    labels = {d["label"] for d in detections}
    if "NOT_OK" in labels:
        status = "NOT_OK"
    elif "OK" in labels:
        status = "OK"
    else:
        status = "NONE"

    return status, frame_bgr, detections


def load_template_gray(path):
    """
    Convenience loader: loads a template image in grayscale.
    """
    t = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if t is None:
        raise FileNotFoundError(f"Template not found or unreadable: {path}")
    return t
