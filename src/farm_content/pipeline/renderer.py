from __future__ import annotations

from typing import List
from pathlib import Path
from datetime import datetime

from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeAudioClip, AudioFileClip
from pydub import AudioSegment
import ffmpeg


OUT_DIR = Path("outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _fade_transition(clips: List[VideoFileClip], fade: float = 0.4) -> List[VideoFileClip]:
    out = []
    for i, c in enumerate(clips):
        cc = c.fx(lambda clip: clip.crossfadein(fade)) if i > 0 else c
        cc = cc.crossfadeout(fade)
        out.append(cc)
    return out


def _loudnorm_video(in_path: str, out_path: str) -> str:
    # Apply ffmpeg loudnorm EBU R128 to full video
    try:
        (
            ffmpeg
            .input(in_path)
            .output(
                out_path,
                c_v="copy",
                c_a="aac",
                b_a="192k",
                af="loudnorm=I=-14:TP=-1.5:LRA=11"
            )
            .global_args("-hide_banner", "-loglevel", "error")
            .run(overwrite_output=True)
        )
        return out_path
    except ffmpeg.Error:
        return in_path


def render_final(segments_paths: List[str]) -> str:
    clips = [VideoFileClip(p).resize((1080, 1920)).set_fps(30) for p in segments_paths]
    clips = _fade_transition(clips, fade=0.4)
    final = concatenate_videoclips(clips, method="compose")

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = OUT_DIR / f"final_{ts}.mp4"

    final.write_videofile(
        str(out_path),
        codec="libx264",
        audio=True,
        audio_codec="aac",
        fps=30,
        preset="medium",
        threads=6,
        bitrate=None,
        ffmpeg_params=["-profile:v", "high", "-level:v", "4.1", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )

    final.close()
    for c in clips:
        c.close()

    # Apply final loudnorm in-place to ensure -14 LUFS
    ln_out = OUT_DIR / f"final_{ts}_ln.mp4"
    final_path = _loudnorm_video(str(out_path), str(ln_out))
    return str(final_path)
