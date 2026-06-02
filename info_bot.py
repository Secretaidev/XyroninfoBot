from config import bot
from buttons import ibtn, InlineKeyboardMarkup
from utils import esc, get_wm
from database import increment_lookup


def extract_bot_info(target, chat_id):
    try:
        chat = bot.get_chat(target)
    except Exception:
        m = InlineKeyboardMarkup()
        m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))
        return "❌ <b>Bot not found!</b>\n\nCheck the username.", m

    uid = chat.id
    name = esc(chat.first_name or "N/A")
    un = f"@{chat.username}" if chat.username else "N/A"
    bio = esc(chat.bio) if chat.bio else "—"
    desc = esc(chat.description) if chat.description else "—"
    join_groups = "✅ Yes" if getattr(chat, "can_join_groups", False) else "❌ No"
    read_all = "✅ Yes" if getattr(chat, "can_read_all_group_messages", False) else "❌ No"
    inline = "✅ Yes" if getattr(chat, "supports_inline_queries", False) else "❌ No"
    has_main_web = "✅ Yes" if getattr(chat, "has_main_web_app", False) else "❌ No"
    share = f"tg://msg_url?url=https://t.me/{chat.username}" if chat.username else f"tg://msg_url?url=bot_{uid}"

    photos = 0
    try:
        pp = bot.get_user_profile_photos(uid)
        photos = pp.total_count if pp else 0
    except Exception:
        pass

    text = (
        f"🤖 <b>Bot</b>\n\n"
        f"🆔 <b>Bot ID:</b> <code>{uid}</code>\n"
        f"📛 <b>Name:</b> {name}\n"
        f"🔗 <b>Username:</b> {un}\n\n"
        f"🖼 <b>Profile Photos:</b> {photos}\n"
        f"👥 <b>Join Groups:</b> {join_groups}\n"
        f"👁 <b>Read All Messages:</b> {read_all}\n"
        f"⚡ <b>Inline Mode:</b> {inline}\n"
        f"🌐 <b>Web App:</b> {has_main_web}\n\n"
        f"📝 <b>Bio:</b> {bio}\n"
        f"📋 <b>Description:</b>\n{desc}\n\n"
        f"⚡ <i>Powered by {esc(get_wm())}</i>"
    )

    m = InlineKeyboardMarkup()
    m.row(
        ibtn("📋 Copy ID", copy_text=str(uid), style="primary"),
        ibtn("🚀 Share", url=share, style="success"),
    )
    if chat.username:
        m.row(ibtn(f"🤖 Open Bot", url=f"https://t.me/{chat.username}", style="primary"))
    m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))

    increment_lookup(chat_id)
    return text, m
