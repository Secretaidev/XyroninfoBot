import json as _json, io, time
from config import bot, OWNER_ID
from database import load_data, save_data, add_user, is_banned, is_admin, is_owner, get_stats, increment_lookup
import buttons
from buttons import ibtn, rbtn, InlineKeyboardMarkup, ReplyKeyboardMarkup
from utils import safe_send, safe_edit, esc, plink, get_wm, get_support, del_msg, del_prev, menu_msg, ping_ms, lang_name, fmt_num
from registration import get_full_registration_info, get_registration_text, get_telegram_era
from info_user import extract_user_info
from info_bot import extract_bot_info
from info_channel import extract_channel_info
from info_group import extract_group_info
from info_forum import extract_forum_info
from maintenance import is_maintenance, get_maintenance_text, show_maintenance_settings, toggle_maintenance, process_maintenance_msg
from force_join import check_force_join, show_force_join_prompt, show_force_join_settings, toggle_force_join, process_add_fj_channel, remove_fj_channel
from ban_system import show_ban_menu, show_banned_list, process_ban_user, unban_user
from admin_manager import show_admin_list, process_add_admin, remove_admin
from broadcast import process_broadcast
from user_manager import show_users_list, show_user_detail, export_users, show_lookup_stats
from owner_panel import show_owner_panel, show_settings_menu, process_set_watermark, process_set_support, process_set_welcome

_state = {}
_start_time = time.time()


def _kb(uid):
    m = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(rbtn('👤 User', 'primary'), rbtn('🤖 Bot', 'success'))
    m.add(rbtn('📢 Channel', 'primary'), rbtn('👥 Group', 'success'))
    m.add(rbtn('🏠 My Channel', 'primary'), rbtn('🏠 My Group', 'success'))
    m.add(rbtn('💬 Forum', 'primary'), rbtn('💬 My Forum', 'success'))
    if is_admin(uid):
        m.add(rbtn('⚙️ Owner Panel', 'danger'))
    return m


def _cancel_mk():
    return InlineKeyboardMarkup().add(ibtn('🔙 Cancel', callback_data='back_owner', style='danger'))


def _menu(cid, uid, name='User', reply_to=None):
    wm = esc(get_wm())
    text = (
        f'━━━━━━━━━━━━━━━━━━━━━\n'
        f'《 🔱 XYRON INFO BOT 》\n'
        f'━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'👋 Welcome, {plink(uid, name)}!\n\n'
        f'🔍 Send me any @username or User ID\n'
        f'📨 Or forward any message to get info\n'
        f'📋 Use the buttons below to select type\n\n'
        f'━━━━━━━━━━━━━━━━━━━━━\n'
        f'⚡ Powered by {wm}'
    )
    safe_send(cid, text, _kb(uid), reply_to)


MODES = {
    '👤 User': ('user', '👤 <b>User Info Mode</b>\n\n📝 Send me a @username or User ID'),
    '🤖 Bot': ('bot', '🤖 <b>Bot Info Mode</b>\n\n📝 Send me a bot @username (e.g. @BotFather)'),
    '📢 Channel': ('channel', '📢 <b>Channel Info Mode</b>\n\n📝 Send me a channel @username or ID'),
    '👥 Group': ('group', '👥 <b>Group Info Mode</b>\n\n📝 Send me a group @username or ID'),
    '🏠 My Channel': ('channel', '📢 <b>My Channel Info</b>\n\n📝 Forward a message from your channel\n📝 Or send the channel @username'),
    '🏠 My Group': ('group', '👥 <b>My Group Info</b>\n\n📝 Forward a message from your group\n📝 Or send the group @username'),
    '💬 Forum': ('forum', '💬 <b>Forum Info Mode</b>\n\n📝 Send me a forum @username or ID'),
    '💬 My Forum': ('forum', '💬 <b>My Forum Info</b>\n\n📝 Forward a message from your forum\n📝 Or send the forum @username'),
}


def _set_mode(cid, mode, prompt):
    _state[cid] = mode
    wm = esc(get_wm())
    m = InlineKeyboardMarkup()
    m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
    msg = safe_send(cid, f'━━━━━━━━━━━━━━━\n{prompt}\n━━━━━━━━━━━━━━━\n⚡ Powered by {wm}', m)
    if msg:
        menu_msg[cid] = msg.message_id


