#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_publisher.py

Оркестратор мультиаккаунт-публикаций:
- Аккаунт 1: генерация залипательных AI-видео и автозагрузка
- Аккаунты 2-3: анализ трендов и публикация собственных тренд-адаптаций
- Аккаунт 4: нарезка фильмов/сериалов (собственный/лицензированный материал) и автозагрузка

Важно: модуль предполагает, что вы используете контент, на который у вас есть права.
"""
from __future__ import annotations

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.farm_content.utils.trend_analyzer import TrendAnalyzer
from src.farm_content.utils.viral_generator import ViralContentGenerator
from src.farm_content.utils.smart_scheduler import SmartScheduler

# Локальные генераторы/резалки
from stable_viral_generator import create_stable_viral_video, create_multiple_viral_videos
from cinematic_movie_cuts import process_single

# Загрузчик YouTube
from uploader.youtube_uploader import get_youtube_service, upload_video


CONFIG_ACCOUNTS = Path("config/accounts.json")
CONFIG_YT_UPLOAD = Path("config/youtube_upload_config.json")


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


async def plan_publish_time(scheduler: SmartScheduler, content_type: str, platform: str, tz: str) -> datetime:
    plan = await scheduler.calculate_optimal_time(content_type=content_type, platform=platform, account_timezone=tz)
    return plan.scheduled_time


async def run_account_pipeline(account: Dict[str, Any], dry_run: bool = False) -> None:
    name = account.get('name', 'account')
    platform = account.get('platform', 'youtube')
    tz = account.get('timezone', 'Europe/Moscow')
    pipeline = account.get('pipeline', 'ai_video')

    print(f"\n=== ▶️ Аккаунт: {name} | Пайплайн: {pipeline} ===")

    scheduler = SmartScheduler()
    trends = TrendAnalyzer()
    meta = ViralContentGenerator()

    # Авторизация YouTube (только если не dry-run)
    yt_cfg = account.get('youtube', {})
    if platform == 'youtube' and not dry_run:
        client_secrets = yt_cfg.get('client_secrets', 'config/client_secrets.json')
        token_file = yt_cfg.get('token_file', f"config/tokens/{name}_token.json")
        service = get_youtube_service(client_secrets, token_file)
    else:
        service = None

    # Выполняем пайплайн
    video_path = None
    content_type = 'ai_video'

    if pipeline == 'ai_video':
        content_type = 'ai_video'
        video_path = create_stable_viral_video()
        analysis = {"content_type": "high_energy", "viral_score": 0.75, "duration": 20}
    elif pipeline == 'trend_shorts':
        content_type = 'trend_short'
        trends_data = await trends.analyze_current_trends(platforms=["youtube_shorts", "instagram"]) 
        # Здесь предполагается ваша собственная адаптация контента под тренды (не перезалив чужих видео)
        video_path = create_stable_viral_video()  # Заглушка: генерим собственный тренд-ролик
        analysis = {"content_type": "high_energy", "viral_score": 0.7, "duration": 20, "trends": trends_data}
    elif pipeline == 'movie_cuts':
        content_type = 'movie_clip'
        # Ожидаем, что у вас есть файл в viral_assets/movie_clips/input.mp4 и субтитры
        src = account.get('movie_clip', {}).get('source', 'viral_assets/movie_clips/input.mp4')
        srt = account.get('movie_clip', {}).get('srt')
        video_path = process_single(src, srt_path=srt, add_bgm=True)
        analysis = {"content_type": "movie_clip", "viral_score": 0.6, "duration": 30}
    else:
        print(f"Неизвестный pipeline: {pipeline}")
        return

    if not video_path:
        print("⚠️ Видео не создано. Пропускаю загрузку.")
        return

    # Метаданные
    metadata = meta.generate_viral_metadata(analysis, platform="youtube_shorts", style="high_energy")
    title = metadata['title']
    description = metadata['description'] + "\n\n" + " ".join(metadata['hashtags'])
    tags = load_json(CONFIG_YT_UPLOAD).get('viral_tags', [])
    category_id = "24"

    # Время публикации
    publish_time = await plan_publish_time(scheduler, content_type, platform='youtube', tz=tz)
    print(f"🕒 План публикации для {name}: {publish_time}")

    if dry_run:
        print("[DRY-RUN] Пропускаю загрузку. Итог:")
        print(f"  • Файл: {video_path}")
        print(f"  • Заголовок: {title}")
        print(f"  • Теги: {tags[:8]}… (всего {len(tags)})")
        print(f"  • PublishAt: {publish_time}")
        return
    # Загрузка на YouTube (можно поменять privacy_status на 'public' без расписания)
    response = upload_video(
        service=service,
        file_path=video_path,
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        privacy_status='private',
        publish_at=publish_time,
    )
    video_id = response.get('id')
    print(f"✅ Загружено в черновик (с расписанием): https://youtube.com/shorts/{video_id}")


async def main():
    import argparse
    p = argparse.ArgumentParser(description="Мультиаккаунт авто-публикации")
    p.add_argument('--only', type=str, nargs='*', help='Имена аккаунтов для запуска (по account.name)')
    p.add_argument('--dry-run', action='store_true', help='Не загружать на YouTube, только создать и спланировать')
    args = p.parse_args()

    cfg = load_json(CONFIG_ACCOUNTS)
    accounts = cfg.get('youtube_accounts', [])
    if not accounts:
        print("Добавьте аккаунты в config/accounts.json")
        return

    if args.only:
        accounts = [a for a in accounts if a.get('name') in set(args.only)]
        if not accounts:
            print("Нет совпадающих аккаунтов по фильтру --only")
            return

    # Последовательно, можно сделать параллельно при желании
    for acc in accounts:
        try:
            await run_account_pipeline(acc, dry_run=args.dry_run)
        except Exception as e:
            print(f"Ошибка аккаунта {acc.get('name')}: {e}")


if __name__ == '__main__':
    asyncio.run(main())
