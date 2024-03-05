import os
import io
import random

import pandas as pd
from pydub import AudioSegment

from common.utils import sanitized_filename


class AudioManager:

    def __init__(self, df_path, audio_dir):
        self.df_path = df_path
        self.audio_dir = audio_dir
        assert os.path.isdir(audio_dir)
        assert os.path.isfile(df_path)

    def __load_words(self):
        df = pd.read_pickle(self.df_path)
        unique_words = list(df['twi'].unique())

        # checking against file name collisions
        unique_filenames = {sanitized_filename(w) for w in unique_words}
        assert len(unique_filenames) == len(unique_words)

        audio_files = os.listdir(self.audio_dir)
        audio_files = {os.path.splitext(af)[0] for af in audio_files}

        words_no_audio = [word for word in unique_words if sanitized_filename(word) not in audio_files]
        return words_no_audio

    def get_word(self):
        words_no_audio = self.__load_words()
        if len(words_no_audio) > 0:
            return random.choice(words_no_audio)
        return None

    def add_audio_from_file(self, word: str, audio_file: str | io.BytesIO):
        audio = AudioSegment.from_file(audio_file)
        audio.export(os.path.join(self.audio_dir, sanitized_filename(word)+".mp3"), format="mp3", tags={"title": word})


class UserContextManager:
    def __init__(self):
        self.__users_contexts = {}

    def __create_if_not_exists(self, uid):
        if uid not in self.__users_contexts:
            self.__users_contexts[uid] = {
                "current_word": None,
                "current_audio": None
            }

    def authenticate(self, uid):
        self.__create_if_not_exists(uid)

    def is_authenticated(self, uid):
        return uid in self.__users_contexts

    def set_word(self, uid, word):
        self.__users_contexts[uid]["current_word"] = word
        self.__users_contexts[uid]["current_audio"] = None

    def set_audio(self, uid, audio):
        self.__users_contexts[uid]["current_audio"] = audio

    def get_audio(self, uid):
        return self.__users_contexts[uid]["current_audio"]

    def get_word(self, uid):
        return self.__users_contexts[uid]["current_word"]


if __name__ == '__main__':
    AudioManager("../files/twi_vocabulary_df_latest.pkl", "../files/public/audio")






