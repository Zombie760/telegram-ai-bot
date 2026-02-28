#!/usr/bin/env python3
"""
Telegram AI Bot — connects a local model to Telegram.
For educational purposes only.

Architecture:
  Telegram API <-> This bot <-> Local AI (LM Studio / Ollama / vLLM)

No data is stored or forwarded to third-party services.
"""

import os
import json
import logging
import asyncio
from typing import Optional
from dataclasses import dataclass
from urllib.request import urlopen, Request
from urllib.error import URLError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("telegram-ai")

try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ContextTypes,
        filters,
    )
except ImportError:
    log.error("Install: pip install python-telegram-bot")
    raise SystemExit(1)


@dataclass
class BotConfig:
    telegram_token: str
    model_url: str = "http://127.0.0.1:1234/v1"
    model_name: str = "local-model"
    max_tokens: int = 2048
    temperature: float = 0.7
    system_prompt: str = "You are a helpful AI assistant. Be concise and accurate."
    max_history: int = 10

    @classmethod
    def from_env(cls) -> "BotConfig":
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        return cls(
            telegram_token=token,
            model_url=os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1"),
            model_name=os.getenv("MODEL_NAME", "local-model"),
            max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            system_prompt=os.getenv("SYSTEM_PROMPT", cls.system_prompt),
            max_history=int(os.getenv("MAX_HISTORY", "10")),
        )


class ConversationManager:
    """Manages per-user conversation history in memory only."""

    def __init__(self, max_history: int = 10):
        self._history: dict[int, list[dict]] = {}
        self._max = max_history

    def get(self, user_id: int) -> list[dict]:
        return self._history.get(user_id, [])

    def append(self, user_id: int, role: str, content: str):
        if user_id not in self._history:
            self._history[user_id] = []
        self._history[user_id].append({"role": role, "content": content})
        if len(self._history[user_id]) > self._max * 2:
            self._history[user_id] = self._history[user_id][-self._max * 2:]

    def clear(self, user_id: int):
        self._history.pop(user_id, None)

    @property
    def active_sessions(self) -> int:
        return len(self._history)


class ModelClient:
    """Sends requests to the local model server."""

    def __init__(self, config: BotConfig):
        self.config = config

    def complete(self, messages: list[dict]) -> str:
        payload = json.dumps({
            "model": self.config.model_name,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False,
        }).encode()

        req = Request(
            f"{self.config.model_url}/chat/completions",
            data=payload,
            method="POST",
        )
        req.add_header("Content-Type", "application/json")

        try:
            with urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                return data["choices"][0]["message"]["content"]
        except URLError as e:
            log.error("Model server unreachable: %s", e)
            return "Model server is offline. Please check LM Studio is running."
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            log.error("Invalid model response: %s", e)
            return "Received an invalid response from the model."

    def health_check(self) -> bool:
        try:
            req = Request(f"{self.config.model_url}/models", method="GET")
            with urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False


def create_bot(config: BotConfig) -> Application:
    """Build the Telegram bot application."""
    conversations = ConversationManager(config.max_history)
    model = ModelClient(config)

    async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Private AI assistant online.\n\n"
            "Send any message to start a conversation.\n"
            "Your data stays on this machine.\n\n"
            "/clear — reset conversation\n"
            "/status — check system health"
        )

    async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        conversations.clear(update.effective_user.id)
        await update.message.reply_text("Conversation cleared.")

    async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        healthy = model.health_check()
        status = "online" if healthy else "offline"
        await update.message.reply_text(
            f"Model server: {status}\n"
            f"Active sessions: {conversations.active_sessions}\n"
            f"Model: {config.model_name}\n"
            f"Max tokens: {config.max_tokens}"
        )

    async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_text = update.message.text

        if not user_text:
            return

        conversations.append(user_id, "user", user_text)

        messages = [{"role": "system", "content": config.system_prompt}]
        messages.extend(conversations.get(user_id))

        await update.message.chat.send_action("typing")

        reply = model.complete(messages)
        conversations.append(user_id, "assistant", reply)

        # Telegram message limit is 4096 chars
        if len(reply) > 4000:
            for i in range(0, len(reply), 4000):
                await update.message.reply_text(reply[i:i + 4000])
        else:
            await update.message.reply_text(reply)

    app = Application.builder().token(config.telegram_token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app


def main():
    config = BotConfig.from_env()

    log.info("Starting Telegram AI bot")
    log.info("Model server: %s", config.model_url)

    model = ModelClient(config)
    if model.health_check():
        log.info("Model server healthy")
    else:
        log.warning("Model server not reachable — will retry on first message")

    app = create_bot(config)
    log.info("Bot running — polling for messages")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
