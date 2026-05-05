from base_anki import BaseAnkiDeck

from pathlib import Path
from argparse import Namespace
import random

import fr_audio.main_cli as fr_audio
from fr_audio.config import Model
import genanki

class FrVerbConjAnkiDeck(BaseAnkiDeck):
    model_id = 1475388531
    model_name = "FrVerbConjModel"
    fields = [
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
    qfmt_content = """
        <div style="text-align: center;">
            <div style="color: gray; font-size: 20px;">{{tense}}</div> 
            <div style="color: blue; font-size: 30px; font-weight: bold;">{{infinitive}}</div>{{inf_audio}}
            <br><br>
            {{type:conjugations}}
        </div>
        """
    afmt_content = """
        <div style="text-align: center;">{{FrontSide}}
            <hr id="answer">
            <div style="color: gray; font-size: 16px;">
                Je: {{je_audio}}; Tu: {{tu_audio}}; Il: {{il_audio}}; Elle: {{elle_audio}}; On: {{on_audio}}<br>
                Nous: {{nous_audio}}; Vous: {{vous_audio}}; Ils: {{ils_audio}}; Elles: {{elles_audio}}<br>
            </div>
        </div>
        """

    def __init__(self, deck_args: DeckArgs):
        super().__init__(deck_args.deck_id, deck_args.deck_name, deck_args.uid_offset)
        self.mood = deck_args.mood
        self.tense = deck_args.tense
        self.conjugation_dict = {}
        self.audio_folder = Path(deck_args.audio_floder)

    @property
    def mood(self):
        return self.mood

    @property
    def tense(self):
        return self.tense

    @property
    def audio_folder(self):
        return self.audio_folder

    def gen_fields(
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
        return fields

    def add_note(self):
        """
        Populate the Anki deck with notes generated from the verb conjugation dictionary,
        using the specified model and starting ID offset.
        """

        for infinitive, conj in self.conjugation_dict.items():
            my_fields = self.gen_fields(self.uid_offset, infinitive, self.tense, conj)
            my_note = genanki.Note(self.model, my_fields)
            self.deck.add_note(my_note)

            self.uid_offset += 1

    def build_conjugation_dict(self, infinitives: list[str]):
        """
        Build a conjugation dictionary that maps infinitives to corresponding conjugation phrases list

        Args:
            infinitives (list[str]): a list of infinitives
        """

        for infinitive in infinitives:
            conj = fr_audio.fetch_verb_conjugation(
                "fr", infinitive, self.mood, self.tense
            )
            if len(conj) > 0:
                self.conjugation_dict[infinitive] = conj
            else:
                print(f"[Skip] Can not conjugate {infinitive} for {self.tense}")

    def download_audios(self) -> bool:
        """
        Download audio MP3 files for all infinitives and conjugation phrases.

        Returns:
            bool: Return True if at least ONE audio files were downloaded.
        """

        infinitives = list(self.conjugation_dict.keys())
        fr_audio.download_audios(self.audio_folder, Model.VoiceModel, infinitives)

        for infinitive in infinitives:
            conj = self.conjugation_dict.get(infinitive)
            result = fr_audio.download_audios(self.audio_folder, Model.VoiceModel, conj)

            if not result:
                conj.pop(infinitive, None)
                print(
                    f"[Skip] Can not download {infinitive} audio MP3 for {self.tense}"
                )

        return len(self.conjugation_dict) > 0

    def set_media_files(self):
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


class DeckArgs:
    def __init__(self, args: Namespace, mood: str, tense: str):
        self.deck_id = (
            args.deck_id if args.deck_id else random.randrange(1 << 30, 1 << 31)
        )
        self.deck_name = f"[FR] {tense} tense conjugation test"
        self.uid_offset = args.uid_offset
        self.audio_folder = args.audio_dir
        self.apkg_output_name = args.output_name
        self.mood = mood
        self.tense = tense

        if not args.deck_id:
            print(f"[INFO] Genarate new deck_id: {self.deck_id}")

    @property
    def deck_id(self):
        return self.deck_id

    @property
    def deck_name(self):
        return self.deck_name

    @property
    def uid_offset(self):
        return self.uid_offset

    @property
    def audio_folder(self):
        return self.audio_folder

    @property
    def apkg_output_name(self):
        return self.apkg_output_name

    @property
    def mood(self):
        return self.mood

    @property
    def tense(self):
        return self.tense

def gen_fr_verb_conj_anki_deck(deck_args: DeckArgs):
    # Setup Model and Deck
    my_model = FrVerbConjAnkiDeck(deck_args)

    # infinitives = ["aller", "devoir", "faire"]
    if deck_args.infinitives:
        infinitives = deck_args.infinitives.split(",")
    elif deck_args.infinitive_file:
        with open(deck_args.infinitive_file, 'r') as f:
            data = f.read()
        print(data.split('\n'))
    

    # generate conjugation and download audios
    my_model.build_conjugation_dict(infinitives)
    success = my_model.download_audios()

    if success:
        print("[INFO] Finished generating conjugation and downloaded audios")

        # Add card
        my_model.add_note()
        print("[INFO] Finished adding Anki cards")

        # Generate APKG file (automatically generate collection.anki21)
        my_model.set_media_files()
        my_model.export(f"{deck_args.apkg_output_name}.apkg")
        print("[INFO] finished generate apkg file.")
    else:
        print(
            "[ERROR] No input infinitives can be successfully conjugated and downloaded"
        )