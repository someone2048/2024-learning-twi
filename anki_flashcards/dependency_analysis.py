import pandas as pd

from common.utils import sanitized_filename


def pseudo_word_frequencies(df, column):
    """Assumes that everything delimited by a space ia a word"""
    words = []
    for word_str in df[column]:
        word_str = sanitized_filename(word_str)
        words += word_str.split("_")
    word_freq = []
    for word in set(words):
        word_freq.append((word, words.count(word)))
    word_freq.sort(key=lambda x: x[1], reverse=True)
    return word_freq


def drop_translated_words(df, word_column, word_freq):
    words_with_translation = [sanitized_filename(w) for w in df[word_column].unique()]
    word_freq = [w for w in word_freq if w[0] not in words_with_translation]
    return word_freq


def count_word_occurrences(word_str, df, word_column):
    simplified_words = sanitized_filename(word_str).split("_")
    filtered_df = df[df[word_column].apply(
        lambda x: all(substring in sanitized_filename(x) for substring in simplified_words))]
    return len(filtered_df)


def pprint_word_frequencies(word_freq, df, word_column):
    for word, count in word_freq:
        print(f"{word} ({count})")
        simplified_word = sanitized_filename(word)
        filtered_df = df[df[word_column].apply(
            lambda x: simplified_word in sanitized_filename(x))]
        for i, row in filtered_df.iterrows():
            print(f"  {row['twi']} --> {row['english']}")


if __name__ == '__main__':
    def main():
        df = pd.read_pickle("../files/twi_vocabulary_df_latest.pkl")
        twi_freq = pseudo_word_frequencies(df, 'twi')
        print(len(twi_freq))
        print(twi_freq)
        twi_freq = drop_translated_words(df, "twi", twi_freq)
        print(twi_freq)
        print(len(twi_freq))

        print("\n" + "-"*50 + "\n")

        eng_freq = pseudo_word_frequencies(df, 'english')
        print(eng_freq)
        eng_freq = drop_translated_words(df, "english", eng_freq)
        print(eng_freq)

        pprint_word_frequencies(twi_freq, df, "twi")

    main()
