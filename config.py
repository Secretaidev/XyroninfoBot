import os
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=50)
