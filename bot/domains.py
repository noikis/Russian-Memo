from dataclasses import dataclass, field

@dataclass
class Meaning:
    synonyms: list[str] = field(default_factory=list)
    definition: str | None = None
    example: str | None = None
    part_of_speech: str | None = None

@dataclass
class Definition:
    word: str
    meanings: list["Meaning"] = field(default_factory=list)
