from __future__ import annotations

import cv2
from typing import List, Tuple

# PySceneDetect imports are optional; we degrade gracefully
try:
    from scenedetect import SceneManager
    from scenedetect.detectors import ContentDetector
    from scenedetect.video_manager import VideoManager
    _SCENEDETECT_AVAILABLE = True
except Exception:
    _SCENEDETECT_AVAILABLE = False


def detect_scenes(video_path: str, threshold: float = 27.0, min_scene_len: float = 1.0) -> List[Tuple[float, float]]:
    """
    Detect scenes and return list of (start_sec, end_sec) tuples.

    Priority: PySceneDetect (ContentDetector) -> fallback: OpenCV frame diff.

    Args:
        video_path: path to video
        threshold: sensitivity for scene detection (PySceneDetect content threshold or diff threshold for fallback)
        min_scene_len: minimum scene length in seconds
    """
    if _SCENEDETECT_AVAILABLE:
        try:
            return _detect_scenes_pyscenedetect(video_path, threshold, min_scene_len)
        except Exception:
            pass

    return _detect_scenes_opencv(video_path, threshold, min_scene_len)


def _detect_scenes_pyscenedetect(video_path: str, threshold: float, min_scene_len: float) -> List[Tuple[float, float]]:
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    video_manager.set_downscale_factor()
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()

    fps = video_manager.get_framerate()
    duration = video_manager.get_duration().get_seconds() if hasattr(video_manager.get_duration(), 'get_seconds') else None

    scenes: List[Tuple[float, float]] = []
    for start_time, end_time in scene_list:
        start = start_time.get_seconds()
        end = end_time.get_seconds()
        if (end - start) >= min_scene_len:
            scenes.append((start, end))

    # If scenedetect returns empty, fallback
    if not scenes:
        return _detect_scenes_opencv(video_path, threshold, min_scene_len)

    # Ensure coverage to end
    if duration is not None and scenes[-1][1] < duration:
        if duration - scenes[-1][1] >= min_scene_len:
            scenes.append((scenes[-1][1], duration))

    return scenes


def _detect_scenes_opencv(video_path: str, threshold: float, min_scene_len: float) -> List[Tuple[float, float]]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    prev_gray = None
    scenes: List[Tuple[float, float]] = []
    scene_start_frame = 0
    frame_index = 0

    def frame_to_time(f: int) -> float:
        return f / fps

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            score = diff.mean()
            if score > threshold:
                # cut scene
                start_sec = frame_to_time(scene_start_frame)
                end_sec = frame_to_time(frame_index)
                if end_sec - start_sec >= min_scene_len:
                    scenes.append((start_sec, end_sec))
                scene_start_frame = frame_index

        prev_gray = gray
        frame_index += 1

    # tail
    total_frames = frame_index
    tail_start = frame_to_time(scene_start_frame)
    tail_end = frame_to_time(total_frames)
    if tail_end - tail_start >= min_scene_len:
        scenes.append((tail_start, tail_end))

    cap.release()
    return scenes
