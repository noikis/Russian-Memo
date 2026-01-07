from bot.adapters.translation_cient import TranslationClient, YandexTranslationClient 

class TranslationService():
    def __init__ (self) -> None:
        self.client = YandexTranslationClient()

    def translate(self, text: str) -> str:
        source_lang = "en"
        target_lang = "ru"
        try:
            result = self.client.translate(text, target_lang, source_lang)
            response = f"#translation\n{result}"
        except Exception as e:
            response = "Translation error for text: " + text
        return response
