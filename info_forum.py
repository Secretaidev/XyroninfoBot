from config import bot
from buttons import ibtn, InlineKeyboardMarkup
from utils import esc, get_wm, fmt_num
from database import increment_lookup


def extract_forum_info(target, chat_id):
    try:
        chat = bot.get_chat(target)
    except Exception:
        m = InlineKeyboardMarkup()
        m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))
        return "❌ <b>Forum not found!</b>\n\nBot must be a member of the forum.", m

    fid = chat.id
    title = esc(chat.title or "N/A")
    un = f"@{chat.username}" if chat.username else "N/A"
    desc = esc(chat.description) if chat.description else "—"
    photo = "✅ Yes" if chat.photo else "❌ No"
    forum = "✅ Enabled" if getattr(chat, "is_forum", False) else "❌ Disabled"
    hidden = "✅ Yes" if getattr(chat, "has_hidden_members", False) else "❌ No"
    protected = "✅ Yes" if getattr(chat, "has_protected_content", False) else "❌ No"
    antispam = "✅ Yes" if getattr(chat, "has_aggressive_anti_spam_enabled", False) else "❌ No"

    members = "🔒 Unknown"
    try:
        members = fmt_num(bot.get_chat_member_count(chat.id))
    except Exception:
        pass

    linked = f"<code>{chat.linked_chat_id}</code>" if getattr(chat, "linked_chat_id", None) else "—"
    share = f"tg://msg_url?url=https://t.me/{chat.username}" if chat.username else f"tg://msg_url?url=forum_{fid}"

    text = (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"《 💬 FORUM INFORMATION 》\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 <b>Forum ID:</b> <code>{fid}</code>\n"
        f"📛 <b>Title:</b> {title}\n"
        f"🔗 <b>Username:</b> {un}\n"
        f"💬 <b>Type:</b> Forum Supergroup\n\n"
        f"🗂 <b>Forum Topics:</b> {forum}\n"
        f"👥 <b>Members:</b> {members}\n"
        f"🖼 <b>Has Photo:</b> {photo}\n"
        f"👻 <b>Hidden Members:</b> {hidden}\n"
        f"🔒 <b>Protected Content:</b> {protected}\n"
        f"🛡 <b>Anti-Spam:</b> {antispam}\n"
        f"🔗 <b>Linked Channel:</b> {linked}\n\n"
        f"📝 <b>Description:</b>\n{desc}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <i>Powered by {esc(get_wm())}</i>"
    )

    m = InlineKeyboardMarkup()
    m.row(
        ibtn("📋 Copy ID", copy_text=str(fid), style="primary"),
        ibtn("🚀 Share", url=share, style="success"),
    )
    if chat.username:
        m.row(ibtn("💬 Open Forum", url=f"https://t.me/{chat.username}", style="primary"))
    m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))

    increment_lookup(chat_id)
    return text, m
