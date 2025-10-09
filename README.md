# 🤖 Auto Filter Bot v7
<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Pyrogram-v2.x-brightgreen?style=for-the-badge&logo=telegram" />
  <img src="https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb" />
  <img src="https://img.shields.io/github/license/muzxfir/Auto-Filter-v7?style=for-the-badge" />
  <img src="https://img.shields.io/github/stars/muzxfir/Auto-Filter-v7?style=for-the-badge" />
</p>

**Smart • Fast • Reliable**  
Automatically filter, index, and deliver files from your Telegram channels.

---

## 🌟 Overview
**Auto Filter v7** is a next-generation Telegram bot for automated media filtering, indexing, and delivery.  
It supports inline search, IMDb integration, admin tools, and multi-channel management — built for speed and simplicity.

---

## ⚡ Features

### Basic Features
- 🔍 Auto Filter – Instantly responds to user queries  
- 🧩 Manual Filter – Add or edit keyword-based replies  
- 🎬 IMDb / TMDB Info – Movie details with posters  
- 📦 Channel Indexing – Auto index files from channels  
- 💬 Inline Search – Use `@BotName query` anywhere  
- 🧠 Smart Spell Fix – Detects and corrects user typos  
- 🪄 Deep Link Support – Access via `/start` links  
- 👑 Admin Controls – Ban/unban, broadcast, logs  
- 📊 Stats Dashboard – Users, groups, DB usage  
- 🖼️ Random Start Pics – Custom Telegraph images  
- 💾 File Store Channel – Auto-manage files

### 🧩 Advanced / Pro Features

**User Features**  
- Smart Search across multiple indexed channels  
- Multiple file results neatly formatted  
- Instant deep-links for quick file download  
- Auto captions with file name, size & type  
- Interactive inline buttons for actions  
- Optional URL shortener integration

**Admin Tools**  
- Broadcast to all users  
- Ban/unban users instantly  
- View full usage statistics  
- Force Subscribe support  
- Auto index new channel files  
- Logs channel for debugging  
- Anti-flood & auto-restart system

**Database & Performance**  
- MongoDB with separate collections  
- Query caching for faster responses  
- Auto cleanup of inactive data  

**IMDb & TMDB Enhancements**  
- Poster mode with cast & rating  
- Trailer button for YouTube  
- Genre tagging & hybrid search  

**Developer Friendly**  
- Modular plugin system  
- Debug logging  
- Multi-session support  
- Localization-ready  
- Auto-update alerts  

**Premium Optional Add-Ons**  
- Paid Content Mode — restrict access to VIP users  
- Encrypted File Sharing — secure delivery  
- AI-Search Assistant — natural-language file search  
- Theme System — customize bot messages and emojis

---

## ⚙️ Configuration

Set these environment variables:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot Token from [@BotFather](https://t.me/BotFather) |
| `API_ID / API_HASH` | Get from [my.telegram.org](https://my.telegram.org) |
| `CHANNELS` | List of channels to index |
| `ADMINS` | Admin user IDs |
| `DATABASE_URI` | MongoDB connection string |
| `DATABASE_NAME` | Database name |
| `LOG_CHANNEL` | Log channel ID |
| `FILE_STORE_CHANNEL` | Optional file storage channel |
| `PICS` | Telegraph images for `/start` |
| `SHORT_URL / SHORT_API` | Optional URL shortener |
| `F_SUB` | Force-subscribe channel (optional) |

---

## 🚀 Deployment

### ☁️ Deploy to Koyeb
[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy)

### 💻 Manual / VPS Deployment
```bash
git clone https://github.com/muzxfir/Auto-Filter-v7
cd Auto-Filter-v7
pip install -r requirements.txt
python3 bot.py
