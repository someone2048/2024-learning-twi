def parse_word_match(word_match):
    word_match = word_match.replace(";", "\n")
    word_match = word_match.split("\n")

    replacements = []
    for line in word_match:
        if not line:
            continue
        twi_word, eng_word = line.split(">")
        twi_word = twi_word.strip()
        eng_word = eng_word.strip()

        replacements.append((twi_word, eng_word))
    return replacements


def preprocess_twi(database: list[list[str]]):
    header = database[0]
    twi_column = header.index("twi")
    word_match_column = header.index("word_match")

    for row in database:
        for col in [twi_column, word_match_column]:
            row[col] = row[col].replace(")", "ɔ")
            row[col] = row[col].replace("3", "ɛ")
    return database


def sanitized_filename(word: str) -> str:
    word = word.lower().strip()
    word = word.replace(" ", "_")
    word = "".join([c for c in word if c in "abcdeɛfghijklmnoɔpqrstuvwxyz0123456789_"])
    return word
