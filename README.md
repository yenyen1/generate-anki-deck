# Generate French learning Anki Deck

[![PyPI - Version](https://img.shields.io/pypi/v/fr-anki.svg)](https://pypi.org/project/fr-anki)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fr-anki.svg)](https://pypi.org/project/fr-anki)

A CLI tool that creates French verb conjugation typing decks for Anki. Simply input a list of infinitives and choose which tenses to practice. The tool generates an APKG file ready to be imported into Anki. Currently supported common tenses include: indicatif présent, indicatif futur simple, indicatif passé composé, indicatif passé simple, conditionnel présent, and impératif présent.

## Installation

### From PyPI
```
pip install fr-anki
```

### From Git
```
git clone https://github.com/yenyen1/generate-anki-deck.git 
cd generate-anki-deck 
pip install .
```

### Print help
```
fr-anki --help
```

**NOTE**: The first run may take about a minute to download the model.

## Usage: Generate French verb conjugation typing deck

### Input verbs list by `--infinitives`
Use comma-separated infinitive verbs to input verbs list by `--infinitives` option.

```
fr-anki verb --tense present --infinitives "avoir,prendre,aller"
```

### Input verbs list by `--infinitive-file`
Use a TXT file containing one infinitive verb per line to input verbs list.

```
fr-anki verb --tense present --infinitive-file verbs.txt
```

### Example of verb list `verbs.txt`

```
avoir
prendre
aller
```
### Import new cards into an existing Anki deck

Specify `--deck-id` (the ID of the existing Anki deck you want to import into) and `--start-pid` (the next consecutive primary ID after your existing cards) if you want to import new cards into an existing Anki deck.

```
fr-anki verb --tense present --infinitive-file verbs.txt --deck-id 132526148 --start-pid 52
```

### Example of output Anki Deck `output.apkg`

- **Front**

    It shows the infinitive form with audio. You can type the conjugations separated by `/` in the input box.

    <img src="https://raw.githubusercontent.com/yenyen1/generate-anki-deck/main/images/verb_front.png" width="80%">

- **Back**

    It displays all conjugation forms with audio and highlights your typing errors in different colors.

    <img src="https://raw.githubusercontent.com/yenyen1/generate-anki-deck/main/images/verb_back.png" width="80%">



## Credits
This tool uses the following Python libraries:
- [genanki](https://github.com/kerrickstaley/genanki/tree/main): A Python 3 library for generating Anki decks
- [fr-audio](https://github.com/yenyen1/french-conjugation-verb-audio): A tool for downloading MP3 audio of French verb conjugations that leveraging [verbecc](https://github.com/bretttolbert/verbecc?tab=readme-ov-file) (for verb conjugation enhanced with machine learning techniques) and [edge-tts](https://github.com/rany2/edge-tts?tab=readme-ov-file) (for accessing to Microsoft Edge’s online text-to-speech service from Python).