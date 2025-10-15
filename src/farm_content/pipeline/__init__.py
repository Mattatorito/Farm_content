"""Pipeline modules for the local Reels content factory.

Modules:
- scene_detector: Detects scenes using PySceneDetect with OpenCV fallback.
- transcriber: Local speech-to-text via faster-whisper; produces SRT.
- cropper: 9:16 face-focused crop using OpenCV / mediapipe.
- enhancer: Visual enhancement & stabilization via ffmpeg filters and LUTs.
- subtitle_overlay: Subtitle rendering via MoviePy or ffmpeg drawtext.
- renderer: Concatenate, transitions, audio normalize, final export.
"""

__all__ = [
    "scene_detector",
    "transcriber",
    "cropper",
    "enhancer",
    "subtitle_overlay",
    "renderer",
]
