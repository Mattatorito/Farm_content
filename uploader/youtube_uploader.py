#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Uploader with scheduling support (publishAt).

Внимание: используйте только собственный/лицензированный контент. 
Модуль предоставляет функции авторизации и загрузки клипов на YouTube.
"""
from __future__ import annotations

import os
import json
import datetime as dt
from typing import Optional, List, Dict

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# Требуемые области доступа
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def _to_rfc3339(dt_obj: dt.datetime) -> str:
    if dt_obj.tzinfo is None:
        # Считаем, что время в локальной зоне и переводим в UTC
        import pytz
        dt_obj = pytz.timezone("Europe/Moscow").localize(dt_obj).astimezone(pytz.utc)
    return dt_obj.isoformat()


def get_youtube_service(client_secrets_file: str, token_file: str) -> any:
    os.makedirs(os.path.dirname(token_file), exist_ok=True)
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # Обновление или первичная авторизация
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    service = build('youtube', 'v3', credentials=creds)
    return service


def upload_video(
    service,
    file_path: str,
    title: str,
    description: str,
    tags: Optional[List[str]] = None,
    category_id: str = "24",
    privacy_status: str = "private",
    publish_at: Optional[dt.datetime] = None,
) -> Dict:
    body: Dict = {
        'snippet': {
            'title': title[:100],
            'description': description[:5000],
            'categoryId': category_id,
            'tags': tags or [],
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False,
        }
    }
    if publish_at is not None:
        body['status']['publishAt'] = _to_rfc3339(publish_at)
        body['status']['privacyStatus'] = 'private'  # YouTube сам переведёт в public по расписанию

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = service.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        # Можно добавить прогресс-лог
    return response
