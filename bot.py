import threading, os, time, traceback
from config import bot
import buttons
import handlers
from server import app
from telebot.types import BotCommand


def _poll():
    time.sleep(3)
    print('🔄 Starting polling thread...')
    try:
        me = bot.get_me()
        print(f'✅ Bot connected: @{me.username} (ID: {me.id})')
    except Exception as e:
        print(f'❌ Bot connection failed: {e}')
        return

    while True:
        try:
            print('🔄 Polling started...')
            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=25,
            )
        except Exception as e:
            print(f'⚠️ Polling error: {e}')
            traceback.print_exc()
            time.sleep(5)


if __name__ == '__main__':
    print('🔱 Initializing...')

    try:
        bot.remove_webhook()
        print('✅ Webhook removed')
    except Exception as e:
        print(f'⚠️ Webhook remove: {e}')

    try:
        bot.delete_webhook(drop_pending_updates=True)
        print('✅ Webhook deleted')
    except Exception as e:
        print(f'⚠️ Webhook delete: {e}')

    try:
        bot.set_my_commands([
            BotCommand('/start', '🔱 Start the bot'),
            BotCommand('/help', '📖 Help & Commands'),
            BotCommand('/id', '🆔 Get your Telegram ID'),
            BotCommand('/ping', '🏓 Check bot speed'),
            BotCommand('/about', '🔱 About this bot'),
            BotCommand('/json', '📄 Export info as JSON'),
        ])
        print('✅ Commands set')
    except Exception as e:
        print(f'⚠️ Commands: {e}')

    t = threading.Thread(target=_poll, daemon=True)
    t.start()
    print('🔱 Xyron Info Bot is running!')

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
