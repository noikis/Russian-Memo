from __future__ import annotations

import json
import socket
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from bot.domains import Definition, Meaning


class DictionaryClient(Protocol):
    language_code: str

    def get_definition(self, word: str) -> Definition | None: ...


class DictionaryAPIClient:
    language_code = "en"
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
    timeout_seconds = 10

    def get_definition(self, word: str) -> Definition | None:
        word = word.strip()
        if not word:
            return None

        request_url = f"{self.url}{quote(word)}"
        request = Request(request_url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 404:
                return None
            return None
        except (URLError, socket.timeout, TimeoutError, ValueError):
            return None

        try:
            payload: Any = json.loads(raw)
        except json.JSONDecodeError:
            return None

        if not isinstance(payload, list) or not payload:
            return None

        entry = payload[0]
        if not isinstance(entry, dict):
            return None

        meanings: list[dict[str, Any]] = entry.get("meanings") or []
        if not isinstance(meanings, list):
            meanings = []

        definition = Definition(word=entry.get("word") or word)

        for meaning in meanings:
            if not isinstance(meaning, dict):
                continue
            part_of_speech = meaning.get("partOfSpeech")
            if not isinstance(part_of_speech, str) or not part_of_speech.strip():
                part_of_speech = None
            else:
                part_of_speech = part_of_speech.strip()

            meaning_synonyms = meaning.get("synonyms") or []
            if not isinstance(meaning_synonyms, list):
                meaning_synonyms = []

            for item in meaning.get("definitions") or []:
                if not isinstance(item, dict):
                    continue
                definition_text = item.get("definition")
                if not isinstance(definition_text, str) or not definition_text.strip():
                    continue

                item_synonyms = item.get("synonyms") or []
                if not isinstance(item_synonyms, list):
                    item_synonyms = []

                synonyms = []
                for synonym in [*meaning_synonyms, *item_synonyms]:
                    if isinstance(synonym, str) and synonym.strip():
                        synonyms.append(synonym.strip())

                example = item.get("example")
                if not isinstance(example, str):
                    example = None

                definition.meanings.append(
                    Meaning(
                        definition=definition_text.strip(),
                        example=example.strip() if example else None,
                        synonyms=sorted(set(synonyms)),
                        part_of_speech=part_of_speech,
                    )
                )

        if not definition.meanings:
            return None
        return definition
