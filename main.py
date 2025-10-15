from __future__ import annotations

import argparse
import random
from pathlib import Path
from tqdm import tqdm

from src.farm_content.pipeline.scene_detector import detect_scenes
from src.farm_content.pipeline.transcriber import transcribe_to_srt
from src.farm_content.pipeline.cropper import crop_to_9_16
from src.farm_content.pipeline.enhancer import enhance_video
from src.farm_content.pipeline.subtitle_overlay import overlay_subtitles
from src.farm_content.pipeline.renderer import render_final


def choose_scenes(scenes, desired_count: int = 4, min_total: float = 0.0, video_duration: float | None = None):
    if video_duration is not None and video_duration <= 60:
        return [(0.0, video_duration)]
    if not scenes:
        return []
    if len(scenes) <= desired_count:
        return scenes
    return sorted(random.sample(scenes, desired_count), key=lambda x: x[0])


def main():
    parser = argparse.ArgumentParser(description="Local Reels content factory")
    parser.add_argument("--input", required=True, help="Path to input video")
    parser.add_argument("--scenes", type=int, default=4, help="Number of scenes to select (3-5)")
    parser.add_argument("--style", default="cinematic", choices=["random", "cinematic", "warm", "cold", "bw"], help="Color style/LUT preset")
    parser.add_argument("--preview", action="store_true", help="Render only first scene with watermark")

    args = parser.parse_args()

    input_path = args.input
    style = args.style

    pbar = tqdm(total=7, desc="Pipeline")

    # 1) Scenes
    pbar.set_description("Detecting scenes")
    scenes = detect_scenes(input_path)
    pbar.update(1)

    # 2) Transcription
    pbar.set_description("Transcribing audio")
    srt_path = transcribe_to_srt(input_path)
    pbar.update(1)

    # 3) Select scenes
    pbar.set_description("Selecting scenes")
    # TODO: compute duration quickly (skipping heavy read), simple fallback
    chosen = choose_scenes(scenes, desired_count=args.scenes)
    if not chosen:
        chosen = [(0.0, 60.0)]  # fallback first 60s if nothing detected
    pbar.update(1)

    # 4) Crop 9:16
    pbar.set_description("Cropping to 9:16")
    crop_out_base = str(Path("outputs") / (Path(input_path).stem + "_crop"))
    cropped_paths = crop_to_9_16(input_path, crop_out_base, chosen)
    pbar.update(1)

    # 5) Enhance + stabilize
    pbar.set_description("Enhancing visuals")
    enhanced_paths = []
    for i, p in enumerate(cropped_paths):
        enhanced = str(Path(p).with_name(Path(p).stem + "_enh.mp4"))
        enhance_video(p, enhanced, style=style)
        enhanced_paths.append(enhanced)
    pbar.update(1)

    # 6) Subtitles overlay
    pbar.set_description("Overlaying subtitles")
    subtitled_paths = []
    for i, p in enumerate(enhanced_paths if not args.preview else enhanced_paths[:1]):
        outp = str(Path(p).with_name(Path(p).stem + "_sub.mp4"))
        overlay_subtitles(p, srt_path, outp, preview=args.preview)
        subtitled_paths.append(outp)
    pbar.update(1)

    # 7) Render final
    pbar.set_description("Rendering final")
    final_path = render_final(subtitled_paths)
    pbar.update(1)
    pbar.close()

    print(f"\n✅ Render Complete: {final_path}")


if __name__ == "__main__":
    main()
