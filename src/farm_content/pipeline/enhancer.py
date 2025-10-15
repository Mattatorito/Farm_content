from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Optional

import ffmpeg

LUT_DIR = Path("assets/luts")

STYLE_PRESETS = {
    "random": {},
    "cinematic": {"contrast": 1.1, "brightness": 0.03, "saturation": 1.15},
    "warm": {"contrast": 1.08, "brightness": 0.04, "saturation": 1.2},
    "cold": {"contrast": 1.12, "brightness": 0.0, "saturation": 0.95},
    "bw": {"contrast": 1.15, "brightness": 0.02, "saturation": 0.0},
}


def _select_lut(style: str = "random") -> Optional[Path]:
    lut_files = list(LUT_DIR.glob("*.cube"))
    if not lut_files:
        return None
    if style == "random" or style not in STYLE_PRESETS:
        return random.choice(lut_files)
    # could map preferred LUTs by style; fallback to any
    return random.choice(lut_files)


def enhance_video(input_path: str, output_path: str, style: str = "cinematic") -> str:
    """
    Apply enhancement filter chain and stabilization (if possible) using ffmpeg-python.
    Returns path to enhanced file.
    """
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["cinematic"])

    lut = _select_lut(style)
    if lut is None:
        print("[WARN] No LUT found in assets/luts, continuing without LUT.")

    eq = f"eq=contrast={preset.get('contrast', 1.1)}:brightness={preset.get('brightness', 0.03)}:saturation={preset.get('saturation', 1.15)}"
    lut_part = f",lut3d='{lut.as_posix()}'" if lut else ""
    vf_chain = (
        f"unsharp=3:3:0.6,{eq}{lut_part},vignette=0.4,gblur=sigma=1.2,noise=alls=10,"
        f"split=2[a][b];[b]boxblur=10,[a][b]overlay"
    )

    transforms_file = Path(output_path).with_suffix(".trf")
    stabilized_input = input_path

    # Two-pass stabilization; ignore failures
    try:
        (
            ffmpeg
            .input(input_path)
            .filter("vidstabdetect", shakiness=5, accuracy=15, result=str(transforms_file))
            .output("/dev/null", f="null")
            .global_args("-hide_banner", "-loglevel", "error")
            .run()
        )
        tmp_stab = str(Path(output_path).with_name(Path(output_path).stem + "_stab_tmp.mp4"))
        (
            ffmpeg
            .input(input_path)
            .filter("vidstabtransform", smoothing=30, input=str(transforms_file))
            .output(tmp_stab, vcodec="libx264", crf=18, preset="fast")
            .global_args("-hide_banner", "-loglevel", "error")
            .run(overwrite_output=True)
        )
        stabilized_input = tmp_stab
    except ffmpeg.Error:
        pass

    # Build filter graph step-by-step
    inp = ffmpeg.input(stabilized_input)
    v = inp.filter('scale', 1080, 1920)
    v = v.filter('fps', fps=30)
    v = v.filter('setsar', 1)
    v = v.filter('setdar', '9/16')
    v = v.filter('format', 'yuv420p')
    v = v.filter('unsharp', '3:3:0.6')
    v = v.filter('eq', contrast=preset.get('contrast', 1.1), brightness=preset.get('brightness', 0.03), saturation=preset.get('saturation', 1.15))
    if lut:
        v = v.filter('lut3d', file=lut.as_posix())
    v = v.filter('vignette', 0.4)
    v = v.filter('gblur', sigma=1.2)
    v = v.filter('noise', alls=10)
    a, b = v.split()
    b_blur = b.filter('boxblur', 10)
    out_v = ffmpeg.overlay(a, b_blur)

    (
        ffmpeg
        .output(out_v, inp.audio, output_path,
                vcodec='libx264', preset='medium', crf=18,
                profile='high', level='4.1', pix_fmt='yuv420p', movflags='+faststart',
                acodec='aac', audio_bitrate='192k')
        .global_args('-hide_banner', '-loglevel', 'error')
        .run(overwrite_output=True)
    )

    try:
        if transforms_file.exists():
            transforms_file.unlink()
        tmp = Path(output_path).with_name(Path(output_path).stem + "_stab_tmp.mp4")
        if tmp.exists():
            tmp.unlink()
    except Exception:
        pass

    return output_path
