import threading, os
from config import bot
import buttons
import handlers
from server import app
from telebot.types import BotCommand

def _server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    bot.set_my_commands([
        BotCommand('/start', '🔱 Start the bot'),
        BotCommand('/help', '📖 Help & Commands'),
        BotCommand('/id', '🆔 Get your Telegram ID'),
        BotCommand('/ping', '🏓 Check bot speed'),
        BotCommand('/about', '🔱 About this bot'),
        BotCommand('/json', '📄 Export info as JSON'),
    ])
    threading.Thread(target=_server, daemon=True).start()
    print('🔱 Xyron Info Bot is running!')
    bot.infinity_polling(allowed_updates=['message', 'callback_query'])
