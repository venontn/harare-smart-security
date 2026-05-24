"""Automatic Number Plate Recognition using OpenCV + EasyOCR."""

from __future__ import annotations

import base64
import re
from typing import List, Optional, Tuple

import cv2
import numpy as np

# Zimbabwe-style: 2-3 letters + 3-4 digits (e.g. AEA 1234, AFG 8891)
PLATE_REGEX = re.compile(r"^[A-Z]{2,3}\s?\d{3,4}$")

_reader = None


def get_ocr_reader():
    global _reader
    if _reader is None:
        import easyocr

        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader


def normalize_plate(text: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]", "", text.upper())
    # Insert space between letters and numbers
    m = re.match(r"^([A-Z]{2,3})(\d{3,4})$", cleaned)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return cleaned


def _decode_image(data: bytes) -> Optional[np.ndarray]:
    arr = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _encode_frame(frame: np.ndarray, max_width: int = 720) -> str:
    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / w
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
    _, buf = cv2.imencode(".jpg", frame)
    return base64.b64encode(buf).decode("ascii")


def find_plate_regions(image_bgr: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Detect candidate plate bounding boxes via morphology + aspect ratio."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    edged = cv2.dilate(edged, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    h_img, w_img = gray.shape
    min_area = (h_img * w_img) * 0.0003
    boxes = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area < min_area:
            continue
        aspect = w / float(h) if h else 0
        if 2.0 <= aspect <= 6.5 and h >= 12 and w >= 40:
            boxes.append((x, y, w, h))

    # Deduplicate overlapping boxes
    boxes.sort(key=lambda b: b[2] * b[3], reverse=True)
    filtered = []
    for box in boxes:
        x, y, w, h = box
        overlap = False
        for fx, fy, fw, fh in filtered:
            if abs(x - fx) < 20 and abs(y - fy) < 15:
                overlap = True
                break
        if not overlap:
            filtered.append(box)
    return filtered[:8]


def ocr_plate_crop(crop: np.ndarray) -> str:
    reader = get_ocr_reader()
    # Preprocess for OCR
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results = reader.readtext(thresh, detail=0, paragraph=False)
    text = " ".join(results).upper()
    return normalize_plate(text)


def analyze_plates_in_image(
    data: bytes,
    vehicle_db: List[Tuple[str, str, str, str]],
) -> dict:
    """
    vehicle_db: list of (plate_number, owner_name, status, notes)
    """
    img = _decode_image(data)
    if img is None:
        return {"success": False, "error": "Could not decode image"}

    annotated = img.copy()
    regions = find_plate_regions(img)
    detections = []

    # Full-frame OCR fallback
    try:
        reader = get_ocr_reader()
        full_results = reader.readtext(img, detail=0, paragraph=False)
        full_text = " ".join(full_results).upper()
    except Exception:
        full_text = ""

    candidates = list(regions)
    if not candidates:
        candidates = [(0, 0, img.shape[1], img.shape[0])]

    seen_plates = set()
    for x, y, w, h in candidates:
        pad = 4
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img.shape[1], x + w + pad)
        y2 = min(img.shape[0], y + h + pad)
        crop = img[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        try:
            plate_text = ocr_plate_crop(crop)
        except Exception:
            continue
        if not plate_text or len(plate_text) < 5:
            continue
        if not PLATE_REGEX.match(plate_text.replace(" ", "")) and not re.match(
            r"^[A-Z]{2,3}\d{3,4}$", plate_text.replace(" ", "")
        ):
            # Try extracting from noisy OCR
            m = re.search(r"[A-Z]{2,3}\s?\d{3,4}", plate_text.replace(" ", " "))
            if m:
                plate_text = normalize_plate(m.group(0))
            else:
                continue
        if plate_text in seen_plates:
            continue
        seen_plates.add(plate_text)

        db_match = None
        for db_plate, owner, status, notes in vehicle_db:
            if db_plate.replace(" ", "").upper() == plate_text.replace(" ", "").upper():
                db_match = {
                    "plate_number": db_plate,
                    "owner_name": owner,
                    "status": status,
                    "notes": notes,
                }
                break

        color = (0, 255, 0)
        alert = False
        if db_match and db_match["status"] in ("stolen", "wanted"):
            color = (0, 0, 255)
            alert = True

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = plate_text + (" ALERT" if alert else "")
        cv2.putText(annotated, label, (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        detections.append({
            "plate_text": plate_text,
            "bbox": {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
            "database_match": db_match,
            "alert": alert,
        })

    # Regex scan on full OCR text
    for token in re.findall(r"[A-Z]{2,3}\s?\d{3,4}", full_text):
        norm = normalize_plate(token)
        if norm in seen_plates:
            continue
        seen_plates.add(norm)
        db_match = None
        for db_plate, owner, status, notes in vehicle_db:
            if db_plate.replace(" ", "").upper() == norm.replace(" ", "").upper():
                db_match = {"plate_number": db_plate, "owner_name": owner, "status": status, "notes": notes}
                break
        detections.append({
            "plate_text": norm,
            "bbox": None,
            "database_match": db_match,
            "alert": db_match and db_match["status"] in ("stolen", "wanted"),
            "source": "full_frame_ocr",
        })

    alerts = [d for d in detections if d.get("alert")]

    return {
        "success": True,
        "plates_detected": len(detections),
        "detections": detections,
        "alert_count": len(alerts),
        "message": (
            f"Detected {len(detections)} plate(s), {len(alerts)} alert(s)"
            if detections
            else "No plates recognized — try a clearer front/rear vehicle image"
        ),
        "annotated_image_base64": _encode_frame(annotated),
    }
