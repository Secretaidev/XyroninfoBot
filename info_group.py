from config import bot
from buttons import ibtn, InlineKeyboardMarkup
from utils import esc, get_wm, fmt_num
from database import increment_lookup


def _perms(p):
    if not p:
        return "  🔒 Unavailable"
    items = [
        ("Send Messages", getattr(p, "can_send_messages", None)),
        ("Send Media", getattr(p, "can_send_media_messages", None)),
        ("Send Polls", getattr(p, "can_send_polls", None)),
        ("Send Stickers/GIFs", getattr(p, "can_send_other_messages", None)),
        ("Add Web Previews", getattr(p, "can_add_web_page_previews", None)),
        ("Change Info", getattr(p, "can_change_info", None)),
        ("Invite Users", getattr(p, "can_invite_users", None)),
        ("Pin Messages", getattr(p, "can_pin_messages", None)),
        ("Manage Topics", getattr(p, "can_manage_topics", None)),
    ]
    return "\n".join(f"  {'✅' if v else '❌'} {n}" for n, v in items)


def extract_group_info(target, chat_id):
    try:
        chat = bot.get_chat(target)
    except Exception:
        m = InlineKeyboardMarkup()
        m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))
        return "❌ <b>Group not found!</b>\n\nBot must be a member of the group.", m

    gid = chat.id
    title = esc(chat.title or "N/A")
    un = f"@{chat.username}" if chat.username else "N/A"
    desc = esc(chat.description) if chat.description else "—"
    photo = "✅ Yes" if chat.photo else "❌ No"
    gtype = "Supergroup" if chat.type == "supergroup" else "Group"
    members = "🔒 Unknown"
    try:
        members = fmt_num(bot.get_chat_member_count(chat.id))
    except Exception:
        pass

    linked = f"<code>{chat.linked_chat_id}</code>" if getattr(chat, "linked_chat_id", None) else "—"
    slow = f"{chat.slow_mode_delay}s" if getattr(chat, "slow_mode_delay", None) else "❌ Disabled"
    protected = "✅ Yes" if getattr(chat, "has_protected_content", False) else "❌ No"
    hidden = "✅ Yes" if getattr(chat, "has_hidden_members", False) else "❌ No"
    antispam = "✅ Yes" if getattr(chat, "has_aggressive_anti_spam_enabled", False) else "❌ No"
    perms = _perms(getattr(chat, "permissions", None))
    share = f"tg://msg_url?url=https://t.me/{chat.username}" if chat.username else f"tg://msg_url?url=grp_{gid}"

    text = (
        f"👥 <b>Group</b>\n\n"
        f"🆔 <b>Group ID:</b> <code>{gid}</code>\n"
        f"📛 <b>Title:</b> {title}\n"
        f"🔗 <b>Username:</b> {un}\n"
        f"👥 <b>Type:</b> {gtype}\n\n"
        f"👤 <b>Members:</b> {members}\n"
        f"🖼 <b>Has Photo:</b> {photo}\n"
        f"⏱ <b>Slow Mode:</b> {slow}\n"
        f"🔒 <b>Protected Content:</b> {protected}\n"
        f"👻 <b>Hidden Members:</b> {hidden}\n"
        f"🛡 <b>Anti-Spam:</b> {antispam}\n"
        f"🔗 <b>Linked Channel:</b> {linked}\n\n"
        f"📋 <b>Permissions:</b>\n{perms}\n\n"
        f"📝 <b>Description:</b>\n{desc}\n\n"
        f"⚡ <i>Powered by {esc(get_wm())}</i>"
    )

    m = InlineKeyboardMarkup()
    m.row(
        ibtn("📋 Copy ID", copy_text=str(gid), style="primary"),
        ibtn("🚀 Share", url=share, style="success"),
    )
    if chat.username:
        m.row(ibtn("👥 Open Group", url=f"https://t.me/{chat.username}", style="primary"))
    m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))

    increment_lookup(chat_id)
    return text, m
