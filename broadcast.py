import threading, time
from config import bot
from database import load_data
from buttons import ibtn, InlineKeyboardMarkup
from utils import safe_send, safe_edit


def start_broadcast(cid, mid=None):
    try:
        n = len(load_data().get("users", []))
        text = f"━━━━━━━━━━━━━━━\n《 📣 BROADCAST 》\n━━━━━━━━━━━━━━━\n\n👥 <b>Recipients:</b> {n}\n\n📝 Send your message now.\n⚠️ /cancel to abort.\n\n━━━━━━━━━━━━━━━"
        m = InlineKeyboardMarkup()
        m.row(ibtn("❌ Cancel", callback_data="back_owner", style="danger"))
        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def process_broadcast(message, cid=None):
    try:
        c = cid or message.chat.id
        if message.text and message.text.strip().lower() == "/cancel":
            safe_send(c, "❌ Cancelled.")
            return
        users = list(load_data().get("users", []))
        if not users:
            safe_send(c, "❌ No users.")
            return
        pmsg = safe_send(c, "⏳ Broadcasting...")
        thread = threading.Thread(target=_broadcast, args=(c, message, pmsg), daemon=True)
        thread.start()
    except Exception as e:
        safe_send(cid or message.chat.id, f"❌ Error: {e}")

def _broadcast(cid, src, pmsg):
    try:
        users = list(load_data().get("users", []))
        total, ok, fail = len(users), 0, 0
        pid = pmsg.message_id if pmsg else None

        for i, uid in enumerate(users):
            try:
                bot.copy_message(uid, src.chat.id, src.message_id)
                ok += 1
            except Exception:
                fail += 1
            if (i + 1) % 25 == 0 or (i + 1) == total:
                pct = int(((i + 1) / total) * 100)
                bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                txt = f"━━━━━━━━━━━━━━━\n📣 [{bar}] {pct}%\n\n✅ {ok}  ❌ {fail}  📨 {i+1}/{total}\n━━━━━━━━━━━━━━━"
                if pid:
                    safe_edit(cid, txt, message_id=pid)
            time.sleep(0.05)

        final = f"━━━━━━━━━━━━━━━\n《 ✅ DONE 》\n━━━━━━━━━━━━━━━\n\n👥 {total}  ✅ {ok}  ❌ {fail}\n\n━━━━━━━━━━━━━━━"
        m = InlineKeyboardMarkup()
        m.row(ibtn("🔙 Back", callback_data="back_owner", style="primary"))
        if pid:
            safe_edit(cid, final, m, pid)
        else:
            safe_send(cid, final, m)
    except Exception as e:
        safe_send(cid, f"❌ Broadcast error: {e}")
