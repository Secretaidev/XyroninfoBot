from config import OWNER_ID
from database import load_data, save_data
from buttons import ibtn, InlineKeyboardMarkup
from utils import safe_edit, safe_send


def show_admin_list(cid, mid=None):
    try:
        admins = load_data().get("extra_admins", [])
        text = (
            f"👮 <b>Admins</b>\n\n"
            f"👑 <b>Owner:</b> <code>{OWNER_ID}</code>\n"
            f"👮 <b>Extra Admins:</b> {len(admins)}\n\n"
        )
        if admins:
            for i, a in enumerate(admins, 1):
                text += f"  {i}. <code>{a}</code>\n"
        else:
            text += "  <i>No extra admins.</i>\n"
        m = InlineKeyboardMarkup()
        for a in admins:
            m.row(ibtn(f"🗑 Remove {a}", callback_data=f"deladm_{a}", style="danger"))
        m.row(ibtn("➕ Add Admin", callback_data="add_admin", style="success"))
        m.row(ibtn("🔙 Back to Panel", callback_data="back_owner", style="danger"))
        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def process_add_admin(message, cid=None):
    try:
        c = cid or message.chat.id
        t = message.text
        if t and t.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            show_admin_list(c)
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
            safe_send(c, "⚠️ Already owner!")
            return
        data = load_data()
        al = data.setdefault("extra_admins", [])
        if tid in al:
            safe_send(c, f"⚠️ <code>{tid}</code> already admin.")
            return
        al.append(tid)
        save_data(data)
        safe_send(c, f"✅ <code>{tid}</code> is now admin!")
        show_admin_list(c)
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")

def remove_admin(cid, tid, mid=None):
    try:
        data = load_data()
        al = data.get("extra_admins", [])
        if tid not in al:
            safe_send(cid, f"⚠️ <code>{tid}</code> not admin.")
            return
        al.remove(tid)
        save_data(data)
        safe_send(cid, f"🗑 <code>{tid}</code> removed!")
        show_admin_list(cid, mid)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")