def _process(cid, uid, text):
    mode = _state.pop(cid, None)
    target = text.strip()
    if target.lstrip('-').isdigit():
        target = int(target)

    increment_lookup(uid)
    handlers = {
        'user': extract_user_info, 'bot': extract_bot_info,
        'channel': extract_channel_info, 'group': extract_group_info,
        'forum': extract_forum_info,
    }

    try:
        if mode and mode in handlers:
            t, m = handlers[mode](target, cid)
        else:
            t, m = _detect(target, cid)
        safe_send(cid, t, m)
    except Exception as e:
        safe_send(cid, f'❌ <b>Error:</b> {esc(str(e))}')


def _detect(target, cid):
    try:
        chat = bot.get_chat(target)
    except Exception:
        return (
            '❌ <b>Not Found</b>\n\n'
            '🔍 Could not find this user/chat.\n'
            '💡 Make sure the username or ID is correct.',
            None
        )
    if chat.type == 'private':
        un = (chat.username or '').lower()
        return extract_bot_info(target, cid) if un.endswith('bot') else extract_user_info(target, cid)
    elif chat.type == 'channel':
        return extract_channel_info(target, cid)
    elif chat.type in ('group', 'supergroup'):
        return extract_forum_info(target, cid) if getattr(chat, 'is_forum', False) else extract_group_info(target, cid)
    return extract_user_info(target, cid)


