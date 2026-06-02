# 🔱 Xyron Info Bot

Advanced Telegram User Information Bot with colorful buttons, modular architecture, and full admin panel.

## ✨ Features

- 👤 **User Info** — ID, DC location, premium status, registration date, bio, badges
- 🤖 **Bot Info** — Capabilities, inline mode, web app support
- 📢 **Channel Info** — Members, protected content, linked chats
- 👥 **Group Info** — Permissions, slow mode, anti-spam, hidden members
- 💬 **Forum Info** — Topic groups with full details
- 📅 **Registration Estimation** — 195+ data points from 2013 to 2025
- 📄 **JSON Export** — Download any profile as a JSON file
- 🏓 **Ping** — Real-time bot latency and uptime
- 🎨 **Colorful Buttons** — Premium UI with styled buttons

## 👑 Admin Panel

- 📊 Live statistics with ping & uptime
- 📣 Broadcast to all users with progress bar
- 🛡️ Maintenance mode toggle
- 📢 Force join channel management
- 🚫 Ban/Unban system
- 👮 Admin management (owner-only)
- 👥 Paginated user list with export
- 📈 Top lookup leaderboard
- 💎 Customizable watermark, support link, welcome message

## 🚀 Setup

1. Clone this repository
2. Create `.env` file:
```
BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_id
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run:
```bash
python bot.py
```

## 📦 Deploy to Render

- Push to GitHub
- Create new Web Service on Render
- Connect your repo
- Set environment variables: `BOT_TOKEN`, `OWNER_ID`
- Deploy!

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
├── config.py           # Configuration
├── database.py         # Thread-safe JSON storage
├── buttons.py          # Colorful button system
├── utils.py            # Utilities & helpers
├── registration.py     # Registration date estimation
├── handlers.py         # Central routing hub
├── info_user.py        # User info extractor
├── info_bot.py         # Bot info extractor
├── info_channel.py     # Channel info extractor
├── info_group.py       # Group info extractor
├── info_forum.py       # Forum info extractor
├── owner_panel.py      # Owner panel & settings
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
