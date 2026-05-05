from src.fr_anki.fr_verb_anki import DeckArgs, gen_fr_verb_conj_anki_deck
from argparse import ArgumentParser
from fr_audio.config import Moods, Tenses



def main():

    parser = ArgumentParser(prog="generate_anki_deck", description="add ...")
    parser.add_argument("--deck-id", type=int, default=None, help="deck_id used to indentified the Deck in Anki")
    parser.add_argument("--uid-offset", type=int, default=1, help="unique id that use to ")
    parser.add_argument("--audio-dir", type=str, default="audios", help="the folder to restore the audio files")
    parser.add_argument(
        "--output-name", type=str, default="output", help="Output APKG file Name"
    )
    parser.add_argument("--infinitives", type=str, default=None, help="A list of infinitive verbs separate by ','")
    parser.add_argument("--infinitive-file", type=str, default=None, help="A infinitive verb in a line")


    args = parser.parse_args()
    
    deck_args = DeckArgs(args, Moods.Infinitif, Tenses.Présent)
    gen_fr_verb_conj_anki_deck(deck_args)


if __name__ == "__main__":
    main()
