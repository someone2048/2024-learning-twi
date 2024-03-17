import json
import os.path
import click
import pandas as pd
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from common.utils import sanitized_filename
from common.read_db_notion import fetch_notion_db

FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../files/"))
assert os.path.isdir(FILES_DIR)


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


@click.command()
@click.argument('video_path')
@click.option('-s', '--start_time', default=0, help='Start time in milliseconds')
@click.option('--min_silence_len', default=1000, help='Minimum silence length in seconds')
@click.option('--silence_thresh', default=-50, help='Silence threshold in dB')
def main(video_path, start_time=0, min_silence_len=1000, silence_thresh=-50):
    """
    Sequentially shows a video as short clips delimited by silence and allows export of a given clips audio.

    Args:
        video_path (str): Path to the video file.
        start_time (int, optional): Start time in seconds. Defaults to 0.
        min_silence_len (int, optional): Minimum silence length in milliseconds. Defaults to 1000.
        silence_thresh (int, optional): Silence threshold in dB. Defaults to -50.
    """

    # fetching df
    with open(os.path.join(FILES_DIR, "secrets/notion_secrets.json")) as f:
        j = json.load(f)
        notion_token = j["notion_token"]
        notion_db = j["notion_db"]
    df = fetch_notion_db(notion_db, notion_token)
    df.to_pickle(os.path.join(FILES_DIR, f"twi_vocabulary_df_latest.pkl"))

    full_video = VideoFileClip(video_path)
    full_audio = AudioSegment.from_file(video_path)

    non_silent_section_times = detect_nonsilent(full_audio, min_silence_len, silence_thresh, 100)
    for start, stop in non_silent_section_times:
        if start/1000 < start_time:
            continue
        video_section = full_video.subclip(start/1000, stop/1000)
        video_section.preview()
        twi_word, is_in_vocab = word_prompt(os.path.join(FILES_DIR, "twi_vocabulary_df_latest.pkl"))
        if twi_word:
            file_name = sanitized_filename(twi_word) + ".mp3"
            full_audio[start:stop].export(os.path.join(FILES_DIR, "public/audio/", file_name), format="mp3")
            print(f"{file_name} ({start/1000}-{stop/1000})")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
