from read_db_notion import *

from utils import parse_word_match


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


def check_for_malformed_entries(df: pd.DataFrame):
    for i, row in df.iterrows():

        if not row["type"] or not row["twi"] or not row["english"]:
            print(f"MISSING KEY FIELD: {i}) {row['twi']}->{row['english']}")

        try:
            parse_word_match(row["word_match"])
        except Exception:
            print(f"WORD MATCH PARSING FAILURE: {i}) {row['twi']}->{row['english']}")


if __name__ == '__main__':
    df = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    check_for_malformed_entries(df)
    recommend_examples(df)
