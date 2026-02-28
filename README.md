> **Disclaimer:** This project is for educational and research purposes only. Use responsibly and in compliance with applicable laws and terms of service.

# Telegram AI Bot

> **Talk to your private AI from your phone. No data touches any cloud. Free forever.**

Connect your locally-hosted AI to Telegram in under 30 minutes. Send a message from your phone, get an answer from your own AI running on your own hardware. End-to-end private.

## How It Works

```
Your Phone  ──→  Telegram (encrypted)  ──→  Your Laptop (local AI)
            ←──                         ←──
```

Your conversations go: Phone → Telegram → Your Machine → Local AI → back to you.
**Nothing stored on corporate servers. Nothing training someone else's model.**

## Quick Start

```bash
git clone https://github.com/Zombie760/telegram-ai-bot.git
cd telegram-ai-bot
pip install -r requirements.txt  # or: npm install
cp .env.example .env
# Add your Telegram bot token
python3 src/bot.py  # or: node src/bot.js
```

### Create Your Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`, pick a name and username
3. Save the token — that's all you need

## Features

- Python and Node.js implementations included
- Works with any OpenAI-compatible server (LM Studio, Ollama, vLLM)
- Conversation history per user
- Auto-chunking for long responses
- Health checks for model server

## Prerequisites

- Local AI running ([Quick Start](https://github.com/Zombie760/private-ai-quickstart))
- Telegram account
- Python 3.8+ or Node.js 18+

## Want More?

- [Automate 9 bots](https://github.com/Zombie760/ai-automation-stack) — run a full business on autopilot
- [Full course](https://github.com/Zombie760/ai-empire-course) — from zero to 9 agents in 48 hours

## Links

- [Website](https://Zombie760.github.io) | [Demo Bot](https://t.me/moneymakingmitch1904_bot) | [Twitter/X](https://x.com/lyfer1904)

---

*Your data. Your machine. Your rules.*
