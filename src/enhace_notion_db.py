from read_db_notion import *
from copy import deepcopy

from utils import parse_word_match

# TODO NEEDS REFACTOR TO DataFrame


def recommend_examples(database):
    header = database[0]
    id_column = header.index("id")
    twi_column = header.index("twi")
    eng_column = header.index("english")
    examples_column = header.index("examples")
    word_match_column = header.index("word_match")
    type_column = header.index("type")
    for row in database[1:]:
        if not row[type_column] == "word":
            continue

        for row2 in database[1:]:
            if not row2[type_column] == "expression":
                continue
            if row2[id_column] in row[examples_column]:
                continue

            word_matches = parse_word_match(row2[word_match_column])
            for twi, eng in word_matches:
                if twi.lower() == row[twi_column].lower().strip():
                    if eng.lower() == row[eng_column].lower().strip():
                        print(f"{row[twi_column]} -> {row2[twi_column]} MATCH: TWI+ENG")
                    else:
                        print(f"{row[twi_column]} -> {row2[twi_column]} MATCH: TWI (only)")


def auto_update_notion_twi_vocab_db(db_url, access_token):
    data_old = fetch_notion_db(db_url, access_token)
    data = deepcopy(data_old)
    data = preprocess_twi(data)
    recommend_examples(data)


if __name__ == '__main__':
    data_old = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    data = deepcopy(data_old)
    data = preprocess_twi(data)
    recommend_examples(data)