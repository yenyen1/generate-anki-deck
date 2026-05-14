from fr_anki.base_anki import BaseAnkiDeck

from pathlib import Path
from argparse import Namespace, ArgumentParser
import random

from fr_audio.main_cli import fetch_verb_conjugation, download_audios
from fr_audio.config import Model, Moods, Tenses
import genanki


class DeckArgs:
    def __init__(self, parser: ArgumentParser, args: Namespace):
        self._mood: str = None
        self._tense: str = None
        self._parse_tense(parser, args)

        self._infinitives: list[str] = None
        self._parse_infinitives(parser, args)

        self._deck_id: int = None
        self._parse_deck_id(args)

        self._deck_name: str = f"[FR] {args.tense} conjugation test"
        self._start_pid: int = args.start_pid
        self._audio_folder: str = args.audio_dir
        self._apkg_output_name: str = args.output_name

    def _parse_infinitives(self, parser: ArgumentParser, args: Namespace):
        has_infinitives = bool(args.infinitives)
        has_file = bool(args.infinitive_file)
        if not has_infinitives and not has_file:
            parser.error("You must provide either --infinitives or --infinitive-file")
        if has_infinitives and has_file:
            parser.error("Provide only one of --infinitives or --infinitive-file")
        if has_infinitives:
            self._infinitives = [
                verb.strip() for verb in args.infinitives.split(",") if verb.strip()
            ]
        else:
            try:
                with open(args.infinitive_file, "r") as f:
                    self._infinitives = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                parser.error(f"Infinitive file not found: {args.infinitive_file}")

    def _parse_tense(self, parser: ArgumentParser, args: Namespace):
        tense_mapping = {
            "present": (Moods.Indicatif, Tenses.Présent),
            "future": (Moods.Indicatif, Tenses.FuturSimple),
            "past": (Moods.Indicatif, Tenses.PasséComposé),
            "past-simple": (Moods.Indicatif, Tenses.PasséSimple),
            "conditional": (Moods.Conditionnel, Tenses.Présent),
            "imperative": (Moods.Imperatif, Tenses.ImperatifPrésent),
        }

        result = tense_mapping.get(args.tense)
        if not result:
            parser.error(
                f"{args.tense} is not supported. "
                "(supported values: present, future, past, "
                "past-simple, conditional, imperative)"
            )
        self._mood, self._tense = result

    def _parse_deck_id(self, args: Namespace):
        if args.deck_id:
            self._deck_id = args.deck_id
        else:
            self._deck_id = random.getrandbits(63)
            print(f"[INFO] Generated new deck_id: {self.deck_id}")

    @property
    def infinitives(self):
        return self._infinitives

    @property
    def deck_id(self):
        return self._deck_id

    @property
    def deck_name(self):
        return self._deck_name

    @property
    def start_pid(self):
        return self._start_pid

    @property
    def audio_folder(self):
        return self._audio_folder

    @property
    def apkg_output_name(self):
        return self._apkg_output_name

    @property
    def mood(self):
        return self._mood

    @property
    def tense(self):
        return self._tense