def _uptime():
    diff = int(time.time() - _start_time)
    d, diff = divmod(diff, 86400)
    h, diff = divmod(diff, 3600)
    m, s = divmod(diff, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


@bot.message_handler(commands=['start'], chat_types=['private'])
def cmd_start(msg):
    uid, cid, name = msg.from_user.id, msg.chat.id, msg.from_user.first_name or 'User'
    add_user(uid)
    if is_maintenance() and not is_admin(uid):
        safe_send(cid, get_maintenance_text())
        return
    if not check_force_join(uid):
        show_force_join_prompt(cid, uid)
        return
    _state.pop(cid, None)
    _menu(cid, uid, name, msg.message_id)


@bot.message_handler(commands=['help'], chat_types=['private'])
def cmd_help(msg):
    cid = msg.chat.id
    sl = get_support()
    wm = esc(get_wm())
    text = (
        '━━━━━━━━━━━━━━━━━━━━━\n'
        '《 📖 HELP & COMMANDS 》\n'
        '━━━━━━━━━━━━━━━━━━━━━\n\n'
        '🔹 /start — Restart the bot\n'
        '🔹 /help — Show this help menu\n'
        '🔹 /id — Get your Telegram ID\n'
        '🔹 /ping — Check bot speed\n'
        '🔹 /about — About this bot\n'
        '🔹 /json — Get info as JSON file\n\n'
        '<b>📋 How to use:</b>\n\n'
        '1️⃣ Select a type using the buttons\n'
        '2️⃣ Send a @username or numeric ID\n'
        '3️⃣ Or just forward any message!\n\n'
        '<b>🔍 Supported types:</b>\n\n'
        '👤 <b>User</b> — Profile info, DC, registration\n'
        '🤖 <b>Bot</b> — Bot details & capabilities\n'
        '📢 <b>Channel</b> — Channel statistics\n'
        '👥 <b>Group</b> — Group info & permissions\n'
        '💬 <b>Forum</b> — Forum topic group info\n\n'
        '💡 <b>Tip:</b> You can also send any\n'
        'username/ID without selecting a mode!\n\n'
        f'━━━━━━━━━━━━━━━━━━━━━\n'
        f'⚡ Powered by {wm}'
    )
    m = InlineKeyboardMarkup()
    m.add(ibtn('💬 Support', url=sl, style='primary'))
    m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
    safe_send(cid, text, m)


@bot.message_handler(commands=['id'], chat_types=['private'])
def cmd_id(msg):
    uid, cid = msg.from_user.id, msg.chat.id
    name = esc(msg.from_user.first_name or 'User')
    text = (
        '━━━━━━━━━━━━━━━━━━━━━\n'
        '《 🆔 YOUR TELEGRAM ID 》\n'
        '━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'👤 <b>Name:</b> {name}\n'
        f'🆔 <b>ID:</b> <code>{uid}</code>\n\n'
        '━━━━━━━━━━━━━━━━━━━━━'
    )
    m = InlineKeyboardMarkup()
    m.add(ibtn('📋 Copy ID', copy_text=str(uid), style='primary'))
    m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
    safe_send(cid, text, m)


@bot.message_handler(commands=['ping'], chat_types=['private'])
def cmd_ping(msg):
    cid = msg.chat.id
    ms = ping_ms()
    up = _uptime()
    text = (
        '━━━━━━━━━━━━━━━━━━━━━\n'
        '《 🏓 PONG 》\n'
        '━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'⚡ <b>Response:</b> {ms}ms\n'
        f'⏱ <b>Uptime:</b> {up}\n'
        f'🖥 <b>Status:</b> Running\n\n'
        '━━━━━━━━━━━━━━━━━━━━━'
    )
    m = InlineKeyboardMarkup()
    m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
    safe_send(cid, text, m)


@bot.message_handler(commands=['about'], chat_types=['private'])
def cmd_about(msg):
    cid = msg.chat.id
    wm = esc(get_wm())
    sl = get_support()
    s = get_stats()
    text = (
        '━━━━━━━━━━━━━━━━━━━━━\n'
        '《 🔱 ABOUT 》\n'
        '━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'📛 <b>Name:</b> {wm}\n'
        '📋 <b>Type:</b> User Info Bot\n\n'
        '<b>🔍 What I can do:</b>\n\n'
        '• Extract detailed user profiles\n'
        '• Detect data center locations\n'
        '• Estimate registration dates\n'
        '• Show channel/group statistics\n'
        '• Identify bot capabilities\n'
        '• Detect premium & verified status\n'
        '• Export info as JSON files\n\n'
        f'👥 <b>Users:</b> {fmt_num(s["total_users"])}\n'
        f'🔍 <b>Lookups:</b> {fmt_num(s["total_lookups"])}\n\n'
        f'━━━━━━━━━━━━━━━━━━━━━\n'
        f'⚡ Powered by {wm}'
    )
    m = InlineKeyboardMarkup()
    m.add(ibtn('💬 Support', url=sl, style='primary'))
    m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
    safe_send(cid, text, m)


@bot.message_handler(commands=['json'], chat_types=['private'])
def cmd_json(msg):
    cid = msg.chat.id
    uid = msg.from_user.id
    if is_banned(uid):
        safe_send(cid, '🚫 <b>Access Denied</b>')
        return
    _state[cid] = 'json'
    m = InlineKeyboardMarkup()
    m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
    safe_send(cid, '━━━━━━━━━━━━━━━\n📄 <b>JSON Export Mode</b>\n\n📝 Send @username or ID to get JSON file\n━━━━━━━━━━━━━━━', m)


def _export_json(target, cid):
    try:
        chat = bot.get_chat(target)
    except Exception:
        safe_send(cid, '❌ <b>Not found!</b>')
        return

    data = {
        "id": chat.id,
        "type": chat.type,
        "first_name": chat.first_name,
        "last_name": chat.last_name,
        "username": chat.username,
        "bio": chat.bio,
        "description": chat.description,
        "title": getattr(chat, "title", None),
        "is_premium": getattr(chat, "is_premium", None),
        "is_verified": getattr(chat, "is_verified", None),
        "is_scam": getattr(chat, "is_scam", None),
        "is_fake": getattr(chat, "is_fake", None),
        "is_forum": getattr(chat, "is_forum", None),
    }

    if chat.type == 'private':
        try:
            pp = bot.get_user_profile_photos(chat.id)
            data["profile_photos"] = pp.total_count if pp else 0
        except Exception:
            pass
        ri = get_full_registration_info(chat.id)
        data["registration"] = ri

    try:
        mc = bot.get_chat_member_count(chat.id)
        data["member_count"] = mc
    except Exception:
        pass

    data = {k: v for k, v in data.items() if v is not None}
    content = _json.dumps(data, indent=2, ensure_ascii=False)
    f = io.BytesIO(content.encode())
    f.name = f"{chat.id}_info.json"
    bot.send_document(cid, f, caption=f"📄 <b>JSON Export</b> — <code>{chat.id}</code>", parse_mode="HTML")


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'sticker', 'animation', 'voice', 'video_note'],
                     chat_types=['private'],
                     func=lambda m: m.forward_from is not None or m.forward_from_chat is not None or m.forward_sender_name is not None)
