# Shelby Solana Trading Agent

AI-powered trading agent for Meteora DLMM pools on Solana — with immutable audit trail on Shelby Protocol decentralized storage.

---

## Overview

This agent monitors Meteora Dynamic Liquidity Market Maker (DLMM) pools, generates trading signals based on technical analysis, executes trades, and stores every decision on Shelby Protocol for verifiable provenance.

**Built for:** Solana DeFi traders who want transparent, auditable AI trading decisions.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        TRIGGER                                │
│              (cron job / manual run)                         │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                  Python Trading Agent                        │
│                                                               │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐     │
│  │   Meteora   │──▶│   Signal    │──▶│     Config      │     │
│  │   Client    │   │  Generator  │   │    Manager      │     │
│  └─────────────┘   └─────────────┘   └─────────────────┘     │
│                          │                                    │
│                          ▼                                    │
│              ┌─────────────────────────┐                      │
│              │   Local State Cache    │                      │
│              │    (JSON / SQLite)     │                      │
│              └───────────┬─────────────┘                      │
└──────────────────────────┼───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Shelby Storage Layer                       │
│                                                               │
│  Every signal → 1 immutable blob on Shelby Protocol         │
│  • Timestamp   • Pool address   • Signal type                │
│  • Confidence  • Agent version  • Decision rationale         │
└──────────────────────────────────────────────────────────────┘
```

---

## Features

- [x] **Meteora DLMM Pool Monitoring** — Fetch real-time pool data (liquidity, bin prices, fee APR)
- [x] **Technical Signal Generation** — RSI, volatility, trend analysis per pool
- [x] **Shelby Protocol Audit Trail** — Every signal stored as immutable blob
- [x] **Configurable Position Sizing** — Max position, min liquidity thresholds
- [x] **Cron-based Automation** — Scheduled runs with configurable intervals
- [x] **Environment-based Config** — No hardcoded credentials
- [x] **Telegram Trade Alerts** — Get notified on buy/sell/LP signals via Telegram bot

---

## Notifications

The agent can send real-time trade alerts to Telegram when signals are generated.

### Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather)
2. Get your bot token (starts with `bot`)
3. Start a chat with your bot and send `/start`
4. Get your chat ID using [@userinfobot](https://t.me/userinfobot) or the API

Add to your `.env`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=5285735187
```

### Alert Format

```
🟢 BUY
Token: `ABC123`
Amount: 0.72K
Tx: `ABC12345...XYZ78901`
Pool: `DEF67890...GHI23456`
```

---

## Prerequisites

- Python 3.10+
- Solana wallet (for trading)
- Meteora API key (public endpoint available)
- Shelby Protocol API key

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/morealwa1/shelby-solana-trading-agent.git
cd shelby-solana-trading-agent
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
SOLANA_PRIVATE_KEY=your_base58_private_key
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
METEORA_API_KEY=your_meteora_key
METEORA_RPC_URL=https://dlmm-api.meteora.ag
SHELBY_API_KEY=your_shelby_key
MAX_POSITION_SIZE=0.1
MIN_POOL_LIQUIDITY=1000
SIGNAL_CONFIDENCE_THRESHOLD=0.65
```

### 3. Run

```bash
python src/main.py
```

---

## Project Structure

```
shelby-solana-trading-agent/
├── src/
│   ├── agent/
│   │   ├── config.py           # Configuration management
│   │   ├── meteora_client.py   # Meteora API client
│   │   └── signals.py          # Technical analysis signals
│   ├── shelby-storage/
│   │   ├── sync.ts             # Shelby blob upload
│   │   └── types.ts            # TypeScript types
│   └── main.py                 # Entry point
├── data/                       # Local state cache
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
└── README.md
```

---

## How It Works

### Signal Generation

The agent calculates trading signals using multiple indicators:

| Indicator | Description | Range |
|-----------|-------------|-------|
| RSI | Relative Strength Index | 0-100 |
| Volatility | Price variance over lookback | 0-1 |
| Trend | Moving average direction | -1 to 1 |
| Confidence | Weighted composite score | 0-1 |

### Audit Trail

Every agent run produces a blob like:

```json
{
  "timestamp": "2026-04-29T09:00:00Z",
  "pool_address": "PLACEHOLDER",
  "signal": "BUY",
  "confidence": 0.72,
  "indicators": {
    "rsi": 34.5,
    "volatility": 0.12,
    "trend": 0.65
  },
  "agent_version": "1.0.0",
  "shelby_blob_id": "PLACEHOLDER"
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Trading Logic | Python 3.10+ |
| Solana SDK | solders + solana |
| HTTP Client | httpx |
| Shelby Storage | @shelby-protocol/sdk |
| Scheduling | cron |

---

## Security Notes

- **Never commit `.env`** — Contains private keys
- **Use separate wallet** for trading agent
- **Revoke API keys** when not in use
- **Audit trail is immutable** — Once uploaded, cannot be modified

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built with ⚡ for the Shelby and Solana ecosystems.**
