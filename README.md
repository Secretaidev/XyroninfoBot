# 🔱 Xyron Info Bot

Advanced Telegram User Information Bot with native picker buttons, MongoDB storage, and full admin panel.

## ✨ Features

- 👤 **User Info** — ID, DC location, premium, registration date, badges
- 🤖 **Bot Info** — Capabilities, inline mode, web app support
- 📢 **Channel Info** — Members, protected content, linked chats
- 👥 **Group Info** — Permissions, slow mode, anti-spam, hidden members
- 💬 **Forum Info** — Topic groups with full details
- 📅 **Registration Estimation** — 200+ data points from Aug 2013 to Apr 2028
- 📄 **JSON Export** — Download any profile as a JSON file
- 🏓 **Ping** — Real-time bot latency and uptime
- 🎨 **Colorful Buttons** — Premium styled buttons
- 📋 **Native Pickers** — Telegram's built-in user/chat selector

## 💾 Database

Uses **MongoDB** for permanent, reliable storage that never loses data.

## 👑 Admin Panel

- 📊 Live statistics with ping & uptime
- 📣 Broadcast with progress bar
- 🛡️ Maintenance mode toggle
- 📢 Force join channel management
- 🚫 Ban/Unban system
- 👮 Admin management (owner-only)
- 👥 Paginated user list with export
- 📈 Top lookup leaderboard
- 💎 Watermark, support link, welcome message

## 🚀 Setup

1. Clone this repository
2. Create `.env` file:
```
BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_id
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/xyron_info_bot
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run:
```bash
python bot.py
```

## 🍃 MongoDB Setup (Free)

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster (M0 — FREE forever)
3. Create a database user with password
4. Whitelist IP: `0.0.0.0/0` (allow all)
5. Get connection string → paste in `.env` as `MONGO_URI`

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Help & commands |
| `/id` | Get your Telegram ID |
| `/ping` | Check bot speed |
| `/about` | About this bot |
| `/json` | Export info as JSON |

## 📁 Structure

```
├── bot.py              # Entry point
├── config.py           # Configuration + MongoDB URI
├── database.py         # MongoDB storage with caching
├── buttons.py          # Colorful button system
├── utils.py            # 50+ language names, DC map, helpers
├── registration.py     # 200+ milestone registration estimator
├── handlers.py         # Central routing + native pickers
├── info_user.py        # User info extractor
├── info_bot.py         # Bot info extractor
├── info_channel.py     # Channel info extractor
├── info_group.py       # Group info extractor
├── info_forum.py       # Forum info extractor
├── owner_panel.py      # Owner panel + settings
├── maintenance.py      # Maintenance mode
├── force_join.py       # Force join system
├── ban_system.py       # Ban management
├── admin_manager.py    # Admin management
├── broadcast.py        # Broadcast system
├── user_manager.py     # User list & stats
├── server.py           # Health check server
├── requirements.txt    # Dependencies
├── Procfile            # Process file
└── render.yaml         # Render config
```