def on_forward(msg):
    uid, cid = msg.from_user.id, msg.chat.id
    if is_banned(uid):
        safe_send(cid, '🚫 <b>Access Denied</b>\n\nYou have been banned from using this bot.')
        return
    if is_maintenance() and not is_admin(uid):
        safe_send(cid, get_maintenance_text())
        return
    if not check_force_join(uid):
        show_force_join_prompt(cid, uid)
        return

    del_msg(cid, msg.message_id)
    add_user(uid)
    increment_lookup(uid)

    if msg.forward_from:
        fw = msg.forward_from
        un = (fw.username or '').lower()
        t, m = extract_bot_info(fw.id, cid) if (fw.is_bot or un.endswith('bot')) else extract_user_info(fw.id, cid)
        safe_send(cid, t, m)
        return

    if msg.forward_from_chat:
        fc = msg.forward_from_chat
        if fc.type == 'channel':
            t, m = extract_channel_info(fc.id, cid)
        elif fc.type in ('group', 'supergroup'):
            t, m = extract_forum_info(fc.id, cid) if getattr(fc, 'is_forum', False) else extract_group_info(fc.id, cid)
        else:
            t, m = extract_channel_info(fc.id, cid)
        safe_send(cid, t, m)
        return

    if msg.forward_sender_name:
        text = (
            '━━━━━━━━━━━━━━━━━━━━━\n'
            '《 👻 HIDDEN USER 》\n'
            '━━━━━━━━━━━━━━━━━━━━━\n\n'
            f'👤 <b>Name:</b> {esc(msg.forward_sender_name)}\n'
            '🔒 <b>Privacy:</b> Enabled\n\n'
            '⚠️ This user has hidden their account.\n'
            'Their forwarded messages cannot reveal their ID.\n\n'
            '━━━━━━━━━━━━━━━━━━━━━'
        )
        m = InlineKeyboardMarkup()
        m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
        safe_send(cid, text, m)


@bot.message_handler(func=lambda message: True, content_types=['text'], chat_types=['private'])
def on_text(msg):
    uid, cid = msg.from_user.id, msg.chat.id
    name = msg.from_user.first_name or 'User'
    text = msg.text.strip()

    if is_banned(uid):
        safe_send(cid, '🚫 <b>Access Denied</b>\n\nYou have been banned from using this bot.')
        return
    if is_maintenance() and not is_admin(uid):
        safe_send(cid, get_maintenance_text())
        return
    if not check_force_join(uid):
        show_force_join_prompt(cid, uid)
        return

    del_msg(cid, msg.message_id)
    del_prev(cid)
    add_user(uid)

    if text in MODES:
        mode, prompt = MODES[text]
        _set_mode(cid, mode, prompt)
        return

    if text == '⚙️ Owner Panel':
        if is_admin(uid):
            show_owner_panel(cid, user_id=uid)
        else:
            safe_send(cid, '🚫 <b>Access Denied</b>\n\nYou are not authorized to access the owner panel.')
        return

    cur_state = _state.get(cid)
    if cur_state == 'json':
        _state.pop(cid, None)
        target = text.strip()
        if target.lstrip('-').isdigit():
            target = int(target)
        _export_json(target, cid)
        return

    _process(cid, uid, text)


