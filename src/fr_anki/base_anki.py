from abc import ABC, abstractmethod
from typing import ClassVar

import genanki


class BaseAnkiDeck(ABC):
    _model_id: ClassVar[int]
    _model_name: ClassVar[str]
    _fields: ClassVar[list[dict[str, str]]]
    _qfmt_content: ClassVar[str]
    _afmt_content: ClassVar[str]

    def __init__(self, deck_id: int, deck_name: str, start_pid: int):
        self.media_files: list = []
        self._model = genanki.Model(
            self.model_id,
            self.model_name,
            fields=self.fields,
            templates=[
                {"name": "VCard", "qfmt": self.qfmt_content, "afmt": self.afmt_content}
            ],
        )
        self._deck = genanki.Deck(deck_id, deck_name)
        self._start_pid = start_pid

    @property
    def model(self):
        return self._model

    @property
    def deck(self):
        return self._deck

    @property
    def model_id(self):
        return self._model_id

    @property
    def model_name(self):
        return self._model_name

    @property
    def fields(self):
        return self._fields

    @property
    def qfmt_content(self):
        return self._qfmt_content

    @property
    def afmt_content(self):
        return self._afmt_content

    @property
    def start_pid(self):
        return self._start_pid

    @start_pid.setter
    def start_pid(self, value: int):
        if not isinstance(value, int):
            raise TypeError("[ERROR] start_pid should be INT")
        self._start_pid = value

    # @property
    # def media_files(self) -> list[str]:
    #     return self._media_files

    # @media_files.setter
    # def media_files(self, value: str):
    #     return self._media_files

    @abstractmethod
    def gen_fields(self, *args, **kwargs) -> list[str]:
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
