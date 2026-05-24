"""OpenCV YuNet + SFace facial recognition against watchlist embeddings."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"
YUNET_PATH = MODEL_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_PATH = MODEL_DIR / "face_recognition_sface_2021dec.onnx"

YUNET_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
SFACE_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_recognition_sface/face_recognition_sface_2021dec.onnx"
)

MATCH_THRESHOLD = 0.363  # OpenCV SFace recommended cosine distance threshold

_detector: Optional[cv2.FaceDetectorYN] = None
_recognizer: Optional[cv2.FaceRecognizerSF] = None


def ensure_models() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for path, url in ((YUNET_PATH, YUNET_URL), (SFACE_PATH, SFACE_URL)):
        if not path.exists():
            urllib.request.urlretrieve(url, path)


def _get_detector() -> cv2.FaceDetectorYN:
    global _detector
    ensure_models()
    if _detector is None:
        _detector = cv2.FaceDetectorYN.create(str(YUNET_PATH), "", (320, 320), 0.6, 0.3, 5000)
    return _detector


def _get_recognizer() -> cv2.FaceRecognizerSF:
    global _recognizer
    ensure_models()
    if _recognizer is None:
        _recognizer = cv2.FaceRecognizerSF.create(str(SFACE_PATH), "")
    return _recognizer


def _decode_image(data: bytes) -> Optional[np.ndarray]:
    arr = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _largest_face(faces: np.ndarray) -> np.ndarray:
    areas = []
    for f in faces:
        areas.append(float(f[2] * f[3]))
    return faces[int(np.argmax(areas))]


def extract_face_embedding(image_bgr: np.ndarray) -> Optional[np.ndarray]:
    detector = _get_detector()
    recognizer = _get_recognizer()
    h, w = image_bgr.shape[:2]
    detector.setInputSize((w, h))
    _, faces = detector.detect(image_bgr)
    if faces is None or len(faces) == 0:
        return None
    face = _largest_face(faces)
    aligned = recognizer.alignCrop(image_bgr, face)
    return recognizer.feature(aligned)


def embedding_to_json(emb: np.ndarray) -> str:
    return json.dumps(emb.flatten().tolist())


def embedding_from_json(raw: Optional[str]) -> Optional[np.ndarray]:
    if not raw:
        return None
    return np.array(json.loads(raw), dtype=np.float32).reshape(1, -1)


def compare_embeddings(probe: np.ndarray, gallery: np.ndarray) -> float:
    recognizer = _get_recognizer()
    # match() returns cosine distance (lower = more similar)
    score = recognizer.match(probe, gallery, cv2.FaceRecognizerSF_FR_COSINE)
    return float(score)


def enroll_face_from_bytes(data: bytes) -> Tuple[Optional[str], Optional[dict]]:
    img = _decode_image(data)
    if img is None:
        return None, {"error": "Invalid image"}
    emb = extract_face_embedding(img)
    if emb is None:
        return None, {"error": "No face detected in image"}
    return embedding_to_json(emb), {"face_detected": True, "dimensions": int(emb.size)}


def analyze_faces_in_image(
    data: bytes,
    watchlist: List[Tuple[int, str, str, str, Optional[str]]],
) -> dict:
    """
    watchlist items: (id, full_name, reason, risk_level, face_embedding_json)
    """
    img = _decode_image(data)
    if img is None:
        return {"success": False, "error": "Could not decode image"}

    detector = _get_detector()
    recognizer = _get_recognizer()
    h, w = img.shape[:2]
    detector.setInputSize((w, h))
    _, faces = detector.detect(img)
    annotated = img.copy()

    if faces is None or len(faces) == 0:
        return {
            "success": True,
            "faces_detected": 0,
            "matches": [],
            "message": "No faces detected",
            "annotated_image_base64": _encode_frame(annotated),
        }

    gallery_entries = []
    for pid, name, reason, risk, emb_json in watchlist:
        emb = embedding_from_json(emb_json)
        if emb is not None:
            gallery_entries.append((pid, name, reason, risk, emb))

    matches = []
    for face in faces:
        x, y, fw, fh = int(face[0]), int(face[1]), int(face[2]), int(face[3])
        aligned = recognizer.alignCrop(img, face)
        probe = recognizer.feature(aligned)

        best = None
        best_dist = 999.0
        for pid, name, reason, risk, gallery_emb in gallery_entries:
            dist = compare_embeddings(probe, gallery_emb)
            if dist < best_dist:
                best_dist = dist
                best = (pid, name, reason, risk, dist)

        label = "Unknown"
        matched = False
        confidence = 0.0
        person_id = None
        if best and best_dist <= MATCH_THRESHOLD:
            matched = True
            person_id, name, reason, risk, best_dist = best
            confidence = round(max(0.0, 1.0 - best_dist), 3)
            label = f"{name} ({confidence:.0%})"
            color = (0, 0, 255)
            matches.append({
                "watchlist_id": person_id,
                "full_name": name,
                "reason": reason,
                "risk_level": risk,
                "confidence": confidence,
                "distance": round(best_dist, 4),
                "bbox": {"x": x, "y": y, "width": fw, "height": fh},
            })
        else:
            color = (0, 255, 255)

        cv2.rectangle(annotated, (x, y), (x + fw, y + fh), color, 2)
        cv2.putText(annotated, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    return {
        "success": True,
        "faces_detected": len(faces),
        "matches": matches,
        "watchlist_match": len(matches) > 0,
        "message": (
            f"{len(matches)} watchlist match(es) from {len(faces)} face(s)"
            if matches
            else f"{len(faces)} face(s) detected, no watchlist matches"
        ),
        "annotated_image_base64": _encode_frame(annotated),
    }


def _encode_frame(frame: np.ndarray, max_width: int = 640) -> str:
    import base64

    fh, fw = frame.shape[:2]
    if fw > max_width:
        scale = max_width / fw
        frame = cv2.resize(frame, (int(fw * scale), int(fh * scale)))
    _, buf = cv2.imencode(".jpg", frame)
    return base64.b64encode(buf).decode("ascii")
