#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cinematic_movie_cuts.py

Назначение:
- Делает вертикальные (9:16) клипы из исходных видео (фильмы/сериалы)
- Центр-кроп до 1080x1920 без чёрных боковых панелей
- Накладывает киношные субтитры: белый жирный текст с чёрной обводкой + полупрозрачная чёрная плашка

Источник файлов:
- Видео берутся из: viral_assets/movie_clips/*.mp4 (или указать --single)
- Субтитры (опционально): viral_assets/subtitles/<basename>.srt (или указать --srt)

Вывод:
- Готовые ролики в папке: ready_videos/

Запуск (примеры):
- Один файл и авто-поиск SRT: 
    python cinematic_movie_cuts.py --single viral_assets/movie_clips/clip1.mp4
- Пакетно все mp4 из папки: 
    python cinematic_movie_cuts.py --all
- Явно задать SRT и отключить фон-музыку: 
    python cinematic_movie_cuts.py --single path/to/clip.mp4 --srt path/to/clip.srt --no-bgm
- Быстрая проверка без исходников (демо 6 сек):
    python cinematic_movie_cuts.py --demo

Зависимости: MoviePy 1.0.3, ImageMagick
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

try:
    from moviepy.editor import (
        VideoFileClip,
        CompositeVideoClip,
        ColorClip,
        TextClip,
        AudioFileClip,
    )
    from moviepy.video.fx.resize import resize
    from moviepy.video.fx.crop import crop
    from moviepy.video.tools.subtitles import SubtitlesClip
    from moviepy.audio.fx.all import audio_loop
except Exception as e:
    print("[ERROR] Не удалось импортировать MoviePy. Убедитесь, что установлена версия 1.0.3 и настроен ImageMagick.")
    print("Причина:", e)
    sys.exit(1)


# --- Константы по умолчанию ---
TARGET_W, TARGET_H = 1080, 1920
MOVIE_DIR = os.path.join("viral_assets", "movie_clips")
SUBS_DIR = os.path.join("viral_assets", "subtitles")
AUDIO_DIR = os.path.join("viral_assets", "audio")
OUTPUT_DIR = "ready_videos"


# --- Модель субтитров ---
@dataclass
class SubtitleLine:
    start: float  # seconds
    end: float    # seconds
    text: str


def ensure_dirs() -> None:
    os.makedirs(MOVIE_DIR, exist_ok=True)
    os.makedirs(SUBS_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_srt(path: str) -> List[SubtitleLine]:
    """Простейший парсер .srt -> список SubtitleLine.
    Поддерживает миллисекунды, пустые строки, порядковые номера.
    """
    import re

    if not os.path.isfile(path):
        raise FileNotFoundError(f"SRT не найден: {path}")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Разбиваем по блокам
    blocks = re.split(r"\n\s*\n", content.strip())
    result: List[SubtitleLine] = []
    for block in blocks:
        lines = [ln.strip("\ufeff") for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        # Ищем таймкод во второй строке или первой (если нет номера)
        time_line = None
        if len(lines) >= 2 and ("-->" in lines[1]):
            time_line = lines[1]
            text_lines = lines[2:]
        elif "-->" in lines[0]:
            time_line = lines[0]
            text_lines = lines[1:]
        else:
            # неподходящий блок
            continue

        def time_to_sec(s: str) -> float:
            # Форматы: HH:MM:SS,ms или MM:SS,ms
            s = s.replace(",", ".")
            parts = s.split(":")
            if len(parts) == 3:
                h, m, sec = parts
                return int(h) * 3600 + int(m) * 60 + float(sec)
            elif len(parts) == 2:
                m, sec = parts
                return int(m) * 60 + float(sec)
            else:
                return float(s)

        try:
            start_s, end_s = [p.strip() for p in time_line.split("-->")]
            start, end = time_to_sec(start_s), time_to_sec(end_s)
            if end <= start:
                continue
            text = " ".join(text_lines).strip()
            if not text:
                continue
            result.append(SubtitleLine(start, end, text))
        except Exception:
            continue

    return result


def fallback_subs_from_txt(path: str, total_duration: float) -> List[SubtitleLine]:
    """Если нет SRT, можно дать .txt с построчными репликами.
    Каждой строке выделим равные интервалы времени.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]
    if not lines:
        return []
    seg = total_duration / len(lines)
    subs: List[SubtitleLine] = []
    cur = 0.0
    for ln in lines:
        subs.append(SubtitleLine(cur, min(cur + seg, total_duration), ln))
        cur += seg
    return subs


def find_subtitles_for(video_path: str) -> Optional[List[SubtitleLine]]:
    base = os.path.splitext(os.path.basename(video_path))[0]
    # Ищем srt в папке субтитров и рядом с видео
    candidates = [
        os.path.join(SUBS_DIR, base + ".srt"),
        os.path.join(os.path.dirname(video_path), base + ".srt"),
        os.path.join(SUBS_DIR, base + ".txt"),
        os.path.join(os.path.dirname(video_path), base + ".txt"),
    ]
    for c in candidates:
        if os.path.isfile(c) and c.lower().endswith(".srt"):
            return parse_srt(c)
    for c in candidates:
        if os.path.isfile(c) and c.lower().endswith(".txt"):
            # Вернём маркер-обработку txt, потребует знать длительность
            return [SubtitleLine(-1, -1, f"__USE_TXT__::{c}")]
    return None


def make_subtitle_textclip(txt: str, max_width: int) -> TextClip:
    """Генерация стилизованного саба: белый жирный с чёрной обводкой."""
    # Подбор шрифта: используем Impact/Arial Black, если нет — стандартный
    possible_fonts = [
        "Impact",
        "Arial-Black",
        "Arial Black",
        "Helvetica-Bold",
        "DejaVuSans-Bold",
        "Arial",
    ]
    font = None
    for f in possible_fonts:
        try:
            # Попытаемся создать крошечный клип — так узнаем доступность шрифта
            _ = TextClip(" ", font=f, fontsize=10, method="label")
            font = f
            break
        except Exception:
            continue
    kwargs = dict(
        fontsize=62,
        color="white",
        method="caption",
        size=(max_width, None),
        align="center",
    )
    if font:
        kwargs["font"] = font
    # stroke работает через ImageMagick
    try:
        kwargs.update(dict(stroke_color="black", stroke_width=6))
    except Exception:
        pass
    clip = TextClip(txt, **kwargs)
    return clip


def build_subs_layer(
    base_video: VideoFileClip,
    subs: List[SubtitleLine],
    banner_height: int = 280,
) -> CompositeVideoClip:
    W, H = base_video.w, base_video.h
    # Плашка выводится только когда есть текст: используем SubtitlesClip
    # Создадим SubtitlesClip для текста
    subs_tuples: List[Tuple[Tuple[float, float], str]] = [
        ((s.start, s.end), s.text) for s in subs if s.end > s.start and s.start >= 0
    ]
    if not subs_tuples:
        # пустой прозрачный слой
        return CompositeVideoClip([base_video.set_duration(base_video.duration)])

    text_subs = SubtitlesClip(
        subs_tuples,
        lambda txt: make_subtitle_textclip(txt, max_width=W - 160),
    ).set_position(("center", "bottom"))

    # Плашка такая же по таймингам, игнорируем текст
    def make_banner(_txt: str):
        return ColorClip(size=(W, banner_height), color=(0, 0, 0)).set_opacity(0.35)

    banner_subs = SubtitlesClip(subs_tuples, make_banner).set_position(
        ("center", "bottom")
    )

    return CompositeVideoClip([base_video, banner_subs, text_subs])


def to_vertical_9x16(clip: VideoFileClip, target_w=TARGET_W, target_h=TARGET_H) -> VideoFileClip:
    """Масштабируем и центр-кропим в вертикаль 9:16, заполняя весь кадр."""
    # Масштаб под заполнение
    scale = max(target_w / clip.w, target_h / clip.h)
    resized = resize(clip, scale)
    # Центр-кроп
    x_center = resized.w / 2
    y_center = resized.h / 2
    cropped = crop(resized, width=target_w, height=target_h, x_center=x_center, y_center=y_center)
    return cropped


def process_single(
    video_path: str,
    srt_path: Optional[str] = None,
    output_dir: str = OUTPUT_DIR,
    add_bgm: bool = True,
) -> Optional[str]:
    if not os.path.isfile(video_path):
        print(f"[WARN] Видео не найдено: {video_path}")
        return None

    print(f"[INFO] Обработка: {video_path}")
    clip = VideoFileClip(video_path)
    vertical = to_vertical_9x16(clip)

    # Поиск субтитров, если явный путь не задан
    subs: Optional[List[SubtitleLine]] = None
    if srt_path and os.path.isfile(srt_path):
        subs = parse_srt(srt_path) if srt_path.lower().endswith(".srt") else None
        if subs is None and srt_path.lower().endswith(".txt"):
            subs = fallback_subs_from_txt(srt_path, vertical.duration)
    else:
        found = find_subtitles_for(video_path)
        if found:
            # Если маркер txt, прогрузим теперь длительность
            if found and len(found) == 1 and found[0].text.startswith("__USE_TXT__::"):
                txt_path = found[0].text.split("::", 1)[1]
                subs = fallback_subs_from_txt(txt_path, vertical.duration)
            else:
                subs = found

    # Наложение субтитров
    if subs:
        with_subs = build_subs_layer(vertical, subs)
    else:
        with_subs = vertical

    # Аудио: оригинал + тихий фон (по желанию)
    final_audio = with_subs.audio
    if add_bgm:
        bg_candidates = [
            os.path.join(AUDIO_DIR, "background_electronic.wav"),
            os.path.join(AUDIO_DIR, "background.mp3"),
        ]
        bgm_path = next((p for p in bg_candidates if os.path.isfile(p)), None)
        if bgm_path:
            try:
                bgm = AudioFileClip(bgm_path)
                bgm_looped = audio_loop(bgm, duration=with_subs.duration).volumex(0.15)
                # Смешаем с оригинальным звуком и гарантированно подрежем по длительности
                from moviepy.editor import CompositeAudioClip

                final_audio = CompositeAudioClip(
                    [a for a in [with_subs.audio, bgm_looped] if a is not None]
                ).set_duration(with_subs.duration)
            except Exception as e:
                print(f"[WARN] Не удалось добавить фон-музыку: {e}")

    final = with_subs.set_audio(final_audio)

    # Вывод
    base = os.path.splitext(os.path.basename(video_path))[0]
    out_name = f"CIN_{base}_9x16.mp4"
    out_path = os.path.join(output_dir, out_name)
    os.makedirs(output_dir, exist_ok=True)

    # Для стабильности уменьшим битрейт, если ролик длинный
    bitrate = "10M" if final.duration and final.duration > 40 else "12M"

    try:
        final.write_videofile(
            out_path,
            codec="libx264",
            audio_codec="aac",
            fps=min(30, clip.fps or 30),
            bitrate=bitrate,
            preset="medium",
            threads=2,
            temp_audiofile=os.path.join(output_dir, "_temp_audio.m4a"),
            remove_temp=True,
        )
        print(f"[OK] Сохранено: {out_path}")
        return out_path
    finally:
        clip.close()
        try:
            vertical.close()
        except Exception:
            pass


def process_all(add_bgm: bool = True) -> List[str]:
    ensure_dirs()
    videos = [
        os.path.join(MOVIE_DIR, f)
        for f in os.listdir(MOVIE_DIR)
        if f.lower().endswith((".mp4", ".mov", ".mkv"))
    ]
    if not videos:
        print(f"[INFO] В {MOVIE_DIR} нет видеофайлов. Поместите сюда ролики и запустите снова.")
        return []
    outputs = []
    for vp in videos:
        try:
            out = process_single(vp, add_bgm=add_bgm)
            if out:
                outputs.append(out)
        except Exception as e:
            print(f"[ERR] Не удалось обработать {vp}: {e}")
    return outputs


def run_demo() -> Optional[str]:
    """Быстрая проверка без исходников: синтетическое видео + 2-3 саба."""
    ensure_dirs()
    import numpy as np

    bg1 = ColorClip((1920, 1080), color=(20, 20, 20)).set_duration(3)
    bg2 = ColorClip((1920, 1080), color=(40, 40, 60)).set_duration(3)
    demo = CompositeVideoClip([bg1.set_start(0), bg2.set_start(3)]).set_duration(6)
    demo = demo.fx(resize, 1.0)  # no-op для совместимости
    demo = to_vertical_9x16(demo)

    subs = [
        SubtitleLine(0.3, 2.7, "Я — демо‑пример субтитров"),
        SubtitleLine(3.2, 5.5, "Кадр без чёрных полей, 9:16"),
    ]
    layered = build_subs_layer(demo, subs)
    out_path = os.path.join(OUTPUT_DIR, "DEMO_CINEMATIC_9x16.mp4")
    layered.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        bitrate="6M",
        preset="veryfast",
        threads=2,
    )
    print(f"[OK] Демо сохранено: {out_path}")
    return out_path


def main(argv: Optional[List[str]] = None) -> int:
    ensure_dirs()

    p = argparse.ArgumentParser(description="Генерация киношных клипов 9:16 с субтитрами")
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--single", type=str, help="Путь к одному видеоролику для обработки")
    g.add_argument("--all", action="store_true", help="Обработать все видео из viral_assets/movie_clips/")
    p.add_argument("--srt", type=str, help="Путь к файлу субтитров (.srt или .txt)")
    p.add_argument("--no-bgm", action="store_true", help="Не добавлять фоновую музыку")
    p.add_argument("--demo", action="store_true", help="Запустить демо-режим без исходников")
    args = p.parse_args(argv)

    if args.demo:
        run_demo()
        return 0

    if not args.single and not args.all:
        print("[HINT] Укажите --single <path.mp4> или --all, либо --demo для проверки.")
        return 2

    if args.single:
        out = process_single(args.single, srt_path=args.srt, add_bgm=not args.no_bgm)
        return 0 if out else 1
    else:
        outs = process_all(add_bgm=not args.no_bgm)
        return 0 if outs else 1


if __name__ == "__main__":
    raise SystemExit(main())
