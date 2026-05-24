<div align="center">

<img src="tgbot/start_image.png" width="200" alt="Devil X String Logo"/>

# 🤖 Devil X String Bot

**A powerful Telegram String Session Generator Bot**

Generate Pyrogram & Telethon string sessions with auto-join, force-join protection, and Supabase storage.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0.106-green?style=for-the-badge)](https://pyrogram.org)
[![Telethon](https://img.shields.io/badge/Telethon-1.36-blue?style=for-the-badge)](https://telethon.dev)
[![Supabase](https://img.shields.io/badge/Supabase-Database-brightgreen?style=for-the-badge&logo=supabase)](https://supabase.com)

---

**[✨ Features](#-features) • [📋 Prerequisites](#-prerequisites-get-these-first) • [🔧 Configuration](#-configuration) • [🚀 Deploy](#-deployment) • [📌 Commands](#-commands) • [🛠️ Troubleshooting](#-troubleshooting)**

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔑 **Pyrogram Sessions** | Generate Pyrogram string sessions instantly |
| 📡 **Telethon Sessions** | Generate Telethon string sessions instantly |
| 🤝 **Auto Join** | Users automatically join your support channel & group after generation |
| 🔒 **Force Join** | Block users from generating until they join your channels |
| 💾 **Supabase Storage** | All sessions stored securely in Supabase PostgreSQL |
| 📢 **Broadcast** | Owner-only broadcast with live progress bar & stats |
| 📊 **Admin Panel** | User count, session stats, ban/unban management |
| 🛡️ **2FA Support** | Handles two-factor authentication seamlessly |

---

## 📋 Prerequisites (Get These First)

You need **4 things** before deploying. Get them all now:

### 1. 🤖 Bot Token
1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**
2. Send `/newbot`
3. Enter a name for your bot (e.g. `Devil X String`)
4. Enter a username ending in `bot` (e.g. `devilxstring_bot`)
5. Copy the token it gives you — looks like: `6342971158:AAEzAvVgP-9Hak...`

### 2. 🔑 API ID & API Hash
1. Go to **[my.telegram.org](https://my.telegram.org)**
2. Log in with your Telegram phone number
3. Click **"API development tools"**
4. Fill in the form (App title: anything, Short name: anything)
5. Click **"Create application"**
6. Copy your **App api_id** (numbers) and **App api_hash** (letters+numbers)

### 3. 🗄️ Supabase Database

**Step 1 — Create a free account:**
1. Go to **[supabase.com](https://supabase.com)** → Click **"Start your project"**
2. Sign up with GitHub or email
3. Click **"New project"**
4. Fill in: Project name (anything), Database Password (save this!), Region (pick closest to you)
5. Click **"Create new project"** — wait ~2 minutes for it to set up

**Step 2 — Get your credentials:**
1. In your project dashboard, click **"Settings"** (gear icon, left sidebar)
2. Click **"API"**
3. Copy **"Project URL"** → this is your `SUPABASE_URL`
4. Under "Project API keys", copy **"service_role"** key → this is your `SUPABASE_KEY`

**Step 3 — Create the sessions table:**
1. In your project dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**
3. Paste this SQL and click **"Run"**:

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username TEXT DEFAULT '',
    session_string TEXT NOT NULL,
    session_type TEXT NOT NULL CHECK (session_type IN ('pyrogram', 'telethon')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_type ON sessions(user_id, session_type);
```

4. You should see **"Success. No rows returned"** — the table is ready ✅

### 4. 🆔 Your Telegram User ID
1. Open Telegram and search for **[@userinfobot](https://t.me/userinfobot)**
2. Send `/start`
3. It will reply with your numeric ID (e.g. `123456789`)
4. This goes into `config.py` as `OWNER_ID`

---

## 🔧 Configuration

After cloning the repo, open `tgbot/config.py` and update these values:

```python
# Your Telegram user ID (from @userinfobot)
OWNER_ID = 123456789

# Channels/groups users must join and auto-join after generating a session
# Use the @username without the @ symbol
AUTO_JOIN_CHATS = [
    "your_channel_username",   # e.g. "devilbots971"
    "your_group_username",     # e.g. "devilbotsupport"
]

# Your bot's display name (shown in welcome message)
BOT_NAME = "Devil X String"
```

> ⚠️ **Important:** Add your bot as a **member or admin** of both your channel and group. Without this, the force-join membership check will not work.

---

## 🚀 Deployment

Choose your preferred platform below. Each section has complete step-by-step instructions.

---

<details>
<summary><h3>📱 Termux (Android) — Click to expand</h3></summary>

Termux lets you run the bot directly on your Android phone for free.

**Step 1 — Install Termux:**
- Download **Termux** from [F-Droid](https://f-droid.org/packages/com.termux/) (NOT from Play Store — Play Store version is outdated)

**Step 2 — Set up Termux:**
```bash
# Update packages
pkg update && pkg upgrade -y

# Install required tools
pkg install python git nano -y
```

**Step 3 — Clone the bot:**
```bash
git clone https://github.com/yourusername/devil-x-string
cd devil-x-string/tgbot
```

**Step 4 — Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Step 5 — Configure the bot:**
```bash
# Copy the example env file
cp .env.example .env

# Open it and fill in your values
nano .env
```

In the nano editor, fill in:
```env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here
```
Press `Ctrl+X` → `Y` → `Enter` to save.

**Step 6 — Edit config.py:**
```bash
nano config.py
# Update OWNER_ID and AUTO_JOIN_CHATS
```

**Step 7 — Run the bot:**
```bash
python3 bot.py
```

**Keep bot running when phone screen is off:**
```bash
# Install termux-services
pkg install termux-services -y

# OR simply use nohup
nohup python3 bot.py &

# To stop it later:
pkill -f bot.py
```

**To run in background and check logs:**
```bash
# Start in background
nohup python3 bot.py > bot.log 2>&1 &

# Check logs anytime
tail -f bot.log

# Check if running
ps aux | grep bot.py
```

</details>

---

<details>
<summary><h3>🚂 Railway — Click to expand</h3></summary>

Railway gives you $5 free credit per month — enough to run a bot continuously.

**Step 1 — Prepare your GitHub repo:**
1. Fork this repository on GitHub (click the Fork button top-right)
2. In your fork, open `tgbot/config.py`
3. Update `OWNER_ID` and `AUTO_JOIN_CHATS` with your values
4. Commit the changes

**Step 2 — Create a Railway account:**
1. Go to **[railway.app](https://railway.app)**
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub

**Step 3 — Create a new project:**
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your forked repository
4. Railway will detect the project automatically

**Step 4 — Configure the service:**
1. Click on your newly created service
2. Go to the **"Settings"** tab
3. Under **"Root Directory"**, enter: `tgbot`
4. Under **"Start Command"**, enter: `python3 bot.py`
5. Click **"Save"**

**Step 5 — Add environment variables:**
1. Go to the **"Variables"** tab
2. Click **"+ New Variable"** and add each one:

| Variable | Value |
|---|---|
| `BOT_TOKEN` | Your bot token from BotFather |
| `API_ID` | Your API ID from my.telegram.org |
| `API_HASH` | Your API Hash from my.telegram.org |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase service role key |

**Step 6 — Deploy:**
1. Go to the **"Deployments"** tab
2. Click **"Deploy Now"** (or it may deploy automatically)
3. Click on the active deployment to see logs
4. You should see `🤖 String Session Bot starting...` in the logs ✅

**To redeploy after code changes:**
- Push to your GitHub repo — Railway auto-deploys on every push

</details>

---

<details>
<summary><h3>🎨 Render — Click to expand</h3></summary>

Render offers a free tier for background workers (may spin down after inactivity on free plan).

**Step 1 — Prepare your GitHub repo:**
1. Fork this repository on GitHub
2. Update `tgbot/config.py` with your `OWNER_ID` and `AUTO_JOIN_CHATS`
3. Commit the changes

**Step 2 — Create a Render account:**
1. Go to **[render.com](https://render.com)**
2. Click **"Get Started for Free"**
3. Sign up with GitHub

**Step 3 — Create a Background Worker:**
1. From your Render dashboard, click **"New +"**
2. Select **"Background Worker"**
3. Click **"Connect a repository"**
4. Find and select your forked repository
5. Click **"Connect"**

**Step 4 — Configure the worker:**

Fill in these settings:

| Setting | Value |
|---|---|
| **Name** | `devil-x-string-bot` (or anything you like) |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Root Directory** | `tgbot` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python3 bot.py` |

**Step 5 — Add environment variables:**
1. Scroll down to the **"Environment Variables"** section
2. Click **"Add Environment Variable"** for each:

| Key | Value |
|---|---|
| `BOT_TOKEN` | Your bot token |
| `API_ID` | Your API ID |
| `API_HASH` | Your API Hash |
| `SUPABASE_URL` | Your Supabase URL |
| `SUPABASE_KEY` | Your Supabase key |

**Step 6 — Create the service:**
1. Click **"Create Background Worker"**
2. Render will build and deploy automatically
3. Click **"Logs"** to see the output
4. Wait for `🤖 String Session Bot starting...` ✅

**Note:** On Render's free plan, background workers run 24/7 for 750 hours/month.

</details>

---

<details>
<summary><h3>💜 Heroku — Click to expand</h3></summary>

Heroku requires a paid plan (Eco Dynos at ~$5/month) since they removed the free tier.

**Step 1 — Install required tools:**
```bash
# Install Git (if not already installed)
# Windows: https://git-scm.com/download/win
# Mac: brew install git
# Linux: sudo apt install git -y

# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew tap heroku/brew && brew install heroku
# Linux:
curl https://cli-assets.heroku.com/install.sh | sh
```

**Step 2 — Log in to Heroku:**
```bash
heroku login
# A browser window will open — log in there
```

**Step 3 — Clone and prepare the bot:**
```bash
git clone https://github.com/yourusername/devil-x-string
cd devil-x-string/tgbot
```

**Step 4 — Edit config.py with your values:**
```bash
nano config.py
# Update OWNER_ID and AUTO_JOIN_CHATS
```

**Step 5 — Create the Heroku app:**
```bash
heroku create your-bot-name
# Replace "your-bot-name" with a unique name (e.g. devil-x-string-123)
```

**Step 6 — Set all environment variables:**
```bash
heroku config:set BOT_TOKEN="your_bot_token_here"
heroku config:set API_ID="your_api_id_here"
heroku config:set API_HASH="your_api_hash_here"
heroku config:set SUPABASE_URL="https://your-project.supabase.co"
heroku config:set SUPABASE_KEY="your-service-role-key-here"

# Verify they are set
heroku config
```

**Step 7 — Initialize Git and deploy:**
```bash
git init
git add .
git commit -m "Deploy Devil X String Bot"
heroku git:remote -a your-bot-name
git push heroku main
```

**Step 8 — Scale the worker dyno:**
```bash
# Heroku bots run as "worker" (not "web")
heroku ps:scale worker=1

# Verify it's running
heroku ps

# Check logs
heroku logs --tail
```

You should see `🤖 String Session Bot starting...` in the logs ✅

**To update the bot after code changes:**
```bash
git add .
git commit -m "Update bot"
git push heroku main
```

</details>

---

<details>
<summary><h3>🐳 Docker — Click to expand</h3></summary>

Docker works on any machine (Windows, Mac, Linux, VPS) that has Docker installed.

**Step 1 — Install Docker:**
- **Windows/Mac:** Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
```

**Step 2 — Clone the repo:**
```bash
git clone https://github.com/yourusername/devil-x-string
cd devil-x-string/tgbot
```

**Step 3 — Edit config.py:**
```bash
nano config.py
# Update OWNER_ID and AUTO_JOIN_CHATS
```

**Step 4 — Create your .env file:**
```bash
cp .env.example .env
nano .env
```
Fill in all 5 values and save.

**Step 5 — Build the Docker image:**
```bash
docker build -t devil-x-string .
```

**Step 6 — Run the container:**
```bash
# Option A: Using .env file (recommended)
docker run -d \
  --env-file .env \
  --name devil-x-string \
  --restart always \
  devil-x-string

# Option B: Pass variables manually
docker run -d \
  -e BOT_TOKEN="your_token" \
  -e API_ID="your_api_id" \
  -e API_HASH="your_api_hash" \
  -e SUPABASE_URL="your_supabase_url" \
  -e SUPABASE_KEY="your_supabase_key" \
  --name devil-x-string \
  --restart always \
  devil-x-string
```

The `--restart always` flag means Docker will automatically restart the bot if it crashes or the server reboots.

**Useful Docker commands:**
```bash
# View live logs
docker logs -f devil-x-string

# Stop the bot
docker stop devil-x-string

# Start again
docker start devil-x-string

# Restart
docker restart devil-x-string

# Remove container (to redeploy)
docker stop devil-x-string && docker rm devil-x-string

# See running containers
docker ps
```

**To update after code changes:**
```bash
docker stop devil-x-string
docker rm devil-x-string
docker build -t devil-x-string .
docker run -d --env-file .env --name devil-x-string --restart always devil-x-string
```

</details>

---

<details>
<summary><h3>🐧 VPS / Linux Server (Ubuntu) — Click to expand</h3></summary>

Best for 24/7 reliability. Works on any Ubuntu/Debian VPS from providers like DigitalOcean, Contabo, Hetzner, Linode, etc.

**Step 1 — Connect to your VPS:**
```bash
ssh root@your_server_ip
# Enter your password when prompted
```

**Step 2 — Install system dependencies:**
```bash
# Update package lists
apt update && apt upgrade -y

# Install Python, pip, git
apt install python3 python3-pip git nano screen -y

# Verify Python version (should be 3.10+)
python3 --version
```

**Step 3 — Clone the bot:**
```bash
cd /root
git clone https://github.com/yourusername/devil-x-string
cd devil-x-string/tgbot
```

**Step 4 — Install Python dependencies:**
```bash
pip3 install -r requirements.txt
```

**Step 5 — Configure the bot:**
```bash
# Copy env file
cp .env.example .env

# Edit env file
nano .env
```
Fill in all 5 values. Press `Ctrl+X` → `Y` → `Enter` to save.

```bash
# Edit config.py
nano config.py
# Update OWNER_ID and AUTO_JOIN_CHATS, then save
```

**Step 6 — Test the bot:**
```bash
python3 bot.py
# You should see: 🤖 String Session Bot starting...
# Press Ctrl+C to stop after confirming it works
```

**Step 7 — Run permanently with Screen:**
```bash
# Start a new screen session named "devilbot"
screen -S devilbot

# Run the bot inside the screen
python3 bot.py

# Detach from screen (bot keeps running)
# Press: Ctrl+A then D

# Later, to check on the bot:
screen -r devilbot

# List all screens
screen -ls
```

**Step 7 (Alternative) — Run permanently with Systemd (recommended):**

Systemd automatically restarts the bot if it crashes and starts it on server boot.

```bash
# Create the service file
nano /etc/systemd/system/devilbot.service
```

Paste this content:
```ini
[Unit]
Description=Devil X String Telegram Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/devil-x-string/tgbot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save with `Ctrl+X` → `Y` → `Enter`.

```bash
# Reload systemd to register the new service
systemctl daemon-reload

# Enable the service (auto-start on reboot)
systemctl enable devilbot

# Start the bot now
systemctl start devilbot

# Check status
systemctl status devilbot
```

You should see `Active: active (running)` ✅

**Useful systemd commands:**
```bash
# View live logs
journalctl -u devilbot -f

# Restart the bot (after code changes)
systemctl restart devilbot

# Stop the bot
systemctl stop devilbot

# Disable auto-start
systemctl disable devilbot
```

**To update the bot:**
```bash
cd /root/devil-x-string
git pull
cd tgbot
pip3 install -r requirements.txt
systemctl restart devilbot
```

</details>

---

<details>
<summary><h3>☁️ Koyeb — Click to expand</h3></summary>

Koyeb offers a generous free tier with no credit card required.

**Step 1 — Create account:**
1. Go to **[koyeb.com](https://www.koyeb.com)**
2. Sign up for free (no credit card needed)

**Step 2 — Prepare your repo:**
1. Fork this repo on GitHub
2. Update `tgbot/config.py` with your values
3. Commit changes

**Step 3 — Create a new service:**
1. From Koyeb dashboard → **"Create Service"**
2. Select **"GitHub"**
3. Connect your GitHub account and select your forked repo
4. Set **Branch**: `main`

**Step 4 — Configure build:**

| Setting | Value |
|---|---|
| **Build command** | `pip install -r tgbot/requirements.txt` |
| **Run command** | `python3 tgbot/bot.py` |
| **Instance type** | Free (nano) |

**Step 5 — Add environment variables:**
Click **"Add variable"** for each:
- `BOT_TOKEN`, `API_ID`, `API_HASH`, `SUPABASE_URL`, `SUPABASE_KEY`

**Step 6 — Deploy:**
Click **"Deploy"** and watch the logs for `🤖 String Session Bot starting...` ✅

</details>

---

## 📌 Commands

### 👤 User Commands

| Command | Description |
|---|---|
| `/start` | Show welcome screen with menu |
| `/help` | Full guide on how to generate sessions |
| `/generate` | Choose session type (Pyrogram or Telethon) |
| `/mysessions` | View your previously generated sessions |
| `/cancel` | Cancel current operation and return to menu |

### 👑 Owner-Only Commands

| Command | Description |
|---|---|
| `/stats` | Full stats dashboard (users, sessions, types) |
| `/users` | List all users who have used the bot |
| `/userinfo <id>` | Detailed info + sessions for a specific user |
| `/broadcast` | Send a message to ALL users (with progress bar) |
| `/ban <id>` | Ban user and delete all their sessions |
| `/unban <id>` | Unban a user |

---

## 🗂️ Project Structure

```
tgbot/
├── bot.py              # Main bot — handlers and session flow
├── admin.py            # Owner-only admin commands & broadcast
├── config.py           # ← Edit this to configure your bot
├── database.py         # Supabase database helpers
├── helpers.py          # Auto-join channel logic (post-generation)
├── force_join.py       # Force-join membership checker (pre-generation)
├── keyboards.py        # Inline keyboard builders
├── messages.py         # All bot message text templates
├── pyrogram_gen.py     # Pyrogram session OTP + sign-in logic
├── telethon_gen.py     # Telethon session OTP + sign-in logic
├── start_image.png     # Bot welcome image
├── requirements.txt    # Python package dependencies
├── Procfile            # Heroku worker configuration
├── railway.toml        # Railway deployment configuration
├── render.yaml         # Render deployment configuration
├── Dockerfile          # Docker container configuration
├── .env.example        # Template for environment variables
├── .gitignore          # Files to exclude from Git
└── supabase_setup.sql  # SQL to create sessions table
```

---

## 🔐 Security Notes

- **Never share your string session** — it gives complete account access
- **Never commit `.env`** to GitHub — it's in `.gitignore` by default
- Use Supabase **service_role** key (not anon key) for full database access
- If a session is compromised: Telegram → Settings → Devices → Terminate session
- `OWNER_ID` in `config.py` is the only account that can run admin commands

---

## 🛠️ Troubleshooting

<details>
<summary><b>Bot doesn't start / crashes immediately</b></summary>

- Check all 5 environment variables are set correctly
- Verify `BOT_TOKEN` is valid — test by visiting `https://api.telegram.org/bot<TOKEN>/getMe`
- Make sure `API_ID` is a number only (no spaces)
- Ensure `SUPABASE_URL` starts with `https://`

</details>

<details>
<summary><b>Supabase error: "table sessions not found"</b></summary>

You haven't created the table yet. Run the SQL from the [Prerequisites](#-prerequisites-get-these-first) section in your Supabase SQL Editor.

</details>

<details>
<summary><b>Auto-join not working after session generation</b></summary>

- Make sure the usernames in `AUTO_JOIN_CHATS` are correct (without `@`)
- The channel/group must be public OR the bot must be a member
- Check bot logs for `[AutoJoin]` lines to see exact errors

</details>

<details>
<summary><b>Force-join check always passes (not blocking anyone)</b></summary>

Your bot needs to be a **member or admin** of both the channel and group to check user membership. Add your bot to both chats, then test again.

</details>

<details>
<summary><b>OTP not received / phone number invalid</b></summary>

- Include country code with `+` (e.g. `+919876543210`)
- If OTP doesn't arrive, check Telegram notifications — it's sent as a Telegram message, not SMS
- Wait 60 seconds and try again if rate limited

</details>

<details>
<summary><b>2FA password rejected</b></summary>

- Make sure Caps Lock is off
- Try the password you use on Telegram → Settings → Privacy and Security → Two-Step Verification

</details>

---

## 📦 Dependencies

```
pyrogram==2.0.106    — Telegram MTProto client (Pyrogram sessions)
TgCrypto==1.2.5      — Fast encryption for Pyrogram
telethon==1.36.0     — Telegram client (Telethon sessions)
supabase==2.15.2     — Supabase Python client
python-dotenv==1.0.1 — Load .env file automatically
```

---

## 👨‍💻 Developer & Support

<div align="center">

Made with ❤️ by **[@mrdevil12](https://t.me/mrdevil12)**

📢 **Channel:** [t.me/devilbots971](https://t.me/devilbots971)
💬 **Support Group:** [t.me/devilbotsupport](https://t.me/devilbotsupport)

---

⭐ **If this helped you, please star the repo!** ⭐

</div>
