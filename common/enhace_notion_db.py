from anki_flashcards.create_fashcards import color_literal_translation
from common.read_db_notion import *

from common.utils import parse_word_match


def recommend_examples(df: pd.DataFrame):
    for _, row in df.iterrows():
        if not row["type"] == "word":
            continue

        for i, row2 in df[df["type"] == "expression"].iterrows():
            if row2["id"] in row["examples"]:
                continue

            word_matches = parse_word_match(row2["word_match"])
            for twi, eng in word_matches:
                if twi.lower() == row["twi"].lower().strip():
                    # we don't care about literal translations here
                    if row["english"].lower().strip() in row2["english"].lower():
                        print(f"{row['twi']}({row['english']}) -> {row2['twi']} MATCH: TWI+ENG")
                    else:
                        print(f"{row['twi']}({row['english']}) -> {row2['twi']} MATCH: TWI (only)")


def verify_database(df: pd.DataFrame) -> dict[int, str]:
    log = {}
    for i, row in df.iterrows():
        if not row["type"] or not row["twi"] or not row["english"]:
            log[i] = f"MISSING KEY FIELD: \"{row['twi']}\" -> \"{row['english']}\""
        try:
            color_literal_translation(row["twi"], row["english_literal"], row["word_match"])
        except Exception:
            log[i] = f"WORD MATCH PARSING FAILURE: \"{row['twi']}\" -> \"{row['english']}\""
    return log
