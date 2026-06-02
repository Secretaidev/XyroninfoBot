from database import load_data, save_data, get_stats
from buttons import ibtn, InlineKeyboardMarkup
from utils import safe_edit, safe_send, esc


def get_owner_keyboard():
    m = InlineKeyboardMarkup()
    m.row(
        ibtn("📊 Statistics", callback_data="owner_stats", style="primary"),
        ibtn("🔧 Settings", callback_data="owner_settings", style="success")
    )
    m.row(
        ibtn("🛡️ Maintenance", callback_data="owner_maintenance", style="primary"),
        ibtn("📢 Force Join", callback_data="owner_forcejoin", style="success")
    )
    m.row(
        ibtn("📣 Broadcast", callback_data="owner_broadcast", style="primary"),
        ibtn("👮 Admins", callback_data="owner_admins", style="success")
    )
    m.row(
        ibtn("🚫 Ban/Unban", callback_data="owner_ban", style="danger"),
        ibtn("👥 Users List", callback_data="owner_users", style="primary")
    )
    m.row(
        ibtn("💎 Watermark", callback_data="owner_watermark", style="success"),
        ibtn("🔗 Support Link", callback_data="owner_support", style="primary")
    )
    m.row(
        ibtn("📈 Lookup Stats", callback_data="owner_lookups", style="success"),
        ibtn("📝 Welcome Msg", callback_data="owner_welcome", style="primary")
    )
    m.row(ibtn("❌ Close Panel", callback_data="owner_close", style="danger"))
    return m


def show_owner_panel(cid, user_id=None, msg_id=None):
    try:
        s = get_stats()
        d = load_data()
        maint = "✅ ON" if d["settings"].get("maintenance_mode", False) else "❌ OFF"
        fj = "✅ ON" if d["settings"].get("force_join_enabled", False) else "❌ OFF"

        text = (
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "《 👑 OWNER PANEL 》\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 DATABASE STATISTICS\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Total Users:</b> {s['total_users']}\n"
            f"🔍 <b>Total Lookups:</b> {s['total_lookups']}\n"
            f"👮 <b>Extra Admins:</b> {s['total_admins']}\n"
            f"🚫 <b>Banned Users:</b> {s['banned_users']}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ QUICK STATUS\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛡️ <b>Maintenance:</b> {maint}\n"
            f"📢 <b>Force Join:</b> {fj}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        m = get_owner_keyboard()
        if msg_id:
            safe_edit(cid, text, m, msg_id)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error loading panel: {e}")


def show_settings_menu(cid, user_id=None, msg_id=None):
    try:
        s = load_data()["settings"]
        wm = esc(s.get("watermark", "—"))
        sl = esc(s.get("support_link", "—"))
        wl = s.get("welcome_message", "") or "—"
        if len(wl) > 100:
            wl = esc(wl[:100]) + "..."
        else:
            wl = esc(wl)

        text = (
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "《 🔧 BOT SETTINGS 》\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💎 <b>Watermark:</b> {wm}\n\n"
            f"🔗 <b>Support Link:</b> {sl}\n\n"
            f"📝 <b>Welcome Message:</b>\n<i>{wl}</i>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        m = InlineKeyboardMarkup()
        m.row(ibtn("💎 Change Watermark", callback_data="set_watermark", style="primary"))
        m.row(ibtn("🔗 Change Support Link", callback_data="set_support", style="success"))
        m.row(ibtn("📝 Change Welcome Message", callback_data="set_welcome", style="primary"))
        m.row(ibtn("🔙 Back to Panel", callback_data="back_owner", style="danger"))
        if msg_id:
            safe_edit(cid, text, m, msg_id)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error loading settings: {e}")


def process_set_watermark(message, cid=None):
    try:
        c = cid or message.chat.id
        t = message.text
        if t and t.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            show_owner_panel(c)
            return
        if not t or not t.strip():
            safe_send(c, "❌ Watermark cannot be empty.")
            return
        data = load_data()
        data["settings"]["watermark"] = t.strip()
        save_data(data)
        safe_send(c, f"✅ Watermark updated to: <b>{esc(t.strip())}</b>")
        show_settings_menu(c)
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")


def process_set_support(message, cid=None):
    try:
        c = cid or message.chat.id
        t = message.text
        if t and t.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            show_owner_panel(c)
            return
        if not t or not t.strip():
            safe_send(c, "❌ Support link cannot be empty.")
            return
        data = load_data()
        data["settings"]["support_link"] = t.strip()
        save_data(data)
        safe_send(c, f"✅ Support link updated to: <b>{esc(t.strip())}</b>")
        show_settings_menu(c)
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")


def process_set_welcome(message, cid=None):
    try:
        c = cid or message.chat.id
        t = message.text
        if t and t.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            show_owner_panel(c)
            return
        if not t or not t.strip():
            safe_send(c, "❌ Welcome message cannot be empty.")
            return
        data = load_data()
        data["settings"]["welcome_message"] = t.strip()
        save_data(data)
        safe_send(c, "✅ Welcome message updated!")
        show_settings_menu(c)
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")
