import genanki
from read_db_csv import read_db_csv
from utils import parse_word_match, preprocess_twi


def colorcode_literal_translation(twi, eng_lit, word_match):
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
        word_start = twi.find(twi_word)
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
            pos = eng_lit.find(eng_word)
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


def create_explanation_str(header, row):
    twi_column = header.index("twi")
    eng_lit_column = header.index("english_literal")
    note_column = header.index("note")
    word_match_column = header.index("word_match")
    # examples_column = header.index("examples")

    explanation = ""
    if row[eng_lit_column]:
        lit_breakdown = row[eng_lit_column]
        if row[word_match_column]:
            twi_color, eng_lit_color = colorcode_literal_translation(row[twi_column],
                                                                     row[eng_lit_column],
                                                                     row[word_match_column])
            lit_breakdown = f"{eng_lit_color}<br>{twi_color}"

        explanation += f"<br><br><i>lit.:</i> {lit_breakdown}"
    if row[note_column]:
        explanation += f"<br><br><i style='color: lightslategray'>{row[note_column]}</i>"
    # if row[example_column]:
    #     explanation += f"<br><br><span style='color: lightslategray'>Examples</span><br>"
    #     for example_id in row[example_column]:
    #        example_row =
    #        explanation += f"<i>{}</i>"

    return explanation


def create_flashcards(database: list[list[str]], out_path):
    twi_column = database[0].index("twi")
    eng_column = database[0].index("english")

    anki_deck = genanki.Deck(11264, "Twi")

    count = 0
    for row in database[1:]:
        explanation = create_explanation_str(database[0], row)

        # twi -> english
        twi_english = genanki.Note(
            model=genanki.builtin_models.BASIC_MODEL,
            fields=[row[twi_column], row[eng_column] + explanation])
        anki_deck.add_note(twi_english)

        # english -> twi
        english_twi = genanki.Note(
            model=genanki.builtin_models.BASIC_MODEL,
            fields=[row[eng_column], row[twi_column] + explanation]
        )
        anki_deck.add_note(english_twi)
        count += 1
    print(f"Added {count} items, {count*2} nodes")
    anki_deck.write_to_file(out_path)


if __name__ == '__main__':
    db = read_db_csv("../twi_test.csv")
    db = preprocess_twi(db)
    create_flashcards(db, "../flashcards.apkg")



