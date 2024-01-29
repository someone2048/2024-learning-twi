from read_db_notion import *
from copy import deepcopy

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
                        print(f"{row['twi']} -> {row2['twi']} MATCH: TWI+ENG")
                    else:
                        print(f"{row['twi']} -> {row2['twi']} MATCH: TWI (only)")


def auto_update_notion_twi_vocab_db(db_url, access_token):
    data_old = fetch_notion_db(db_url, access_token)
    data = deepcopy(data_old)
    data = preprocess_twi(data)
    recommend_examples(data)


if __name__ == '__main__':
    df = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    recommend_examples(df)