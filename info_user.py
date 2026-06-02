from config import bot
from buttons import ibtn, InlineKeyboardMarkup
from utils import esc, plink, get_dc, get_wm, lang_name, fmt_num
from registration import get_registration_text, get_telegram_era, get_full_registration_info
from database import increment_lookup


def extract_user_info(target, chat_id):
    try:
        chat = bot.get_chat(target)
    except Exception:
        m = InlineKeyboardMarkup()
        m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))
        return "❌ <b>User not found!</b>\n\nThe user doesn't exist or is inaccessible.", m

    uid = chat.id
    fn = esc(chat.first_name or "N/A")
    ln = esc(chat.last_name) if chat.last_name else "N/A"
    un = f"@{chat.username}" if chat.username else "N/A"
    bio = esc(chat.bio) if chat.bio else "N/A"
    is_premium = getattr(chat, "is_premium", False) or False
    is_bot_flag = getattr(chat, "is_bot", False) or False
    is_verified = getattr(chat, "is_verified", False) or False
    is_scam = getattr(chat, "is_scam", False) or False
    is_fake = getattr(chat, "is_fake", False) or False
    lang = lang_name(getattr(chat, "language_code", None))
    emoji_status = getattr(chat, "emoji_status_custom_emoji_id", None)

    photos = 0
    dc_id, dc_name = None, "Unknown"
    try:
        pp = bot.get_user_profile_photos(uid)
        photos = pp.total_count if pp else 0
        if pp and pp.photos:
            dc_id, dc_name = get_dc(pp.photos[0][-1].file_id)
    except Exception:
        pass

    dc_line = f"DC{dc_id} — {dc_name}" if dc_id else "🔒 Hidden (No Photo)"
    reg = get_registration_text(uid)
    era = get_telegram_era(uid)
    ri = get_full_registration_info(uid)
    link = plink(uid, fn)
    share = f"tg://msg_url?url=https://t.me/{chat.username}" if chat.username else f"tg://msg_url?url=tg://user?id={uid}"

    premium_txt = "✅ Yes" if is_premium else "❌ No"
    bot_txt = "✅ Yes" if is_bot_flag else "❌ No"

    badges = " ".join(filter(None, [
        "✅ Verified" if is_verified else "",
        "⚠️ SCAM" if is_scam else "",
        "⚠️ FAKE" if is_fake else "",
    ]))
    badge_line = f"🏷 <b>Badges:</b> {badges}\n" if badges else ""
    emoji_line = f"🎭 <b>Emoji Status:</b> <code>{emoji_status}</code>\n" if emoji_status else ""

    text = (
        f"👤 <b>User</b>\n\n"
        f"🆔 <b>ID:</b> <code>{uid}</code>\n"
        f"👤 <b>First Name:</b> {fn}\n"
        f"👥 <b>Last Name:</b> {ln}\n"
        f"🔗 <b>Username:</b> {un}\n"
        f"🌍 <b>Language:</b> {lang}\n\n"
        f"🌐 <b>Data Center:</b> {dc_line}\n"
        f"🖼 <b>Profile Photos:</b> {photos}\n"
        f"⭐ <b>Premium:</b> {premium_txt}\n"
        f"🤖 <b>Is Bot:</b> {bot_txt}\n"
        f"{badge_line}{emoji_line}\n"
        f"📅 <b>Registered:</b> ~{reg}\n"
        f"🗓 <b>Era:</b> {era}\n"
        f"⏳ <b>Account Age:</b> {ri['formatted']}\n\n"
        f"🔗 <b>Link:</b> {link}\n"
        f"📝 <b>Bio:</b> {bio}\n\n"
        f"⚡ <i>Powered by {esc(get_wm())}</i>"
    )

    m = InlineKeyboardMarkup()
    m.row(
        ibtn("📋 Copy ID", copy_text=str(uid), style="primary"),
        ibtn("🚀 Share ID", url=share, style="success"),
    )
    m.row(ibtn("📅 Registration Details", callback_data=f"reg_detail_{uid}", style="primary"))
    if chat.username:
        m.row(ibtn(f"👤 Open Profile", url=f"https://t.me/{chat.username}", style="success"))
    m.row(ibtn("🔙 Back to Menu", callback_data="back_menu", style="danger"))

    increment_lookup(chat_id)
    return text, m
