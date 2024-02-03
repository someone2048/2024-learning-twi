import genanki
import pandas as pd
from src.read_db_notion import fetch_notion_db, NOTION_DB, NOTION_TOKEN
from utils import parse_word_match


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
    # random.shuffle(highlight_colors)

    replacements = parse_word_match(word_match)
    replacements = [(*r, highlight_colors[i % len(highlight_colors)]) for i, r in enumerate(replacements)]

    # parsing twi
    twi_color = ""
    for twi_word, eng_word, highlight_color in replacements:
        word_start = twi.lower().find(twi_word.lower())
        if word_start == -1:
            print(f"WARNING: '{twi_word}' could not be found in '{twi}'!")
            continue
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
                    print(f"WARNING: '{eng_word}' could not be found in '{eng_lit}' ({twi})!")
                break
            initial = False
            eng_word_color = f"<span style='color:{highlight_color}'>{eng_word}</span>"
            eng_lit_color = eng_lit_color[:pos] + eng_word_color + eng_lit_color[pos + len(eng_word):]
            eng_lit = eng_lit[:pos] + ">" * len(eng_word_color) + eng_lit[pos + len(eng_word):]
    # print("<br><br>", twi_color, "<br>", eng_lit_color)
    return twi_color, eng_lit_color


def create_flashcard(df, word: str, language: str):
    languages = ["twi", "english"]
    translation_language = languages[languages.index(language) - 1]
    translation_loc = df.index[df[language] == word]
    formatted_translations = [format_translation(df, loc, translation_language) for loc in translation_loc]

    front = f"{word}"
    if len(formatted_translations) > 1:
        back = ""
        for i, trans in enumerate(formatted_translations, 1):
            back += f"<b>{i})</b> {trans}<br><br>"
    else:
        back = formatted_translations[0]

    tags = [f"{language}", df.iloc[translation_loc]["type"].values[0]]

    return front, back, tags


def format_translation(df, row_index: int, translation_language: str):
    translation = df.iloc[row_index][translation_language]

    twi = df.iloc[row_index]["twi"]
    english_literal = df.iloc[row_index]["english_literal"]

    if english_literal:
        word_match = df.iloc[row_index]["word_match"]
        if word_match:
            twi_color, eng_lit_color = color_literal_translation(twi, english_literal, word_match)
            translation += f"<br><br><i>lit.:</i> {eng_lit_color}<br>{twi_color}"
        else:
            translation += f"<br><br><i>lit.:</i> {english_literal}"

    note = df.iloc[row_index]["note"]
    if note:
        translation += f"<br><br><i style='color: lightslategray'>{note}</i>"

    examples = df.iloc[row_index]["examples"]
    if examples:
        translation += f"<br><br><i><b>Examples:</b></i>"
        for example_id in examples:
            example_index = df.index[df["id"] == example_id][0]
            translation += f"<br>{df.iloc[example_index]['twi']} → {df.iloc[example_index]['english']}"

    return translation


class LanguageNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


def create_flashcards(df: pd.DataFrame, out_path):
    anki_deck = genanki.Deck(11264, "Twi")
    cards_count = 0
    for language in ["twi", "english"]:
        for word in df[language].unique():
            front, back, tags = create_flashcard(df, word, language)
            twi_english = LanguageNote(
                model=genanki.builtin_models.BASIC_MODEL,
                fields=[front, back],
                tags=tags
            )
            anki_deck.add_note(twi_english)
            cards_count += 1
            # print(f"<h3>{front}</h3><p>{back}</p>")
    anki_deck.write_to_file(out_path)
    return cards_count


if __name__ == '__main__':
    df = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    create_flashcards(df, "flashcards_test.apkg")
