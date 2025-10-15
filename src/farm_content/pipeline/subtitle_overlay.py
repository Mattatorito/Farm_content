from __future__ import annotations

from typing import Optional
from pathlib import Path

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip


def _subtitle_generator(txt):
    return TextClip(txt, fontsize=42, font="Arial", color="white", stroke_color="black", stroke_width=2)


def overlay_subtitles(input_path: str, srt_path: Optional[str], output_path: str, preview: bool = False) -> str:
    clip = VideoFileClip(input_path)

    clips = [clip]
    if srt_path and Path(srt_path).exists():
        subs = SubtitlesClip(srt_path, _subtitle_generator)
        subs = subs.set_position(("center", "bottom")).set_duration(clip.duration)
        clips.append(subs)
    else:
        print("[WARN] SRT not provided or missing; skipping subtitles.")

    if preview:
        # Watermark for preview mode
        wm = TextClip("preview only", fontsize=28, font="Arial", color="white")
        wm = wm.on_color(size=(wm.w + 10, wm.h + 10), color=(0, 0, 0), col_opacity=0.4)
        wm = wm.set_pos(("right", "top")).set_duration(clip.duration)
        clips.append(wm)

    final = CompositeVideoClip(clips, size=clip.size)
    final.write_videofile(
        output_path,
        codec="libx264",
        audio=True,
        audio_codec="aac",
        fps=30,
        preset="medium",
        threads=4,
    )

    clip.close()
    final.close()
    return output_path
