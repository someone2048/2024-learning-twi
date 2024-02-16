import os
import io
from pydub import AudioSegment


class AudioManager:

    @staticmethod
    def sanitize(word: str) -> str:
        word = word.lower()
        word = word.replace(" ", "_")
        word = "".join([c for c in word if c in "abcdeɛfghijklmnoɔpqrstuvwxyz0123456789"])
        return word

    def __init__(self, wordlist_path, audio_dir):
        self.audio_dir = audio_dir
        assert os.path.isdir(audio_dir)

        with open(wordlist_path, 'r') as f:
            words = f.readlines()
            words = [w.strip() for w in words if w.strip()]

            # checking for collisions
            sanitized_words = set()
            for word in words:
                sanitized_word = self.sanitize(word)
                if sanitized_word in sanitized_words:
                    raise ValueError(f"Name collision when sanitizing word '{word}'")
                sanitized_words.add(word)

        audio_files = os.listdir(audio_dir)
        audio_files = [os.path.splitext(af)[0] for af in audio_files]

        self.words_no_audio = set()
        for word in words:
            if self.sanitize(word) not in audio_files:
                self.words_no_audio.add(word)

    def add_audio_from_file(self, word: str, audio_file: str | io.BytesIO, strip_silence=True):
        assert word in self.words_no_audio
        audio = AudioSegment.from_file(audio_file)

        if strip_silence:
            audio.export(os.path.join(self.audio_dir, self.sanitize(word) + ".raw.mp3"),
                             format="mp3", tags={"title": word})
            audio = audio.strip_silence(silence_thresh=-40, padding=100)

        audio.export(os.path.join(self.audio_dir, self.sanitize(word)+".mp3"),
                         format="mp3", tags={"title": word})
        self.words_no_audio.remove(word)


class UserContextManager:
    def __init__(self):
        self.__users_contexts = {}

    def __create_if_not_exists(self, uid):
        if uid not in self.__users_contexts:
            self.__users_contexts[uid] = {
                "current_word": None,
                "current_audio": None
            }

    def set_word(self, uid, word):
        self.__create_if_not_exists(uid)
        self.__users_contexts[uid]["current_word"] = word
        self.__users_contexts[uid]["current_audio"] = None

    def set_audio(self, uid, audio):
        self.__create_if_not_exists(uid)
        self.__users_contexts[uid]["current_audio"] = audio

    def get_audio(self, uid):
        self.__create_if_not_exists(uid)
        return self.__users_contexts[uid]["current_audio"]

    def get_word(self, uid):
        self.__create_if_not_exists(uid)
        return self.__users_contexts[uid]["current_word"]










