from fr_anki.fr_verb_anki import DeckArgs  # , BaseAnkiDeck, gen_fr_verb_conj_anki_deck
from fr_anki.main import create_parser

from fr_audio.config import Moods, Tenses

import pytest


def test_deckargs_parse_tense(capsys):
    parser = create_parser()

    expect_emsg = "argument --tense: expected one argument"
    with pytest.raises(SystemExit):
        parser.parse_args(["verb", "--tense", "--infinitives", "avoir"])
    captured = capsys.readouterr()
    print(captured.err)
    assert expect_emsg in captured.err

    expect_emsg = "the following arguments are required: --tense"
    with pytest.raises(SystemExit):
        parser.parse_args(["verb"])
    captured = capsys.readouterr()
    print(captured.err)
    assert expect_emsg in captured.err

    test_args = parser.parse_args(["verb", "--tense", "na", "--infinitives", "avoir"])
    expect_emsg = "na is not supported. (supported values: present, future, past, past-simple, conditional, imperative)"
    with pytest.raises(SystemExit):
        DeckArgs(parser, test_args)
    captured = capsys.readouterr()
    assert expect_emsg in captured.err

    test_args = parser.parse_args(
        ["verb", "--tense", "present", "--infinitives", "avoir"]
    )
    deckargs = DeckArgs(parser, test_args)
    assert deckargs.mood == Moods.Indicatif
    assert deckargs.tense == Tenses.Présent


def test_deckargs_parse_infinitives(capsys):
    parser = create_parser()

    expect_emsg = "argument --infinitives: expected one argument"
    with pytest.raises(SystemExit):
        parser.parse_args(["verb", "--tense", "present", "--infinitives"])
    captured = capsys.readouterr()
    assert expect_emsg in captured.err

    expect_emsg = "You must provide either --infinitives or --infinitive-file"
    test_args = parser.parse_args(["verb", "--tense", "present"])
    with pytest.raises(SystemExit):
        DeckArgs(parser, test_args)
    captured = capsys.readouterr()
    assert expect_emsg in captured.err

    expect_emsg = "You must provide either --infinitives or --infinitive-file"
    test_args = parser.parse_args(["verb", "--tense", "present", "--infinitives", ""])
    with pytest.raises(SystemExit):
        DeckArgs(parser, test_args)
    captured = capsys.readouterr()
    assert expect_emsg in captured.err

    expect_emsg = "Provide only one of --infinitives or --infinitive-file"
    test_args = parser.parse_args(
        ["verb", "--tense", "past", "--infinitives", "a", "--infinitive-file", "a.txt"]
    )
    with pytest.raises(SystemExit):
        DeckArgs(parser, test_args)
    captured = capsys.readouterr()
    assert expect_emsg in captured.err

    expect_emsg = "Infinitive file not found: a.txt"
    test_args = parser.parse_args(
        ["verb", "--tense", "present", "--infinitive-file", "a.txt"]
    )
    with pytest.raises(SystemExit):
        DeckArgs(parser, test_args)
    captured = capsys.readouterr()
    assert expect_emsg in captured.err

    test_args = parser.parse_args(
        ["verb", "--tense", "present", "--infinitives", "avoir, aller,prendre \n"]
    )
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.infinitives == ["avoir", "aller", "prendre"]

    test_args = parser.parse_args(
        ["verb", "--tense", "present", "--infinitive-file", "tests/data/test_verb.txt"]
    )
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.infinitives == ["avoir", "aller", "prendre"]


def test_deckargs_parse_deck_id():
    parser = create_parser()

    test_args = parser.parse_args(
        ["verb", "--tense", "present", "--infinitives", "avoir", "--deck-id", "123"]
    )
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.deck_id == 123

    test_args = parser.parse_args(
        ["verb", "--tense", "present", "--infinitives", "avoir"]
    )
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.deck_id
    assert isinstance(deck_args.deck_id, int)


def test_deckargs_deck_name():
    parser = create_parser()

    test_args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    except_result = f"[FR] {test_args.tense} conjugation test"
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.deck_name == except_result


def test_deckargs_start_pid(capsys):
    parser = create_parser()

    test_args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.start_pid == 1

    test_args = parser.parse_args(
        ["verb", "--tense", "past", "--infinitives", "avoir", "--start-pid", "10"]
    )
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.start_pid == 10

    expect_emsg = "argument --start-pid: invalid int value:"
    with pytest.raises(SystemExit):
        test_args = parser.parse_args(
            ["verb", "--tense", "past", "--infinitives", "avoir", "--start-pid", "10a"]
        )
    cuptured = capsys.readouterr()
    assert expect_emsg in cuptured.err


def test_deckargs_audio_folder():
    parser = create_parser()

    test_args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.audio_folder == "audios"

    test_args = parser.parse_args(
        ["verb", "--tense", "past", "--infinitives", "avoir", "--audio-dir", "a"]
    )
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.audio_folder == "a"


def test_deckargs_apkg_output_name():
    parser = create_parser()
    test_args = parser.parse_args(["verb", "--tense", "past", "--infinitives", "avoir"])
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.apkg_output_name == "output"

    test_args = parser.parse_args(
        ["verb", "--tense", "past", "--infinitives", "avoir", "--output-name", "a"]
    )
    deck_args = DeckArgs(parser, test_args)
    assert deck_args.apkg_output_name == "a"
