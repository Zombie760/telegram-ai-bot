> **Disclaimer:** This project is for educational and research purposes only. Use responsibly and in compliance with applicable laws and terms of service.

# Telegram AI Bot

> **Connect your locally-hosted AI to Telegram. Private. Fast. Free.**

Talk to your private AI from your phone via Telegram. No data touches any cloud server. Built for people who value their privacy.

## Features

- Direct connection between Telegram and your local AI model
- Supports text conversations, document analysis, and task automation
- Zero data sent to third parties
- Works with any OpenAI-compatible local server (LM Studio, Ollama, vLLM)
- Runs 24/7 on minimal hardware

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Your Phone  │────▶│  Telegram API    │────▶│  Your Laptop    │
│  (Telegram)  │◀────│  (encrypted)     │◀────│  (local AI)     │
└─────────────┘     └──────────────────┘     └─────────────────┘
                                                    │
                                              ┌─────┴─────┐
                                              │ LM Studio  │
                                              │ localhost   │
                                              │ :1234       │
                                              └───────────┘
```

Your conversations go: Phone → Telegram → Your Machine → Local AI → back to you.
**Nothing stored on corporate servers. Nothing training someone else's model.**

## Prerequisites

1. A running local AI server ([Quick Start Guide](https://github.com/Zombie760/private-ai-quickstart))
2. A Telegram account
3. Python 3.8+ or Node.js 18+

## Setup

### 1. Create Your Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name and username
4. Save the bot token (looks like `123456789:ABCdefGhIjKlMnOpQrStUvWxYz`)

### 2. Install Dependencies

```bash
# Python
pip install python-telegram-bot requests

# OR Node.js
npm install node-telegram-bot-api axios
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your bot token and model settings
```

```env
# .env.example
TELEGRAM_BOT_TOKEN=your_bot_token_here
LM_STUDIO_URL=http://localhost:1234/v1
MODEL_NAME=your-model-name
MAX_TOKENS=2048
TEMPERATURE=0.7
```

### 4. Run

```bash
# Python
python3 bot.py

# OR Node.js
node bot.js
```

### 5. Test

Open Telegram, find your bot, and send a message. Your local AI responds.

## Example Bot (Python)

```python
"""
Minimal Telegram bot connected to a local AI model.
No data leaves your machine except the Telegram message delivery.
"""
import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

LM_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
MODEL = os.getenv("MODEL_NAME", "local-model")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    # Send to your LOCAL AI — nothing goes to the cloud
    response = requests.post(f"{LM_URL}/chat/completions", json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful private AI assistant."},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    })

    ai_reply = response.json()["choices"][0]["message"]["content"]
    await update.message.reply_text(ai_reply)

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot running — your AI is private and local.")
    app.run_polling()

if __name__ == "__main__":
    main()
```

## Example Bot (Node.js)

```javascript
/**
 * Minimal Telegram bot connected to a local AI model.
 * Zero data sent to Big Tech.
 */
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const LM_URL = process.env.LM_STUDIO_URL || 'http://localhost:1234/v1';
const MODEL = process.env.MODEL_NAME || 'local-model';
const bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { polling: true });

bot.on('message', async (msg) => {
  if (!msg.text) return;

  const response = await axios.post(`${LM_URL}/chat/completions`, {
    model: MODEL,
    messages: [
      { role: 'system', content: 'You are a helpful private AI assistant.' },
      { role: 'user', content: msg.text }
    ],
    temperature: 0.7,
    max_tokens: 2048
  });

  const aiReply = response.data.choices[0].message.content;
  bot.sendMessage(msg.chat.id, aiReply);
});

console.log('Bot running — your AI is private and local.');
```

## Advanced: Multi-Bot Setup

Want to run multiple specialized bots? See the [AI Automation Stack](https://github.com/Zombie760/ai-automation-stack) for running 9 bots simultaneously.

## Security Notes

- Never commit your `.env` file or bot token to git
- Use `.gitignore` to exclude sensitive files
- The bot token is the only credential needed — your AI runs locally
- All conversation data stays on your hardware

## Project

Built by **SGKx1904** — 9 private AI bots running on a single laptop.

- [Website](https://Zombie760.github.io)
- [Live Demo Bot](https://t.me/moneymakingmitch1904_bot)
- [Quick Start](https://github.com/Zombie760/private-ai-quickstart)
- [Full Course](https://github.com/Zombie760/ai-empire-course)

---

*AI For The Rest of Us. Your data. Your machine. Your rules.*
