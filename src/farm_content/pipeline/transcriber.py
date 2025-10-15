from __future__ import annotations

from typing import Optional
import os
from pathlib import Path
import pysrt
from faster_whisper import WhisperModel


def transcribe_to_srt(input_video: str, output_srt: Optional[str] = None, model_size: str = "small", device: Optional[str] = None) -> str:
    """
    Transcribe audio using faster-whisper locally and save SRT.

    Args:
        input_video: path to input media
        output_srt: where to save .srt; if None, same stem with .srt in outputs
        model_size: whisper model size, e.g., tiny, base, small, medium, large-v2
        device: 'cpu' or 'cuda'; autodetect if None

    Returns:
        path to the generated .srt
    """
    input_video = str(input_video)
    if output_srt is None:
        out_dir = Path("outputs")
        out_dir.mkdir(parents=True, exist_ok=True)
        output_srt = str(out_dir / (Path(input_video).stem + ".srt"))

    # Initialize model
    model = WhisperModel(model_size, device=device or ("cuda" if os.environ.get("WHISPER_DEVICE") == "cuda" else "cpu"))

    segments, info = model.transcribe(input_video, beam_size=5, vad_filter=True)

    subs = pysrt.SubRipFile()
    idx = 1
    for seg in segments:
        start_s = seg.start
        end_s = seg.end
        text = seg.text.strip()
        # Convert float seconds to SubRipTime
        start = pysrt.SubRipTime(seconds=int(start_s), milliseconds=int((start_s - int(start_s)) * 1000))
        end = pysrt.SubRipTime(seconds=int(end_s), milliseconds=int((end_s - int(end_s)) * 1000))
        subs.append(pysrt.SubRipItem(index=idx, start=start, end=end, text=text))
        idx += 1

    subs.clean_indexes()
    subs.save(output_srt, encoding="utf-8")
    return output_srt
