from config import bot
from buttons import ibtn, InlineKeyboardMarkup
from utils import esc, get_wm, fmt_num
from database import increment_lookup


def extract_channel_info(target, chat_id):
    try:
        chat = bot.get_chat(target)
    except Exception:
        m = InlineKeyboardMarkup()
        m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))
        return "❌ <b>Channel not found!</b>\n\nBot must be a member of the channel.", m

    cid = chat.id
    title = esc(chat.title or "N/A")
    un = f"@{chat.username}" if chat.username else "N/A"
    desc = esc(chat.description) if chat.description else "—"
    photo = "✅ Yes" if chat.photo else "❌ No"
    has_protected = "✅ Yes" if getattr(chat, "has_protected_content", False) else "❌ No"
    sign_messages = "✅ Yes" if getattr(chat, "sign_messages", False) else "❌ No"

    members = "🔒 Unknown"
    try:
        members = fmt_num(bot.get_chat_member_count(chat.id))
    except Exception:
        pass

    linked = f"<code>{chat.linked_chat_id}</code>" if getattr(chat, "linked_chat_id", None) else "—"
    invite = f"<a href='{chat.invite_link}'>Join Link</a>" if getattr(chat, "invite_link", None) else "—"
    share = f"tg://msg_url?url=https://t.me/{chat.username}" if chat.username else f"tg://msg_url?url=channel_{cid}"

    text = (
        f"📢 <b>Channel</b>\n\n"
        f"🆔 <b>Channel ID:</b> <code>{cid}</code>\n"
        f"📛 <b>Title:</b> {title}\n"
        f"🔗 <b>Username:</b> {un}\n\n"
        f"👥 <b>Members:</b> {members}\n"
        f"🖼 <b>Has Photo:</b> {photo}\n"
        f"🔒 <b>Protected Content:</b> {has_protected}\n"
        f"✍️ <b>Sign Messages:</b> {sign_messages}\n"
        f"🔗 <b>Linked Chat:</b> {linked}\n"
        f"🔗 <b>Invite Link:</b> {invite}\n\n"
        f"📝 <b>Description:</b>\n{desc}\n\n"
        f"⚡ <i>Powered by {esc(get_wm())}</i>"
    )

    m = InlineKeyboardMarkup()
    m.row(
        ibtn("📋 Copy ID", copy_text=str(cid), style="primary"),
        ibtn("🚀 Share", url=share, style="success"),
    )
    if chat.username:
        m.row(ibtn("📢 Open Channel", url=f"https://t.me/{chat.username}", style="primary"))
    m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))

    increment_lookup(chat_id)
    return text, m
