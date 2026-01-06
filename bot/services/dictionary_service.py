from bot.adapters.dictionary_client.client import DictionaryAPIClient

class DictionaryService:
    def __init__(self) -> None:
        self.client = DictionaryAPIClient()

    def define(self, word: str) -> str:
      definition = self.client.get_definition(word)
      if definition is None:
        return self._escape_md_v2("Definition not found.")

      grouped = self._group_meanings_by_part_of_speech(definition.meanings)
      lines = [f"*{self._escape_md_v2(definition.word)}*"]

      for part_of_speech in sorted(grouped.keys(), key=lambda k: (k == "other", k)):
        meanings = grouped[part_of_speech]
        self._add_part_of_speech_section(lines, part_of_speech, meanings)

      return "\n".join(lines).strip()

    def _escape_md_v2(self, text: str) -> str:
      return "".join(
        f"\\{ch}" if ch in r"_*[]()~`>#+-=|{}.!\\"
        else ch
        for ch in text
      )

    def _trim(self, text: str, limit: int) -> str:
      if len(text) <= limit:
        return text
      return text[: max(0, limit - 1)].rstrip() + "…"

    def _group_meanings_by_part_of_speech(self, meanings) -> dict[str, list]:
      grouped: dict[str, list] = {}
      for meaning in meanings:
        key = meaning.part_of_speech or "other"
        grouped.setdefault(key, []).append(meaning)
      return grouped

    def _add_part_of_speech_section(self, lines: list[str], part_of_speech: str, meanings: list) -> None:
      heading = part_of_speech if part_of_speech != "other" else "Other"
      lines.append(f"\n_{self._escape_md_v2(heading)}_")

      self._add_definitions(lines, meanings)
      self._add_synonyms(lines, meanings)

    def _add_definitions(self, lines: list[str], meanings: list) -> None:
      max_defs_per_group = 5
      max_example_chars = 160

      for meaning in meanings[:max_defs_per_group]:
        if not meaning.definition:
          continue
        lines.append(f"• {self._escape_md_v2(meaning.definition)}")
        if meaning.example:
          trimmed = self._trim(meaning.example, max_example_chars)
          lines.append(f"   Example: {self._escape_md_v2(trimmed)}")

      remaining = len(meanings) - max_defs_per_group
      if remaining > 0:
        lines.append(f"   …and {remaining} more")

    def _add_synonyms(self, lines: list[str], meanings: list) -> None:
      max_synonyms = 12
      synonyms_set: set[str] = set()
      for m in meanings:
        for s in m.synonyms:
          if s:
            synonyms_set.add(s)

      if synonyms_set:
        synonyms = sorted(synonyms_set)
        shown = ", ".join(self._escape_md_v2(s) for s in synonyms[:max_synonyms])
        if len(synonyms) > max_synonyms:
          shown += self._escape_md_v2(f" (+{len(synonyms) - max_synonyms} more)")
        lines.append(f"   Synonyms: {shown}")
