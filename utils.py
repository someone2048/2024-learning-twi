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