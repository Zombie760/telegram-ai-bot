#!/usr/bin/env node
/**
 * Telegram AI Bot — Node.js implementation.
 * For educational purposes only.
 *
 * Connects a locally-hosted AI model to Telegram.
 * Zero data sent to cloud services.
 */

const TelegramBot = require("node-telegram-bot-api");
const http = require("http");

// ---- Configuration ----

const CONFIG = {
  token: process.env.TELEGRAM_BOT_TOKEN,
  modelUrl: process.env.LM_STUDIO_URL || "http://127.0.0.1:1234/v1",
  modelName: process.env.MODEL_NAME || "local-model",
  maxTokens: parseInt(process.env.MAX_TOKENS || "2048", 10),
  temperature: parseFloat(process.env.TEMPERATURE || "0.7"),
  systemPrompt:
    process.env.SYSTEM_PROMPT ||
    "You are a helpful AI assistant. Be concise and accurate.",
  maxHistory: parseInt(process.env.MAX_HISTORY || "10", 10),
};

if (!CONFIG.token) {
  console.error("TELEGRAM_BOT_TOKEN not set");
  process.exit(1);
}

// ---- Conversation Manager ----

class ConversationManager {
  constructor(maxHistory = 10) {
    this.history = new Map();
    this.maxHistory = maxHistory;
  }

  get(userId) {
    return this.history.get(userId) || [];
  }

  append(userId, role, content) {
    if (!this.history.has(userId)) {
      this.history.set(userId, []);
    }
    const hist = this.history.get(userId);
    hist.push({ role, content });
    if (hist.length > this.maxHistory * 2) {
      this.history.set(userId, hist.slice(-this.maxHistory * 2));
    }
  }

  clear(userId) {
    this.history.delete(userId);
  }

  get activeSessions() {
    return this.history.size;
  }
}

// ---- Model Client ----

function complete(messages) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${CONFIG.modelUrl}/chat/completions`);
    const payload = JSON.stringify({
      model: CONFIG.modelName,
      messages,
      temperature: CONFIG.temperature,
      max_tokens: CONFIG.maxTokens,
      stream: false,
    });

    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(payload),
      },
      timeout: 60000,
    };

    const req = http.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed.choices[0].message.content);
        } catch (e) {
          reject(new Error(`Invalid response: ${e.message}`));
        }
      });
    });

    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("Request timeout"));
    });

    req.write(payload);
    req.end();
  });
}

function healthCheck() {
  return new Promise((resolve) => {
    const url = new URL(`${CONFIG.modelUrl}/models`);
    const req = http.get(
      { hostname: url.hostname, port: url.port, path: url.pathname, timeout: 5000 },
      (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => resolve(res.statusCode === 200));
      }
    );
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

// ---- Bot ----

async function main() {
  const conversations = new ConversationManager(CONFIG.maxHistory);
  const bot = new TelegramBot(CONFIG.token, { polling: true });

  console.log(`[${ts()}] Bot starting — model: ${CONFIG.modelUrl}`);

  const healthy = await healthCheck();
  console.log(`[${ts()}] Model server: ${healthy ? "online" : "offline"}`);

  bot.onText(/\/start/, (msg) => {
    bot.sendMessage(
      msg.chat.id,
      "Private AI assistant online.\n\n" +
        "Send any message to start a conversation.\n" +
        "Your data stays on this machine.\n\n" +
        "/clear — reset conversation\n" +
        "/status — check system health"
    );
  });

  bot.onText(/\/clear/, (msg) => {
    conversations.clear(msg.from.id);
    bot.sendMessage(msg.chat.id, "Conversation cleared.");
  });

  bot.onText(/\/status/, async (msg) => {
    const ok = await healthCheck();
    bot.sendMessage(
      msg.chat.id,
      `Model server: ${ok ? "online" : "offline"}\n` +
        `Active sessions: ${conversations.activeSessions}\n` +
        `Model: ${CONFIG.modelName}\n` +
        `Max tokens: ${CONFIG.maxTokens}`
    );
  });

  bot.on("message", async (msg) => {
    if (!msg.text || msg.text.startsWith("/")) return;

    const userId = msg.from.id;
    conversations.append(userId, "user", msg.text);

    const messages = [
      { role: "system", content: CONFIG.systemPrompt },
      ...conversations.get(userId),
    ];

    bot.sendChatAction(msg.chat.id, "typing");

    try {
      const reply = await complete(messages);
      conversations.append(userId, "assistant", reply);

      if (reply.length > 4000) {
        for (let i = 0; i < reply.length; i += 4000) {
          await bot.sendMessage(msg.chat.id, reply.slice(i, i + 4000));
        }
      } else {
        await bot.sendMessage(msg.chat.id, reply);
      }
    } catch (e) {
      console.error(`[${ts()}] Error: ${e.message}`);
      bot.sendMessage(msg.chat.id, "Model server unavailable. Check that LM Studio is running.");
    }
  });

  console.log(`[${ts()}] Bot running — polling for messages`);
}

function ts() {
  return new Date().toISOString().slice(11, 19);
}

main().catch(console.error);
