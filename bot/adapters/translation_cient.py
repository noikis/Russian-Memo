from __future__ import annotations

from typing import Protocol, Optional
import requests
import os


class TranslationClient(Protocol):
    def translate(self, text: str, target_lang: str, source_lang: str | None = None) -> str:
        ...


class TranslationError(RuntimeError):
    """Raised when the translation provider returns an error or unexpected response."""

class YandexTranslationClient:
    BASE_URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"

    def __init__(self) -> None:
        self.api_key = os.environ["YANDEX_API_KEY"]
        self.folder_id = os.environ["YANDEX_FOLDER_ID"]
        self.BASE_URL = "https://translate.api.cloud.yandex.net/translate/v2/translate"

    def translate(self, text: str, target_lang: str, source_lang: str) -> str:
        body = {
            "folderId": self.folder_id,
            "texts": [text],
            "targetLanguageCode": target_lang,
            "sourceLanguageCode": source_lang
        }

        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.BASE_URL, json=body, headers=headers)
        if response.status_code != 200:
            raise TranslationError(f"Translation API returned status code {response.status_code}")
        data = response.json()
        if "translations" not in data or not data["translations"]:
            raise TranslationError("Translation API returned unexpected response format")

        return data["translations"][0]["text"]
