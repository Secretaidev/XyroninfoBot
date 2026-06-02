import threading, os, time
from config import bot
import buttons
import handlers
from server import app
from telebot.types import BotCommand


def _poll():
    time.sleep(2)
    while True:
        try:
            bot.infinity_polling(
                allowed_updates=['message', 'callback_query'],
                timeout=30,
                long_polling_timeout=25,
            )
        except Exception as e:
            print(f'⚠️ Polling error: {e}')
            time.sleep(5)


if __name__ == '__main__':
    try:
        bot.remove_webhook()
    except Exception:
        pass

    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

    try:
        bot.set_my_commands([
            BotCommand('/start', '🔱 Start the bot'),
            BotCommand('/help', '📖 Help & Commands'),
            BotCommand('/id', '🆔 Get your Telegram ID'),
            BotCommand('/ping', '🏓 Check bot speed'),
            BotCommand('/about', '🔱 About this bot'),
            BotCommand('/json', '📄 Export info as JSON'),
        ])
    except Exception:
        pass

    t = threading.Thread(target=_poll, daemon=True)
    t.start()
    print('🔱 Xyron Info Bot is running!')

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
