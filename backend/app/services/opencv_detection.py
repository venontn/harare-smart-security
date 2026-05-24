"""Real OpenCV motion and object-region detection on uploaded images and video."""

import base64
import tempfile
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
ALLOWED_VIDEO = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def _encode_frame(frame: np.ndarray, max_width: int = 640) -> str:
    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / w
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
    _, buf = cv2.imencode(".jpg", frame)
    return base64.b64encode(buf).decode("ascii")


def analyze_image_bytes(data: bytes, filename: str = "upload.jpg") -> dict:
    """Detect motion regions by comparing against a blurred background model."""
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"success": False, "error": "Could not decode image"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Adaptive threshold highlights regions differing from local mean
    diff = cv2.absdiff(gray, cv2.medianBlur(gray, 51))
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    annotated = img.copy()
    regions = []
    min_area = max(500, (img.shape[0] * img.shape[1]) * 0.001)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        regions.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h), "area": int(area)})
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(annotated, "MOTION", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    motion_detected = len(regions) > 0
    coverage = sum(r["area"] for r in regions) / (img.shape[0] * img.shape[1]) * 100

    return {
        "success": True,
        "filename": filename,
        "motion_detected": motion_detected,
        "region_count": len(regions),
        "motion_coverage_percent": round(coverage, 2),
        "regions": regions[:20],
        "image_width": img.shape[1],
        "image_height": img.shape[0],
        "annotated_image_base64": _encode_frame(annotated),
        "message": (
            f"Motion detected: {len(regions)} region(s), {coverage:.1f}% frame coverage"
            if motion_detected
            else "No significant motion regions detected"
        ),
    }


def analyze_video_bytes(data: bytes, filename: str = "upload.mp4", max_frames: int = 60) -> dict:
    """Sample video frames and detect motion using frame differencing."""
    suffix = Path(filename).suffix.lower() or ".mp4"
    if suffix not in ALLOWED_VIDEO:
        suffix = ".mp4"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    cap = cv2.VideoCapture(tmp_path)
    if not cap.isOpened():
        Path(tmp_path).unlink(missing_ok=True)
        return {"success": False, "error": "Could not open video file"}

    fps = cap.get(cv2.CAP_PROP_FPS) or 15.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, total_frames // max_frames) if total_frames > 0 else 1

    prev_gray: Optional[np.ndarray] = None
    motion_frames = []
    frame_index = 0
    analyzed = 0

    while analyzed < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_index % step != 0:
            frame_index += 1
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prev_gray is not None:
            delta = cv2.absdiff(prev_gray, gray)
            thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            total_area = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 500)
            if total_area > frame.shape[0] * frame.shape[1] * 0.005:
                ann = frame.copy()
                for cnt in contours:
                    if cv2.contourArea(cnt) < 500:
                        continue
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(ann, (x, y), (x + w, y + h), (0, 0, 255), 2)
                motion_frames.append({
                    "frame": frame_index,
                    "timestamp_sec": round(frame_index / fps, 2),
                    "motion_area": int(total_area),
                    "preview_base64": _encode_frame(ann, max_width=480),
                })

        prev_gray = gray
        frame_index += 1
        analyzed += 1

    cap.release()
    Path(tmp_path).unlink(missing_ok=True)

    return {
        "success": True,
        "filename": filename,
        "total_frames": total_frames,
        "frames_analyzed": analyzed,
        "motion_events": len(motion_frames),
        "motion_detected": len(motion_frames) > 0,
        "events": motion_frames[:15],
        "message": (
            f"Motion in {len(motion_frames)} of {analyzed} sampled frames"
            if motion_frames
            else "No significant motion in sampled frames"
        ),
    }
