import os.path
import pandas as pd

from common.utils import sanitized_filename

if __name__ == '__main__':

    df = pd.read_pickle("../files/twi_vocabulary_df_latest.pkl")
    unique_words = list(df['twi'].unique())
    unique_filenames = [sanitized_filename(w) + ".mp3" for w in unique_words]
    unique_filenames_unused = [sanitized_filename(w) + "_UNUSED.mp3"for w in unique_words]

    audio_dir = "../files/public/audio/"
    for file in os.listdir(audio_dir):

        new = None
        if file in unique_filenames_unused:
            new = unique_filenames[unique_filenames_unused.index(file)]
        if not file.endswith("_UNUSED.mp3") and file not in unique_filenames:
            new = file[:-4] + "_UNUSED.mp3"

        if new is not None:
            print(f"{file} -> {new}")
            assert not os.path.exists(os.path.join(audio_dir, new))
            os.rename(os.path.join(audio_dir, file), os.path.join(audio_dir, new))
