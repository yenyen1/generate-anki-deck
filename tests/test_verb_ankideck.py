from fr_anki.fr_verb_anki import DeckArgs, FrVerbConjAnkiDeck
from fr_anki.main import create_parser

from fr_audio.config import Moods, Tenses
from genanki import Model, Deck

import shutil
from pathlib import Path
import pytest


def test_ankideck_init_type_check():
    parser = create_parser()
    args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)

    # Paras inherited from BaseAnkiDeck(ABC)
    assert isinstance(verb_deck.model_id, int)
    assert isinstance(verb_deck.model_name, str)
    assert isinstance(verb_deck.fields, list)
    assert isinstance(verb_deck.afmt_content, str)
    assert isinstance(verb_deck.qfmt_content, str)
    assert isinstance(verb_deck.media_files, list)
    assert isinstance(verb_deck.model, Model)
    assert isinstance(verb_deck.deck, Deck)
    assert isinstance(verb_deck.start_pid, int)
    assert verb_deck.start_pid == deck_args.start_pid

    # para specific for FrVerbConjAnkiDeck
    assert len(verb_deck.fields) == 14
    assert isinstance(verb_deck.mood, str)
    assert isinstance(verb_deck.tense, str)
    assert isinstance(verb_deck.audio_folder, Path)
    assert verb_deck.audio_folder == Path(deck_args.audio_folder)
    assert isinstance(verb_deck.conjugation_dict, dict)


def test_ankideck_tense():
    parser = create_parser()

    args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)
    assert verb_deck.mood == Moods.Indicatif
    assert verb_deck.tense == Tenses.PasséComposé

    args = parser.parse_args(["verb", "--tense", "future", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)
    assert verb_deck.mood == Moods.Indicatif
    assert verb_deck.tense == Tenses.FuturSimple

    args = parser.parse_args(
        ["verb", "--tense", "imperative", "--infinitives", "avoir"]
    )
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)
    assert verb_deck.mood == Moods.Imperatif
    assert verb_deck.tense == Tenses.ImperatifPrésent


def test_ankideck_start_pid():
    # control under @property
    parser = create_parser()
    args = parser.parse_args(
        ["verb", "--tense", "past", "--infinitives", "avoir", "--start-pid", "10"]
    )
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)
    assert verb_deck.start_pid == 10
    verb_deck.start_pid += 5
    assert verb_deck.start_pid == 15


def test_ankideck_media_files():
    # no control
    parser = create_parser()
    args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)

    assert isinstance(verb_deck.media_files, list)
    assert len(verb_deck.media_files) == 0
    verb_deck.media_files.append("test1")
    assert len(verb_deck.media_files) == 1


def test_ankideck_conjugation_dict():
    # no control
    parser = create_parser()
    args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)

    assert isinstance(verb_deck.conjugation_dict, dict)
    assert len(verb_deck.conjugation_dict) == 0
    verb_deck.conjugation_dict["test1"] = []
    assert len(verb_deck.conjugation_dict) == 1


def test_ankideck_gen_fields():
    parser = create_parser()
    args = parser.parse_args(["verb", "--tense", "present", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)
    expect_result = [
        "3",
        "avoir",
        "présent",
        "j'ai/tu as",
        "[sound:avoir.mp3]",
        "[sound:j'ai.mp3]",
        "[sound:tu_as.mp3]",
    ]
    expect_result = expect_result[:14] + [""] * (14 - len(expect_result))
    actuall_result = verb_deck.gen_fields(3, "avoir", ["j'ai", "tu as"])
    assert expect_result == actuall_result


def test_ankideck_add_note(capsys):
    # check how imperative works?
    pass
    # parser = create_parser()
    # args = parser.parse_args(["verb", "--tense", "present", "--infinitives", "avoir"])
    # deck_args = DeckArgs(parser, args)
    # verb_deck = FrVerbConjAnkiDeck(deck_args)
    # actuall_result = verb_deck.gen_fields(3, "avoir", ["j'ai", "tu as"])

    # mynote = Note(verb_deck.model, actuall_result)
    # cuptured = capsys.readouterr()
    # assert mynote.fields == ""


def test_set_media_files():
    parser = create_parser()
    args = parser.parse_args(["verb", "--tense", "present", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)

    assert len(verb_deck.conjugation_dict) == 0
    verb_deck.set_media_files()
    assert verb_deck.media_files == []

    verb_deck.build_conjugation_dict(["avoir"])
    verb_deck.set_media_files()
    expect_result = [(verb_deck.audio_folder / "avoir.mp3").resolve()]
    expect_result += [
        (verb_deck.audio_folder / f"{e.replace(' ', '_')}.mp3").resolve()
        for e in verb_deck.conjugation_dict.get("avoir")
    ]
    assert verb_deck.media_files == expect_result


def test_export():
    pass


def test_build_conjugation_dict(capsys):
    parser = create_parser()
    args = parser.parse_args(["verb", "--tense", "present", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)

    verb_deck.build_conjugation_dict(["happy"])
    captured = capsys.readouterr()
    assert "[Skip] Can not conjugate" in captured.out

    verb_deck.build_conjugation_dict(["avoir"])
    expect_result = [
        "j'ai",
        "tu as",
        "il a",
        "elle a",
        "on a",
        "nous avons",
        "vous avez",
        "ils ont",
        "elles ont",
    ]
    assert verb_deck.conjugation_dict.get("avoir") == expect_result


def test_download_audios(temp_output_dir):
    parser = create_parser()
    args = parser.parse_args(["verb", "--tense", "present", "--infinitives", "avoir", "--audio-dir", str(temp_output_dir)])
    deck_args = DeckArgs(parser, args)
    verb_deck = FrVerbConjAnkiDeck(deck_args)
    verb_deck.build_conjugation_dict(["avoir"])

    assert verb_deck.audio_folder == temp_output_dir
    assert not (temp_output_dir / "j'ai.mp3").exists()

    verb_deck.download_audios()
    assert (temp_output_dir / "avoir.mp3").exists()
    assert (temp_output_dir / "j'ai.mp3").exists()
    assert (temp_output_dir / "tu_as.mp3").exists()
    assert (temp_output_dir / "il_a.mp3").exists()
    assert (temp_output_dir / "elle_a.mp3").exists()
    assert (temp_output_dir / "on_a.mp3").exists()
    assert (temp_output_dir / "nous_avons.mp3").exists()
    assert (temp_output_dir / "vous_avez.mp3").exists()
    assert (temp_output_dir / "ils_ont.mp3").exists()
    assert (temp_output_dir / "elles_ont.mp3").exists()


@pytest.fixture
def temp_output_dir():
    # Setup: Define where to put test files
    base_tmp = Path("test_tmp")
    # test_path = base_tmp / "tense"

    # Yield: Hand this path to the test function
    yield base_tmp

    # Teardown: This runs AFTER the test function finishes
    if base_tmp.exists():
        shutil.rmtree(base_tmp)
        print(f"\nSuccessfully cleaned up {base_tmp}")
