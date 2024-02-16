import io
import logging
import random

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


from rsTwiAudioBot.managers import AudioManager, UserContextManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

AUDIO_MANAGER = AudioManager("word_list.txt", "./audio")
USER_MANAGER = UserContextManager()


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=
    "Welcome to the Twi audio telegram bot!\n\n"
    "Please respond to each twi word or phrase I send, with a voice message of you speaking it. "
    "If you send several voice messages, the last one will be used. \n"
    "Once you are happy with your pronounciation you can type the command /save to confirm it and have me send you the next word. \n"
    "If you don't want me to save the recording you can use the command /skip to advance to the next word.")


async def command_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"{update.effective_chat.id} /save")

    word = USER_MANAGER.get_word(update.effective_chat.id)
    audio = USER_MANAGER.get_audio(update.effective_chat.id)
    if audio:
        r = requests.get(audio)
        if r.ok:
            audio = io.BytesIO(r.content)
        else:
            audio = None

    if word and audio:
        AUDIO_MANAGER.add_audio_from_file(word, audio)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"saved \"{word}\" successfully!")
        await action_send_word(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Sorry, there is nothing to save yet... please send an audio message first!")
        if not word:
            await action_send_word(update, context)


async def command_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"{update.effective_chat.id} /skip")
    await action_send_word(update, context)


async def handler_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_link = (await update.message.effective_attachment.get_file()).file_path
    USER_MANAGER.set_audio(update.effective_chat.id, file_link)
    logging.info(f"{update.effective_chat.id} [voice message received]")


async def action_send_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(list(AUDIO_MANAGER.words_no_audio))
    USER_MANAGER.set_word(update.effective_chat.id, word)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=word)


if __name__ == '__main__':
    application = ApplicationBuilder().token('6703057904:AAH4HYWWkkaOQKnuZyjRXKp_-V9GCRNkrTk').build()

    start_handler = CommandHandler('start', command_start)
    application.add_handler(start_handler)

    start_handler = CommandHandler('skip', command_skip)
    application.add_handler(start_handler)

    start_handler = CommandHandler('save', command_save)
    application.add_handler(start_handler)

    voice_handler = MessageHandler(filters.VOICE, handler_voice_message)
    application.add_handler(voice_handler)

    application.run_polling()