class FrVerbConjAnkiDeck(BaseAnkiDeck):
    _model_id = 1475388531
    _model_name = "FrVerbConjModel"
    _fields = [
        {"name": "uid"},
        {"name": "infinitive"},
        {"name": "tense"},
        {"name": "conjugations"},
        {"name": "inf_audio"},
        {"name": "je_audio"},
        {"name": "tu_audio"},
        {"name": "il_audio"},
        {"name": "elle_audio"},
        {"name": "on_audio"},
        {"name": "nous_audio"},
        {"name": "vous_audio"},
        {"name": "ils_audio"},
        {"name": "elles_audio"},
    ]
    _qfmt_content = """
        <div style="text-align: center;">
            <div style="color: gray; font-size: 20px;">{{tense}}</div> 
            <div style="color: blue; font-size: 30px; font-weight: bold;">{{infinitive}}</div>{{inf_audio}}
            <br><br>
            {{type:conjugations}}
        </div>
        """
    _afmt_content = """
        <div style="text-align: center;">{{FrontSide}}
            <hr id="answer">
            <div style="color: gray; font-size: 16px;">
                Je: {{je_audio}}; Tu: {{tu_audio}}; Il: {{il_audio}}; Elle: {{elle_audio}}; On: {{on_audio}}<br>
                Nous: {{nous_audio}}; Vous: {{vous_audio}}; Ils: {{ils_audio}}; Elles: {{elles_audio}}<br>
            </div>
        </div>
        """

    def __init__(self, deck_args: DeckArgs):
        super().__init__(deck_args.deck_id, deck_args.deck_name, deck_args.start_pid)
        self._mood: str = deck_args.mood
        self._tense: str = deck_args.tense
        self.conjugation_dict: dict[str, str] = {}
        self._audio_folder: Path = Path(deck_args.audio_folder)

    @property
    def mood(self):
        return self._mood

    @property
    def tense(self):
        return self._tense

    @property
    def audio_folder(self):
        return self._audio_folder

    def _gen_fields(
        self, uid: int, infinitive: str, conjugation_list: list[str]
    ) -> list[str]:
        """
        Generate fields list for the french conjugation Anki Model.

        Args:
            uid (int): Card unique ID
            infinitive (str): Infinitive verb
            conjugations (list[str]): A list of French conjugated phrases

        Returns:
            list[str]: fields for the french conjugation Anki Model
        """

        def gen_sound_dir(name: str):
            return f"[sound:{name.replace(' ', '_')}.mp3]"

        inf_sound = gen_sound_dir(infinitive)
        fields = [
            str(uid),
            infinitive,
            self.tense,
            "/".join(conjugation_list),
            inf_sound,
        ]

        for conj in conjugation_list:
            fields.append(gen_sound_dir(conj))
        fields = fields[:14] + [""] * max(0, 14 - len(fields))

        return fields

    def _add_note(self):
        """
        Populate the Anki deck with notes generated from the verb conjugation dictionary,
        using the specified model and starting PID.
        """
        if len(self.conjugation_dict) == 0:
            raise ValueError(
                "None of the input infinitives was processed to conjugation forms. Please ensure that you provide the correct infinitives, or make sure to run self.build_conjugation_dict before calling self.add_note."
            )

        for infinitive, conj in self.conjugation_dict.items():
            my_fields = self._gen_fields(self.start_pid, infinitive, conj)
            my_note = genanki.Note(self.model, my_fields)
            self.deck.add_note(my_note)

            self.start_pid += 1

    def _build_conjugation_dict(self, infinitives: list[str]):
        """
        Build a conjugation dictionary that maps infinitives to corresponding conjugation phrases list

        Args:
            infinitives (list[str]): a list of infinitives
        """
        for infinitive in infinitives:
            try:
                conj = fetch_verb_conjugation("fr", infinitive, self.mood, self.tense)
                self.conjugation_dict[infinitive] = conj
            except Exception as e:
                print(f"[Skip] Can not conjugate {infinitive} for {self.tense}: {e}")

    def _download_audios(self) -> int:
        """
        Download audio MP3 files for all infinitives and conjugation phrases.

        Returns:
            int: Return the number of infinitives that were successfully conjugated and downloaded.
        """
        if len(self.conjugation_dict) == 0:
            raise ValueError(
                "None of the input infinitives was processed to conjugation forms. Please ensure that you provide the correct infinitives, or make sure to run self.build_conjugation_dict before calling self.add_note."
            )

        infinitives = list(self.conjugation_dict.keys())
        download_audios(self.audio_folder, Model.VoiceModel, infinitives)

        for infinitive in infinitives:
            conj = self.conjugation_dict.get(infinitive)
            result = download_audios(self.audio_folder, Model.VoiceModel, conj)

            if not result:
                conj.pop(infinitive, None)
                print(
                    f"[Skip] Can not download {infinitive} audio MP3 for {self.tense}"
                )

        return len(self.conjugation_dict)

    def _set_media_files(self):
        """
        Generate absolute path for all audio MP3 files and set it to Genanki media files
        """

        def gen_abs_path(audio_folder: Path, name: str):
            file = audio_folder / f"{name.replace(' ', '_')}.mp3"
            return file.resolve()

        for infinitive, conj in self.conjugation_dict.items():
            self.media_files.append(gen_abs_path(self.audio_folder, infinitive))
            for c in conj:
                self.media_files.append(gen_abs_path(self.audio_folder, c))


def gen_fr_verb_conj_anki_deck(deck_args: DeckArgs):
    """
    Generate French verb conjugation Anki Deck

    Args:
        deck_args (DeckArgs): input DeckArgs
    """
    # Setup Model and Deck
    my_model = FrVerbConjAnkiDeck(deck_args)

    # generate conjugation and download audios
    my_model._build_conjugation_dict(deck_args.infinitives)
    success_num = my_model._download_audios()
    print(f"[INFO] Finished generating {success_num} infinitives' audio files")

    try:
        my_model._add_note()
        my_model._set_media_files()
        print("[INFO] Finished adding Anki cards an media files")

        # Generate APKG file (automatically generate collection.anki21)
        my_model.export(f"{deck_args.apkg_output_name}.apkg")
        print(f"[INFO] finished generate {deck_args.apkg_output_name}.apkg file.")
    except Exception as e:
        raise RuntimeError(e)