@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    cid = call.message.chat.id
    uid = call.from_user.id
    mid = call.message.message_id
    d = call.data
    name = call.from_user.first_name or 'User'

    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    if d == 'noop':
        return

    if d == 'back_menu':
        _state.pop(cid, None)
        del_msg(cid, mid)
        _menu(cid, uid, name)
        return

    if d == 'check_joined':
        if check_force_join(uid):
            del_msg(cid, mid)
            _menu(cid, uid, name)
        else:
            try:
                bot.answer_callback_query(call.id, '❌ You haven\'t joined all channels yet!', show_alert=True)
            except Exception:
                pass
        return

    if d.startswith('reg_detail_'):
        try:
            tid = int(d[11:])
        except ValueError:
            return
        ri = get_full_registration_info(tid)
        text = (
            '━━━━━━━━━━━━━━━━━━━━━\n'
            '《 📅 REGISTRATION DETAILS 》\n'
            '━━━━━━━━━━━━━━━━━━━━━\n\n'
            f'🆔 <b>User ID:</b> <code>{tid}</code>\n'
            f'📅 <b>Est. Date:</b> {esc(ri["date"])}\n'
            f'📆 <b>Account Age:</b> {esc(ri["formatted"])}\n'
            f'📅 <b>Year:</b> {ri["year"] or "Unknown"}\n'
            f'🏛 <b>Telegram Era:</b> {esc(ri["era"])}\n\n'
            '━━━━━━━━━━━━━━━━━━━━━'
        )
        m = InlineKeyboardMarkup()
        m.add(ibtn('🔙 Back to Menu', callback_data='back_menu', style='danger'))
        safe_edit(cid, text, m, mid)
        return

    def _admin_gate():
        if not is_admin(uid):
            try:
                bot.answer_callback_query(call.id, '🚫 Access Denied', show_alert=True)
            except Exception:
                pass
            return False
        return True

    def _owner_gate():
        if not is_owner(uid):
            try:
                bot.answer_callback_query(call.id, '🚫 Only the owner can do this', show_alert=True)
            except Exception:
                pass
            return False
        return True

    if d == 'owner_panel':
        if _admin_gate():
            show_owner_panel(cid, user_id=uid, msg_id=mid)
        return

    if d == 'owner_stats':
        if _admin_gate():
            s = get_stats()
            text = (
                '━━━━━━━━━━━━━━━━━━━━━\n'
                '《 📊 BOT STATISTICS 》\n'
                '━━━━━━━━━━━━━━━━━━━━━\n\n'
                f'👥 <b>Total Users:</b> {fmt_num(s["total_users"])}\n'
                f'🚫 <b>Banned Users:</b> {s["banned_users"]}\n'
                f'👑 <b>Extra Admins:</b> {s["total_admins"]}\n'
                f'🔍 <b>Total Lookups:</b> {fmt_num(s["total_lookups"])}\n'
                f'⚡ <b>Response:</b> {ping_ms()}ms\n'
                f'⏱ <b>Uptime:</b> {_uptime()}\n\n'
                '━━━━━━━━━━━━━━━━━━━━━'
            )
            m = InlineKeyboardMarkup()
            m.add(ibtn('🔙 Back to Panel', callback_data='owner_panel', style='danger'))
            safe_edit(cid, text, m, mid)
        return

    if d == 'owner_settings':
        if _admin_gate():
            show_settings_menu(cid, user_id=uid, msg_id=mid)
        return

    if d == 'owner_maintenance':
        if _admin_gate():
            show_maintenance_settings(cid, mid)
        return

    if d == 'owner_forcejoin':
        if _admin_gate():
            show_force_join_settings(cid, mid)
        return

    if d == 'owner_broadcast':
        if _admin_gate():
            n = len(load_data().get("users", []))
            safe_edit(cid,
                f'━━━━━━━━━━━━━━━━━━━━━\n'
                f'《 📣 BROADCAST 》\n'
                f'━━━━━━━━━━━━━━━━━━━━━\n\n'
                f'👥 <b>Total Recipients:</b> {fmt_num(n)}\n\n'
                f'📝 Send me the message you want to broadcast.\n'
                f'You can send <b>text, photo, video, document</b> or any type.\n\n'
                f'⚠️ Send /cancel to abort.\n\n'
                f'━━━━━━━━━━━━━━━━━━━━━',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_broadcast(m, cid))
        return

    if d == 'owner_admins':
        if _owner_gate():
            show_admin_list(cid, mid)
        return

    if d == 'owner_ban':
        if _admin_gate():
            show_ban_menu(cid, mid)
        return

    if d == 'owner_users':
        if _admin_gate():
            show_users_list(cid, page=0, msg_id=mid)
        return

    if d == 'owner_watermark':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 💎 SET WATERMARK 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the new watermark text:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_set_watermark(m, cid))
        return

    if d == 'owner_support':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 🔗 SET SUPPORT LINK 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the new support link\n'
                '(e.g. https://t.me/your_channel):',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_set_support(m, cid))
        return

    if d == 'owner_lookups':
        if _admin_gate():
            show_lookup_stats(cid, mid)
        return

    if d == 'owner_welcome':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 📝 SET WELCOME MSG 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the new welcome message:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_set_welcome(m, cid))
        return

    if d == 'owner_close':
        if _admin_gate():
            del_msg(cid, mid)
            _menu(cid, uid, name)
        return

    if d == 'maint_toggle':
        if _admin_gate():
            toggle_maintenance(cid, mid)
        return

    if d == 'maint_edit_msg':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 ✏️ MAINTENANCE MESSAGE 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the new maintenance message:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_maintenance_msg(m, cid))
        return

    if d == 'fj_toggle':
        if _admin_gate():
            toggle_force_join(cid, mid)
        return

    if d == 'fj_add':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 ➕ ADD CHANNEL 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the channel link or @username\n'
                '(e.g. https://t.me/channel or @channel):',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_add_fj_channel(m, cid))
        return

    if d.startswith('fj_del_'):
        if _admin_gate():
            remove_fj_channel(cid, d[7:], mid)
        return

    if d == 'ban_user':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 🔨 BAN USER 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the User ID to ban:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_ban_user(m, cid))
        return

    if d == 'unban_list':
        if _admin_gate():
            show_banned_list(cid, mid)
        return

    if d.startswith('unban_'):
        if _admin_gate():
            try:
                unban_user(cid, int(d[6:]), mid)
            except ValueError:
                pass
        return

    if d == 'add_admin':
        if _owner_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 ➕ ADD ADMIN 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the User ID to add as admin:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_add_admin(m, cid))
        return

    if d.startswith('deladm_'):
        if _owner_gate():
            try:
                remove_admin(cid, int(d[7:]), mid)
            except ValueError:
                pass
        return

    if d.startswith('users_page_'):
        if _admin_gate():
            try:
                show_users_list(cid, page=int(d[11:]), msg_id=mid)
            except ValueError:
                show_users_list(cid, page=0, msg_id=mid)
        return

    if d.startswith('user_detail_'):
        if _admin_gate():
            try:
                show_user_detail(cid, int(d[12:]), mid)
            except ValueError:
                pass
        return

    if d == 'export_users':
        if _admin_gate():
            export_users(cid)
        return

    if d.startswith('ban_direct_'):
        if _admin_gate():
            try:
                tid = int(d[11:])
                if tid == OWNER_ID:
                    return
                data = load_data()
                bl = data.setdefault("banned_users", [])
                if tid not in bl:
                    bl.append(tid)
                    save_data(data)
                    safe_send(cid, f"🚫 <code>{tid}</code> banned!")
                else:
                    safe_send(cid, "⚠️ Already banned.")
            except ValueError:
                pass
        return

    if d == 'set_watermark':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 💎 SET WATERMARK 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the new watermark text:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_set_watermark(m, cid))
        return

    if d == 'set_support':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 🔗 SET SUPPORT LINK 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the new support link:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_set_support(m, cid))
        return

    if d == 'set_welcome':
        if _admin_gate():
            safe_edit(cid,
                '━━━━━━━━━━━━━━━\n'
                '《 📝 SET WELCOME MESSAGE 》\n'
                '━━━━━━━━━━━━━━━\n\n'
                '📝 Send the new welcome message:',
                _cancel_mk(), mid)
            bot.register_next_step_handler_by_chat_id(cid, lambda m: process_set_welcome(m, cid))
        return

    if d == 'back_owner':
        if _admin_gate():
            show_owner_panel(cid, user_id=uid, msg_id=mid)
        return

    if d == 'back_settings':
        if _admin_gate():
            show_settings_menu(cid, user_id=uid, msg_id=mid)
        return

    if d == 'back_ban':
        if _admin_gate():
            show_ban_menu(cid, mid)
        return

    if d == 'back_forcejoin':
        if _admin_gate():
            show_force_join_settings(cid, mid)
        return

    if d == 'back_maintenance':
        if _admin_gate():
            show_maintenance_settings(cid, mid)
        return

    if d == 'back_users':
        if _admin_gate():
            show_users_list(cid, page=0, msg_id=mid)
        return
