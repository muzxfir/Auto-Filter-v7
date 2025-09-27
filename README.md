<p align="center">
  <img src="https://files.catbox.moe/wllfrk.png">
</p>
<h1 align="center">
  ᴀᴜᴛᴏ-ꜰɪʟᴛᴇʀ-ᴠ7 ʙᴏᴛ
</h1>

---

![Repo Views](https://komarev.com/ghpvc/?username=TGEBOTZ&repo=Auto-Filter-v7&label=Views&color=blue&style=for-the-badge)

---

## ✨ Features

- 🔎 **Auto Filter** – Automatically filter content  
- 📝 **Manual Filter** – Add and manage custom filters  
- 🎬 **IMDB Search** – Get movie & TV details from IMDB  
- ⚡ **Inline Search** – Fast inline mode content search  
- 🖼 **Random Pics** – Send random images  
- 📂 **Indexing System** – Index files from channels  
- 📊 **Stats Dashboard** – Track users, chats & database  
- 🛡 **Admin Tools** – Logs, ban/unban, broadcast, disable/enable  
- 🔐 **User Management** – IDs, info, connect/disconnect  
- 🗂 **File Store** – Store & share files easily  
- ✅ **Spelling Check** – Smart spelling correction for queries  

---

## 🔧 Configuration

Set the following environment variables:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot API Token (from [@BotFather](https://t.me/BotFather)) |
| `API_ID` | Telegram API ID ([my.telegram.org](https://my.telegram.org)) |
| `API_HASH` | Telegram API Hash ([my.telegram.org](https://my.telegram.org)) |
| `CHANNELS` | Space-separated list of channel/group IDs or usernames |
| `ADMINS` | Space-separated list of admin user IDs |
| `DATABASE_URI` | MongoDB connection URI |
| `DATABASE_NAME` | MongoDB database name |
| `LOG_CHANNEL` | Channel ID for error logs |

**Optional:**

- `PICS` – Telegraph image URLs for `/start`  
- `FILE_STORE_CHANNEL` – Channel(s) for file storage  

---

## 🚀 Deployment

### 🔹 Deploy to Koyeb
Click below to deploy instantly on **Koyeb**:

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/TGEBOTZ/Auto-Filter-v7&branch=main&name=auto-filter-v7)

After clicking, just set your **environment variables** (`BOT_TOKEN`, `API_ID`, `API_HASH`, `DATABASE_URI`, `DATABASE_NAME`, `LOG_CHANNEL`, `CHANNELS`, `ADMINS`, etc.) and press **Deploy** 🎉
