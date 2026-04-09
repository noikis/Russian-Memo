
import logging
import os
import re

import vk_api
from django.core.management.base import BaseCommand
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from bot.services.dictionary_service import DictionaryService
from bot.services.translation_service import TranslationService

TOKEN = os.environ["VK_TOKEN"]
GROUP_ID = int(os.environ["VK_GROUP_ID"])
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run VK bot (polling)"

    MD_V2_ESCAPE_PATTERN = re.compile(r"\\([_*\[\]()~`>#+\-=|{}.!\\])")

    def _split_message(self, text: str, max_len: int = 3500) -> list[str]:
        if len(text) <= max_len:
            return [text]

        parts: list[str] = []
        current: list[str] = []
        current_len = 0

        for paragraph in text.split("\n\n"):
            if not paragraph:
                continue

            paragraph_len = len(paragraph) + (2 if current else 0)
            if current and current_len + paragraph_len > max_len:
                parts.append("\n\n".join(current))
                current = [paragraph]
                current_len = len(paragraph)
                continue

            if current:
                current_len += 2
            current.append(paragraph)
            current_len += len(paragraph)

        if current:
            parts.append("\n\n".join(current))
        return parts or [text[:max_len]]

    def _send_message(self, vk, peer_id: int, text: str) -> None:
        for chunk in self._split_message(text):
            vk.messages.send(
                peer_id=peer_id,
                message=chunk,
                random_id=0,
            )

    def _normalize_vk_text(self, text: str) -> str:
        text = self.MD_V2_ESCAPE_PATTERN.sub(r"\1", text)
        text = re.sub(r"^\*(.+)\*$", r"\1", text, flags=re.MULTILINE)
        text = re.sub(r"^_(.+)_$", r"\1", text, flags=re.MULTILINE)
        return text

    def handle(self, *args, **options):
        logger.info("VK bot started")
        print("VK bot started")

        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, GROUP_ID)

        dictionary_service = DictionaryService()
        translation_service = TranslationService()

        for event in longpoll.listen():
            print(f"Received VK event: {event.type}")
            if event.type != VkBotEventType.MESSAGE_NEW:
                continue

            if not event.from_user:
                continue

            message = event.message
            text = (message.text or "").strip()
            if not text:
                continue

            peer_id = message.peer_id

            try:
                if text.startswith("/define"):
                    word = text.removeprefix("/define").strip()
                    if not word:
                        self._send_message(vk, peer_id, "Usage: /define <word>")
                        continue

                    response = self._normalize_vk_text(dictionary_service.define(word))
                    self._send_message(vk, peer_id, response)
                    continue

                if text.startswith("/translate"):
                    query = text.removeprefix("/translate").strip()
                    if not query:
                        self._send_message(vk, peer_id, "Usage: /translate <text>")
                        continue

                    response = translation_service.translate(query)
                    self._send_message(vk, peer_id, response)
                    continue
            except Exception:
                logger.exception("Unhandled exception while processing VK update")
                self._send_message(vk, peer_id, "Internal error. Try again later.")
