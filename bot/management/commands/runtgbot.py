import os
import logging
from django.core.management.base import BaseCommand

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.services.dictionary_service import DictionaryService
from bot.services.translation_service import TranslationService

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run Telegram bot (polling)"


    def handle(self, *args, **options):
        app = Application.builder().token(TOKEN).build()

        def _split_message(text: str, max_len: int = 3500) -> list[str]:
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

        async def define(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            if not context.args or len(context.args) == 0:
                await update.message.reply_text("Usage: /define <word>")
                return
                
            word = context.args[0]
            service = DictionaryService()
            response = service.define(word)
            for chunk in _split_message(response):
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN_V2)
        
        async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            if not context.args or len(context.args) == 0:
                await update.message.reply_text("Usage: /translate <text>")
                return

            text = " ".join(context.args)
            service = TranslationService()
            response = service.translate(text)
            await update.message.reply_text(response)


        async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
            logger.exception("Unhandled exception while processing update", exc_info=context.error)
        

        

        app.add_handler(CommandHandler("define", define))
        app.add_handler(CommandHandler("translate", translate))
        app.add_error_handler(on_error)
        app.run_polling()
