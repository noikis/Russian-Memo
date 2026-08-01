
import logging
import os
import re
from urllib.parse import urljoin

import vk_api
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard

from bot.services.dictionary_service import DictionaryService
from bot.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


def _get_vk_group_token() -> str:
    token = os.environ.get("VK_GROUP_TOKEN") or os.environ.get("VK_TOKEN")
    if not token:
        raise CommandError(
            "Missing VK bot token. Set VK_GROUP_TOKEN to the VK community access "
            "token. VK_TOKEN is still accepted as a legacy alias."
        )
    return token


def _get_vk_group_id() -> int:
    group_id = os.environ.get("VK_GROUP_ID")
    if not group_id:
        raise CommandError("Missing VK_GROUP_ID for the VK bot.")

    try:
        return int(group_id)
    except ValueError as exc:
        raise CommandError("VK_GROUP_ID must be an integer.") from exc


def _vk_mini_app_url() -> str:
    return f"https://vk.com/app{settings.VK_APP_ID}"


def _vk_web_app_url() -> str:
    return urljoin(settings.PUBLIC_BASE_URL + "/", "account/vk_app/")


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

    def _send_message(self, vk, peer_id: int, text: str, keyboard: str = None) -> None:
        for chunk in self._split_message(text):
            vk.messages.send(
                peer_id=peer_id,
                message=chunk,
                keyboard=keyboard,
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

        vk_session = vk_api.VkApi(token=_get_vk_group_token())
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, _get_vk_group_id())

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

                if text.startswith("/app"):
                    keyboard = VkKeyboard(one_time=False)
                    group_id = _get_vk_group_id()
                    if hasattr(keyboard, "add_vkapps_button"):
                        keyboard.add_vkapps_button(
                            label="Open app",
                            app_id=int(settings.VK_APP_ID),
                            owner_id=-group_id,
                            hash="",
                        )
                    else:
                        keyboard.add_openlink_button(
                            label="Open app",
                            link=_vk_mini_app_url() if settings.VK_APP_ID else _vk_web_app_url(),
                        )
                    self._send_message(
                        vk,
                        peer_id,
                        "Tap the button to open the site.",
                        keyboard=keyboard.get_keyboard(),
                    )
                    continue
            except Exception:
                logger.exception("Unhandled exception while processing VK update")
                self._send_message(vk, peer_id, "Internal error. Try again later.")
