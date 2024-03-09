import os.path

import genanki
import pandas as pd

from anki_flashcards.anki_model import LanguageNote, LANGUAGE_MODEL
from anki_flashcards.dependency_analysis import count_word_occurrences
from common.utils import parse_word_match, sanitized_filename


def color_literal_translation(twi, eng_lit, word_match):
    highlight_colors = [
        "gold",
        "darkorange",
        "limegreen",
        "deepskyblue",
        "darkblue",
        "lightpink",
        "lightcoral",
        "darkred"
    ]

    replacements = parse_word_match(word_match)
    replacements = [(*r, highlight_colors[i % len(highlight_colors)]) for i, r in enumerate(replacements)]

    # parsing twi
    twi_color = ""
    for twi_word, eng_word, highlight_color in replacements:
        word_start = twi.lower().find(twi_word.lower())
        if word_start == -1:
            raise ValueError(f"'{twi_word}' could not be found in '{twi}'!")
        twi_color += twi[:word_start] + f"<span style='color:{highlight_color}'>{twi_word}</span>"  # f"[{twi_word}]"
        twi = twi[word_start + len(twi_word):]
    twi_color += twi

    eng_lit_color = eng_lit
    for twi_word, eng_word, highlight_color in sorted(replacements, key=lambda tup: len(tup[1]), reverse=True):
        initial = True
        while True:
            pos = eng_lit.lower().find(eng_word.lower())
            if pos == -1:
                if initial:
                    raise ValueError(f"'{eng_word}' could not be found in '{eng_lit}' ({twi})!")
                break
            initial = False
            eng_word_color = f"<span style='color:{highlight_color}'>{eng_word}</span>"
            eng_lit_color = eng_lit_color[:pos] + eng_word_color + eng_lit_color[pos + len(eng_word):]
            eng_lit = eng_lit[:pos] + ">" * len(eng_word_color) + eng_lit[pos + len(eng_word):]
    # print("<br><br>", twi_color, "<br>", eng_lit_color)
    return twi_color, eng_lit_color


def format_translation(df, row_index: int, translation_language: str) -> str:
    """
    Generates the text for a single translation of a given word/phrase
    :param df: df
    :param row_index: row index of the translation in the df
    :param translation_language: language of the translation.
    :return: translation as html
    """
    translation = df.loc[row_index][translation_language]

    twi = df.loc[row_index]["twi"]
    english_literal = df.loc[row_index]["english_literal"]
    word_match = df.loc[row_index]["word_match"]

    if word_match:
        if not english_literal:
            english_literal = df.loc[row_index]["english"]
        twi_color, eng_lit_color = color_literal_translation(twi, english_literal, word_match)
        translation += f"<br><br><i>lit.:</i> {eng_lit_color}<br>{twi_color}"
    elif english_literal:
        translation += f"<br><br><i>lit.:</i> {english_literal}"

    note = df.loc[row_index]["note"]
    if note:
        translation += f"<br><br><i style='color: lightslategray'>{note}</i>"

    examples = df.loc[row_index]["examples"]
    if examples:
        translation += f"<br><br><div style='color: lightslategray'><i><b>Examples:</b></i>"
        for example_id in examples:
            example_index = df.index[df["id"] == example_id]
            if len(example_index) > 0:
                example_index = example_index[0]
                translation += f"<br>{df.loc[example_index]['twi']} → {df.loc[example_index]['english']}"
        translation += "</div>"

    return translation


def create_flashcard(df, word: str, language: str, audio_dir: str):
    """
    generates an anki flashcard for a given word
    :param: df: df
    :param: word: the word to generate a flashcard for (front of the card)
    :param: language: the language of the word
    """
    languages = ["twi", "english"]
    translation_language = languages[languages.index(language) - 1]
    translation_loc = df.index[df[language] == word]
    formatted_translations = sorted([format_translation(df, loc, translation_language) for loc in translation_loc])

    if len(formatted_translations) > 1:
        front = f"{word} ({len(formatted_translations)})"
        back = ""
        for i, trans in enumerate(formatted_translations, 1):
            back += f"<b>{i})</b> {trans}<br><br>"
    else:
        front = f"{word}"
        back = formatted_translations[0]

    tags = [f"{language}", df.loc[translation_loc]["type"].values[0]]

    audio_file_name = f"{sanitized_filename(word)}.mp3"
    if os.path.isfile(os.path.join(audio_dir, audio_file_name)):
        audio = f"[sound:{audio_file_name}]"
    else:
        audio = ""

    card = LanguageNote(
        model=LANGUAGE_MODEL,
        fields=[word, front, back, audio],
        tags=tags
    )
    return card


def create_flashcards(df: pd.DataFrame, out_path, audio_dir):
    def sort_key_func(row):
        return count_word_occurrences(row["twi"], df, "twi") + 1 - len(row["twi"]) / 100

    df['sort_key'] = df.apply(sort_key_func, axis=1)
    df.sort_values(by='sort_key', ascending=False, inplace=True)

    anki_deck = genanki.Deck(1550882594, "Twi")
    cards_count = 0
    words_eng = []
    for language in ["twi", "english"]:
        for word in df[language].unique():
            if language == "english" and word in words_eng:
                continue
            card = create_flashcard(df, word, language, audio_dir)
            anki_deck.add_note(card)
            cards_count += 1
            if language == "twi":
                eng_translations = df[df["twi"] == word]["english"].tolist()
                for eng_translation in eng_translations:
                    if eng_translation in words_eng:
                        continue
                    card = create_flashcard(df, eng_translation, "english", audio_dir)
                    anki_deck.add_note(card)
                    cards_count += 1
                    words_eng.append(eng_translation)
    anki_package = genanki.Package(anki_deck)
    anki_package.media_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir)]

    anki_package.write_to_file(out_path)
    return cards_count


if __name__ == '__main__':
    df = pd.read_pickle("../files/twi_vocabulary_df_latest.pkl")
    count = create_flashcards(df, "../files/public/flashcards.apkg", "../files/public/audio")
    print(f"Created {count} flashcards!")
