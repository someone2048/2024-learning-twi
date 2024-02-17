import functools
import io
import json

import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from rsTwiAudioBot.managers import AudioManager, UserContextManager

AUDIO_MANAGER = AudioManager("files/twi_vocabulary_df_latest.pkl", "files/public/audio")
USER_MANAGER = UserContextManager()

with open("files/secrets/telegram_secrets.json", "r") as f:
    secrets = json.load(f)
    BOT_TOKEN = secrets["token"]
    AUTH_PASSWORD = secrets["password"]


def privileged(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not USER_MANAGER.is_authenticated(update.effective_chat.id):
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"please authenticate first using the /auth command!")
            return None
        result = await func(update, context)
        return result

    return wrapper


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=
    "Welcome to the Twi audio telegram bot!\n\n"
    "Please respond to each twi word or phrase I send, with a voice message of you speaking it. "
    "If you send several voice messages, the last one will be used. \n"
    "Once you are happy with your pronounciation you can type the command /save to confirm it and have me send you "
    "the next word. \n"
    "If you don't want me to save the recording you can use the command /skip to advance to the next word. \n\n"
    "Before we begin please authenticate with the \"/auth TypePasswordHere\" command!")


async def command_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not len(context.args) == 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="USAGE: /auth TypePasswordHere")
        return

    password = context.args[0]
    if password == AUTH_PASSWORD:
        USER_MANAGER.authenticate(update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="authentication successful!")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Let's start with the following word:")
        await action_send_word(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="password incorrect!")


@privileged
async def command_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


@privileged
async def command_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await action_send_word(update, context)


@privileged
async def handler_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_link = (await update.message.effective_attachment.get_file()).file_path
    USER_MANAGER.set_audio(update.effective_chat.id, file_link)


@privileged
async def action_send_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = AUDIO_MANAGER.get_word()
    if word is None:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"There are currently no words or phrases that don't have an audio recording...",
                                       parse_mode=ParseMode.MARKDOWN)
    USER_MANAGER.set_word(update.effective_chat.id, word)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*{word}*", parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', command_start))
    application.add_handler(CommandHandler('auth', command_auth))
    application.add_handler(CommandHandler('skip', command_skip))
    application.add_handler(CommandHandler('save', command_save))

    application.add_handler(MessageHandler(filters.VOICE, handler_voice_message))

    application.run_polling()
