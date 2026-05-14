from fr_anki.fr_verb_anki import DeckArgs, gen_fr_verb_conj_anki_deck
from argparse import ArgumentParser


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="fr-anki", description="A tool to generate Anki Deck for learning French"
    )

    subparser = parser.add_subparsers(dest="command", metavar="<command>")

    verb_parser = subparser.add_parser(
        "verb",
        help="Generate an Anki deck for practicing French verb conjugation typing",
    )
    verb_parser.add_argument(
        "--deck-id",
        type=int,
        default=None,
        help="Anki deck identifier (specify --deck-id and --start-pid if you want to import new cards into an existing Anki deck)",
    )
    verb_parser.add_argument(
        "--start-pid",
        type=int,
        default=1,
        help="Starting value for the card primary ID (Specify --deck-id and --start-pid if you want to import new cards into an existing Anki deck)",
    )
    verb_parser.add_argument(
        "--audio-dir",
        type=str,
        default="audios",
        help="Destination folder for downloaded audio files",
    )
    verb_parser.add_argument(
        "--output-name", type=str, default="output", help="Output APKG file name"
    )
    verb_parser.add_argument(
        "--infinitives",
        type=str,
        default=None,
        help='Comma-separated infinitive verbs (e.g., "avoir,prendre")',
    )
    verb_parser.add_argument(
        "--infinitive-file",
        type=str,
        default=None,
        help="A file containing one infinitive verb per line",
    )
    verb_parser.add_argument(
        "--tense",
        type=str,
        required=True,
        help="The verb tense practiced in this deck (supported values: present, future, past, past simple, conditional, imperative)",
    )

    #
    subparser_sentence = subparser.add_parser(
        "sentence", help="Generate Anki Deck for French sentence typing test"
    )
    subparser_sentence.add_argument("--test2", type=str, help="...")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    elif args.command == "verb":
        deck_args = DeckArgs(parser, args)
        gen_fr_verb_conj_anki_deck(deck_args)

    elif args.command == "sentence":
        pass


if __name__ == "__main__":
    main()
