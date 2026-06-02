import os
from telebot import TeleBot

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

bot = TeleBot(BOT_TOKEN, parse_mode="HTML", num_threads=50)
