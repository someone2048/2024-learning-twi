import os.path
from tkinter import filedialog

import pandas as pd
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from common.utils import sanitized_filename, preprocess_twi


def word_prompt(df_path) -> tuple[str | None, bool]:
    def simplify_words(words):
        simpler_words = [sanitized_filename(w) for w in words]
        simpler_words = [w.replace("ɛ", "3") for w in simpler_words]
        simpler_words = [w.replace("ɔ", ")") for w in simpler_words]
        simpler_words = [w.replace("_", " ") for w in simpler_words]
        return simpler_words

    # Define a list of words for tab completion
    df = pd.read_pickle(df_path)
    unique_words = list(df['twi'].unique())
    simplified_words = simplify_words(unique_words)

    # Prompt the user for input with tab completion
    word_completer = WordCompleter(simplified_words)
    user_input = prompt('>', completer=word_completer, search_ignore_case=True)
    if user_input in simplified_words:
        return unique_words[simplified_words.index(user_input)], True
    else:
        user_input = user_input.replace("3", "ɛ").replace(")", "ɔ")
        return user_input, False


def main(start_time=0):
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    full_video = VideoFileClip(video_path)
    full_audio = AudioSegment.from_file(video_path)

    non_silent_section_times = detect_nonsilent(full_audio, min_silence_len=1000,
                                           silence_thresh=-50, seek_step=100)
    for start, stop in non_silent_section_times:
        if start/1000 < start_time:
            continue
        video_section = full_video.subclip(start/1000, stop/1000)
        video_section.preview()
        twi_word, is_in_vocab = word_prompt("../files/twi_vocabulary_df_latest.pkl")
        if twi_word:
            file_name = sanitized_filename(twi_word) + f"{'_UNUSED' if not is_in_vocab else ''}" + ".mp3"
            full_audio[start:stop].export(os.path.join("../files/public/audio/", file_name), format="mp3")
            print(f"{file_name} ({start/1000}-{stop/1000})")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
