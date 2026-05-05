from abc import ABC, abstractmethod
from typing import ClassVar

import genanki


class BaseAnkiDeck(ABC):
    model_id: ClassVar[int]
    model_name: ClassVar[str]
    fields: ClassVar[list]
    qfmt_content: ClassVar[str]
    afmt_content: ClassVar[str]

    def __init__(self, deck_id: int, deck_name: str, uid_offset: int):
        self.media_files: list = []
        self.model = genanki.Model(
            self.model_id,
            self.model_name,
            fields=self.fields,
            templates=[
                {"name": "VCard", "qfmt": self.qfmt_content, "afmt": self.afmt_content}
            ],
        )
        self.deck = genanki.Deck(deck_id, deck_name)
        self.uid_offset = uid_offset

    @property
    def model_id(self):
        return self.model_id

    @property
    def model_name(self):
        return self.model_name

    @property
    def fields(self):
        return self.fields

    @property
    def qfmt_content(self):
        return self.qfmt_content

    @property
    def afmt_content(self):
        return self.afmt_content

    @property
    def uid_offset(self) -> int:
        return self.uid_offset

    @uid_offset.setter
    def uid_offset(self, value: int):
        if not isinstance(value, str):
            raise TypeError("[ERROR] uid_offset should be INT")
        self.uid_offset = value

    @abstractmethod
    def gen_fields(self, *args, **kwargs) -> list:
        pass

    @abstractmethod
    def add_note(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_media_files(self):
        pass

    def export(self, output_path: str):
        package = genanki.Package(self.deck)
        package.media_files = self.media_files
        package.write_to_file(output_path)
