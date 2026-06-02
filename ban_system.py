from config import OWNER_ID
from database import load_data, save_data
from buttons import ibtn, InlineKeyboardMarkup
from utils import safe_edit, safe_send


def show_ban_menu(cid, mid=None):
    try:
        n = len(load_data().get("banned_users", []))
        text = f"━━━━━━━━━━━━━━━\n《 🚫 BAN SYSTEM 》\n━━━━━━━━━━━━━━━\n\n🚫 <b>Banned:</b> {n}\n\n━━━━━━━━━━━━━━━"
        m = InlineKeyboardMarkup()
        m.row(ibtn("🔨 Ban User", callback_data="ban_user", style="danger"))
        m.row(ibtn("📋 Banned List", callback_data="unban_list", style="primary"))
        m.row(ibtn("🔙 Back", callback_data="back_owner", style="danger"))
        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def show_banned_list(cid, mid=None):
    try:
        banned = load_data().get("banned_users", [])
        text = "━━━━━━━━━━━━━━━\n《 📋 BANNED LIST 》\n━━━━━━━━━━━━━━━\n\n"
        if not banned:
            text += "<i>No banned users.</i>\n"
        else:
            for i, uid in enumerate(banned, 1):
                text += f"  {i}. <code>{uid}</code>\n"
        text += "\n━━━━━━━━━━━━━━━"
        m = InlineKeyboardMarkup()
        for uid in banned:
            m.row(ibtn(f"✅ Unban {uid}", callback_data=f"unban_{uid}", style="success"))
        m.row(ibtn("🔙 Back", callback_data="back_ban", style="danger"))
        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def process_ban_user(message, cid=None):
    try:
        c = cid or message.chat.id
        t = message.text
        if t and t.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            show_ban_menu(c)
            return
        if not t or not t.strip():
            safe_send(c, "❌ Send a user ID.")
            return
        try:
            tid = int(t.strip())
        except ValueError:
            safe_send(c, "❌ Invalid ID.")
            return
        if tid == OWNER_ID:
            safe_send(c, "❌ Can't ban owner.")
            return
        data = load_data()
        bl = data.setdefault("banned_users", [])
        if tid in bl:
            safe_send(c, f"⚠️ <code>{tid}</code> already banned.")
            return
        bl.append(tid)
        save_data(data)
        safe_send(c, f"🚫 <code>{tid}</code> banned!")
        show_ban_menu(c)
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")

def unban_user(cid, tid, mid=None):
    try:
        data = load_data()
        bl = data.get("banned_users", [])
        if tid not in bl:
            safe_send(cid, f"⚠️ <code>{tid}</code> not banned.")
            return
        bl.remove(tid)
        save_data(data)
        safe_send(cid, f"✅ <code>{tid}</code> unbanned!")
        show_banned_list(cid, mid)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")
