import io
from config import bot, OWNER_ID
from database import load_data, is_banned, is_admin
from buttons import ibtn, InlineKeyboardMarkup
from utils import safe_edit, safe_send

PER_PAGE = 20

def show_users_list(cid, page=0, msg_id=None):
    try:
        users = load_data().get("users", [])
        total = len(users)
        if not total:
            text = "━━━━━━━━━━━━━━━\n《 👥 USERS 》\n━━━━━━━━━━━━━━━\n\n<i>No users yet.</i>\n\n━━━━━━━━━━━━━━━"
            m = InlineKeyboardMarkup()
            m.row(ibtn("🔙 Back", callback_data="back_owner", style="danger"))
            if msg_id:
                safe_edit(cid, text, m, msg_id)
            else:
                safe_send(cid, text, m)
            return

        pages = (total + PER_PAGE - 1) // PER_PAGE
        page = max(0, min(page, pages - 1))
        start = page * PER_PAGE
        chunk = users[start:start + PER_PAGE]

        text = f"━━━━━━━━━━━━━━━\n《 👥 USERS 》\n━━━━━━━━━━━━━━━\n\n📊 <b>Total:</b> {total}  📄 {page+1}/{pages}\n\n"
        for i, uid in enumerate(chunk, start + 1):
            icons = ""
            if uid == OWNER_ID:
                icons = " 👑"
            elif is_admin(uid):
                icons = " 👮"
            if is_banned(uid):
                icons += " 🚫"
            text += f"  {i}. <code>{uid}</code>{icons}\n"
        text += "\n━━━━━━━━━━━━━━━"

        m = InlineKeyboardMarkup()
        nav = []
        if page > 0:
            nav.append(ibtn("⬅️", callback_data=f"users_page_{page-1}", style="primary"))
        if page < pages - 1:
            nav.append(ibtn("➡️", callback_data=f"users_page_{page+1}", style="primary"))
        if nav:
            m.row(*nav)
        m.row(ibtn("📤 Export", callback_data="export_users", style="success"))
        m.row(ibtn("🔙 Back", callback_data="back_owner", style="danger"))

        if msg_id:
            safe_edit(cid, text, m, msg_id)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def show_user_detail(cid, tid, mid=None):
    try:
        data = load_data()
        lookups = data.get("lookup_stats", {}).get(str(tid), 0)
        banned = is_banned(tid)
        admin = is_admin(tid)
        owner = tid == OWNER_ID

        role = "👑 Owner" if owner else ("👮 Admin" if admin else "👤 User")
        b_stat = "🚫 Yes" if banned else "✅ No"

        text = f"━━━━━━━━━━━━━━━\n《 👤 USER 》\n━━━━━━━━━━━━━━━\n\n🆔 <b>ID:</b> <code>{tid}</code>\n🏷 <b>Role:</b> {role}\n🚫 <b>Banned:</b> {b_stat}\n🔍 <b>Lookups:</b> {lookups}\n\n━━━━━━━━━━━━━━━"
        m = InlineKeyboardMarkup()
        if not owner:
            if banned:
                m.row(ibtn("✅ Unban", callback_data=f"unban_{tid}", style="success"))
            else:
                m.row(ibtn("🚫 Ban", callback_data=f"ban_direct_{tid}", style="danger"))
        m.row(ibtn("🔙 Back", callback_data="users_page_0", style="danger"))
        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def export_users(cid):
    try:
        users = load_data().get("users", [])
        if not users:
            safe_send(cid, "❌ No users.")
            return
        f = io.BytesIO("\n".join(str(u) for u in users).encode())
        f.name = "users.txt"
        bot.send_document(cid, f, caption=f"📤 <b>Export</b> — {len(users)} users", parse_mode="HTML")
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")

def show_lookup_stats(cid, mid=None):
    try:
        data = load_data()
        total = data.get("total_lookups", 0)
        top = sorted(data.get("lookup_stats", {}).items(), key=lambda x: x[1], reverse=True)[:10]
        medals = ["🥇", "🥈", "🥉"]

        text = f"━━━━━━━━━━━━━━━\n《 📈 LOOKUPS 》\n━━━━━━━━━━━━━━━\n\n🔍 <b>Total:</b> {total}\n\n"
        if top:
            for i, (uid, cnt) in enumerate(top):
                medal = medals[i] if i < 3 else f"  {i+1}."
                text += f"{medal} <code>{uid}</code> → {cnt}\n"
        else:
            text += "<i>No data yet.</i>\n"
        text += "\n━━━━━━━━━━━━━━━"

        m = InlineKeyboardMarkup()
        m.row(ibtn("🔙 Back", callback_data="back_owner", style="danger"))
        if mid:
            safe_edit(cid, text, m, mid)
        else:
            safe_send(cid, text, m)
    except Exception as e:
        safe_send(cid, f"❌ Error: {e}")
