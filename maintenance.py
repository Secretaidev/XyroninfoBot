from database import load_data, save_data
from buttons import ibtn, InlineKeyboardMarkup
from utils import safe_edit, safe_send


def is_maintenance():
    try:
        return load_data()["settings"].get("maintenance_mode", False)
    except Exception:
        return False

def get_maintenance_text():
    try:
        return load_data()["settings"].get("maintenance_message", "🔧 Under maintenance.")
    except Exception:
        return "🔧 Under maintenance."

def show_maintenance_settings(cid, mid=None):
    try:
        s = load_data()["settings"]
        on = s.get("maintenance_mode", False)
        msg = s.get("maintenance_message", "Not set")
        status = "✅ ON" if on else "❌ OFF"
        tog = "🔴 Disable" if on else "🟢 Enable"
        sty = "danger" if on else "success"

        text = (
            "━━━━━━━━━━━━━━━\n"
            "《 🛡️ MAINTENANCE 》\n"
            "━━━━━━━━━━━━━━━\n\n"
            f"📌 <b>Status:</b> {status}\n\n"
            f"💬 <b>Message:</b>\n<i>{msg}</i>\n"
            "\n━━━━━━━━━━━━━━━"
        )

        m = InlineKeyboardMarkup()
        m.row(ibtn(tog, callback_data="maint_toggle", style=sty))
        m.row(ibtn("✏️ Edit Message", callback_data="maint_edit_msg", style="primary"))
        m.row(ibtn("🔙 Back", callback_data="back_owner", style="danger"))

        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def toggle_maintenance(cid, mid=None):
    try:
        data = load_data()
        data["settings"]["maintenance_mode"] = not data["settings"].get("maintenance_mode", False)
        save_data(data)
        show_maintenance_settings(cid, mid)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def process_maintenance_msg(message, cid=None):
    try:
        c = cid or message.chat.id
        t = message.text
        if t and t.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            return
        if not t or not t.strip():
            safe_send(c, "❌ Empty message.")
            return
        data = load_data()
        data["settings"]["maintenance_message"] = t.strip()
        save_data(data)
        safe_send(c, "✅ Maintenance message updated!")
        show_maintenance_settings(c)
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")
