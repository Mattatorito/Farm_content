from __future__ import annotations

from typing import List, Tuple, Optional
import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip

TARGET_W, TARGET_H = 1080, 1920
ASPECT = TARGET_W / TARGET_H  # 9:16


def _detect_face_bbox(frame_bgr: np.ndarray, face_cascade: Optional[cv2.CascadeClassifier]) -> Optional[Tuple[int, int, int, int]]:
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    if face_cascade is None:
        return None
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    if len(faces) == 0:
        return None
    # choose largest
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return int(x), int(y), int(w), int(h)


def _compute_crop_rect(frame_w: int, frame_h: int, face_bbox: Optional[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
    # Desired aspect 9:16 portrait
    frame_aspect = frame_w / frame_h
    if frame_aspect > ASPECT:
        # too wide, limit width
        out_h = frame_h
        out_w = int(out_h * ASPECT)
    else:
        # too tall, limit height
        out_w = frame_w
        out_h = int(out_w / ASPECT)

    if face_bbox is None:
        # center crop
        x = (frame_w - out_w) // 2
        y = (frame_h - out_h) // 2
        return x, y, out_w, out_h

    fx, fy, fw, fh = face_bbox
    cx = fx + fw // 2
    cy = fy + fh // 2
    x = max(0, min(frame_w - out_w, cx - out_w // 2))
    y = max(0, min(frame_h - out_h, cy - out_h // 2))
    return x, y, out_w, out_h


def crop_to_9_16(input_path: str, output_path: str, segments: List[Tuple[float, float]], face_cascade_path: Optional[str] = None) -> List[str]:
    """
    Crop specified segments of video to 9:16, centered around detected face if possible.

    Returns list of paths to cropped segment files (mp4), each resized to 1080x1920.
    """
    face_cascade = None
    # Try default OpenCV Haarcascade if not provided
    if not face_cascade_path:
        try:
            default_xml = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
            if os.path.exists(default_xml):
                face_cascade_path = default_xml
        except Exception:
            pass
    if face_cascade_path and os.path.exists(face_cascade_path):
        face_cascade = cv2.CascadeClassifier(face_cascade_path)

    clip = VideoFileClip(input_path)
    out_paths: List[str] = []

    for i, (start, end) in enumerate(segments):
        sub = clip.subclip(start, end)
        # sample a frame near the middle for face detection
        t = (start + end) / 2.0
        frame = clip.get_frame(t)
        frame_bgr = frame[:, :, ::-1].copy()
        bbox = _detect_face_bbox(frame_bgr, face_cascade)

        h, w = frame.shape[:2]
        x, y, cw, ch = _compute_crop_rect(w, h, bbox)

        def crop_frame(f):
            fbgr = f[:, :, ::-1]
            crop = fbgr[y:y+ch, x:x+cw]
            crop = cv2.resize(crop, (TARGET_W, TARGET_H), interpolation=cv2.INTER_AREA)
            return crop[:, :, ::-1]

        cropped = sub.fl_image(crop_frame)
        seg_out = f"{output_path}_seg{i+1}.mp4"
        cropped.write_videofile(seg_out, codec="libx264", audio=True, audio_codec="aac", fps=30, threads=4, preset="medium")
        out_paths.append(seg_out)

    clip.close()
    return out_paths
