from config import bot
from database import load_data, save_data
from buttons import ibtn, InlineKeyboardMarkup
from utils import safe_edit, safe_send, ch_username


def check_force_join(user_id):
    try:
        s = load_data()["settings"]
        if not s.get("force_join_enabled", False):
            return True
        channels = s.get("force_join_channels", [])
        if not channels:
            return True
        for ch in channels:
            try:
                un = ch_username(ch)
                if not un:
                    continue
                mem = bot.get_chat_member(f"@{un}", user_id)
                if mem.status in ("left", "kicked"):
                    return False
            except Exception:
                continue
        return True
    except Exception:
        return True

def show_force_join_prompt(cid, uid=None):
    try:
        chs = load_data()["settings"].get("force_join_channels", [])
        text = "🔐 <b>Join Required</b>\n\n📢 Join our channels to continue:\n"
        m = InlineKeyboardMarkup()
        for ch in chs:
            un = ch_username(ch)
            url = ch if ch.startswith("http") else f"https://t.me/{un}"
            m.row(ibtn(f"📢 Join @{un}", url=url, style="primary"))
        m.row(ibtn("✅ I Joined", callback_data="check_joined", style="success"))
        safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def show_force_join_settings(cid, mid=None):
    try:
        s = load_data()["settings"]
        on = s.get("force_join_enabled", False)
        chs = s.get("force_join_channels", [])
        status = "✅ ON" if on else "❌ OFF"
        tog = "🔴 Disable" if on else "🟢 Enable"
        sty = "danger" if on else "success"

        text = (
            f"📢 <b>Force Join</b>\n\n"
            f"📌 <b>Status:</b> {status}\n"
            f"📊 <b>Channels:</b> {len(chs)}\n\n"
        )
        if chs:
            for i, ch in enumerate(chs):
                un = ch_username(ch)
                text += f"  {i+1}. @{un}\n"
        else:
            text += "  <i>No channels yet.</i>\n"

        m = InlineKeyboardMarkup()
        m.row(ibtn(tog, callback_data="fj_toggle", style=sty))
        for i, ch in enumerate(chs):
            un = ch_username(ch)
            m.row(ibtn(f"🗑 Remove @{un}", callback_data=f"fj_del_{i}", style="danger"))
        m.row(ibtn("➕ Add Channel", callback_data="fj_add", style="primary"))
        m.row(ibtn("🔙 Back to Panel", callback_data="back_owner", style="danger"))

        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def toggle_force_join(cid, mid=None):
    try:
        data = load_data()
        data["settings"]["force_join_enabled"] = not data["settings"].get("force_join_enabled", False)
        save_data(data)
        show_force_join_settings(cid, mid)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def process_add_fj_channel(message, cid=None):
    try:
        c = cid or message.chat.id
        t = message.text
        if t and t.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            return
        if not t or not t.strip():
            safe_send(c, "❌ Send a valid link.")
            return
        raw = t.strip()
        un = ch_username(raw) if not raw.startswith("@") else raw[1:]
        if not un:
            safe_send(c, "❌ Invalid link. Send t.me/channel or @channel.")
            return
        try:
            bot.get_chat(f"@{un}")
        except Exception:
            safe_send(c, "❌ Can't access channel. Make bot admin there.")
            return
        data = load_data()
        chs = data["settings"].setdefault("force_join_channels", [])
        for ex in chs:
            if ch_username(ex) == un:
                safe_send(c, "⚠️ Already in list.")
                return
        chs.append(f"https://t.me/{un}")
        save_data(data)
        safe_send(c, f"✅ @{un} added!")
        show_force_join_settings(c)
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")

def remove_fj_channel(cid, idx_str, mid=None):
    try:
        data = load_data()
        chs = data["settings"].get("force_join_channels", [])
        idx = int(idx_str)
        if idx < 0 or idx >= len(chs):
            safe_send(cid, "❌ Invalid index.")
            return
        removed = chs.pop(idx)
        save_data(data)
        un = ch_username(removed)
        safe_send(cid, f"🗑 @{un} removed!")
        show_force_join_settings(cid, mid)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")
