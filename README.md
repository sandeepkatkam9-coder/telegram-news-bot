# 🚀 AutoTrade-HUB Market Intelligence Engine

A Python-based Market Intelligence Engine that collects financial news from multiple RSS sources, identifies important macroeconomic events, filters low-value content, and prepares actionable alerts for traders.

---

# 📌 Overview

AutoTrade-HUB is designed for traders who want **high-quality market-moving news** instead of hundreds of low-value headlines.

Instead of forwarding every article, the engine:

- Collects news from trusted financial sources
- Recognizes important market events
- Filters out less important news
- Estimates market impact
- (Upcoming) Sends intelligent Telegram alerts

---

# ✅ Current Features

- RSS News Collection
- Multi-Source News Aggregation
- Market Event Recognition
- Decision Engine
- Market Impact Engine
- Confidence Scoring
- Git Version Control

---

# 📊 Supported Markets

- 🟡 Gold (XAUUSD)
- ⚪ Silver (XAGUSD)
- 🛢️ Crude Oil (WTI / Brent)
- 🇺🇸 US Dollar
- 🇪🇺 Euro
- 🇬🇧 British Pound
- ₿ Bitcoin

---

# 📰 News Sources

- Reuters
- FXStreet
- Investing.com
- CoinDesk
- Kitco
- Additional sources planned

---

# 📂 Project Structure

```
telegram-news-bot/

│
├── app/
│   ├── decision_engine.py
│   ├── event_recognizer.py
│   ├── impact_engine.py
│   ├── market_events.py
│   ├── news_fetcher.py
│   ├── rss_sources.py
│   └── ...

│
├── data/
│
├── bot.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/sandeepkatkam9-coder/telegram-news-bot.git
```

Open the project:

```bash
cd telegram-news-bot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run

```bash
py bot.py
```

---

# 📈 Current Workflow

```
RSS News
     │
     ▼
Event Recognition
     │
     ▼
Decision Engine
     │
     ▼
Market Impact Engine
     │
     ▼
Telegram Alerts (Coming Soon)
```

---

# 🗺️ Roadmap

## ✅ Milestone 1
- RSS News Collection
- Asset Detection
- Event Classification

## ✅ Milestone 2
- Event Recognition
- Decision Engine
- Market Impact Engine

## 🚧 Milestone 3
- Duplicate Detection
- Better Article Classification
- Telegram Integration

## 🚧 Milestone 4
- AI Market Summary
- Daily News Digest
- Weekly Market Report

## 🚧 Milestone 5
- Economic Calendar Integration
- TradingView Alerts
- MT5 Notifications

---

# 📄 License

This project is under development.

---

# 👨‍💻 Author

AutoTrade-HUB