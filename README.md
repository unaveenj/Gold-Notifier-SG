# 🪙 GoldAlert SG — Gold Price Notifier

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://goldalert-sg.streamlit.app)

An automated gold price monitoring system for Singapore that scrapes live jewellery gold prices and sends email alerts to subscribers. Features a premium SaaS-style landing page for subscription management.

Built with:
- Python · BeautifulSoup · Gmail SMTP
- Streamlit · Airtable
- GitHub Actions (serverless scheduler)

---

# 🖥 Frontend — Luxury Financial Terminal UI

The Streamlit frontend has been redesigned as a polished, premium SaaS landing page. The aesthetic direction is **"Luxury Financial Terminal"** — editorial, refined, and data-precise.

### Design System

| Element | Choice |
|---|---|
| **Display font** | Cormorant Garamond (serif, editorial) |
| **Data/number font** | DM Mono (monospaced, instrument-like) |
| **Body font** | Outfit (modern, clean) |
| **Gold accent** | `#c8a84b` — real 22k gold, not garish yellow |
| **Background** | `#050507` near-black for maximum gold contrast |

### Key UI Features

- **Sticky frosted navbar** — blur backdrop with gold logo, pinned on scroll
- **Hero section** — grain noise texture overlay, radial gold ambient glow, large serif headline split between regular + italic weights, animated live-status badge
- **Subscription form** — dark card with gold hairline borders; button transitions from transparent outline to filled gold on hover
- **Flip clock counters** — two-panel card flip architecture with staggered slide-up entrance animations, DM Mono digits on dark instrument panels with corner accent gradients
- **Value proposition** — large editorial `S$350` in Cormorant Garamond with gold gradient, decorative hairline accents above and below
- **How it works** — Roman numerals (I, II, III) with geometric icons, minimal dark cards
- **Footer** — gold hairline divider with centred ornament, reassurance copy

### Page Sections

1. **Hero** — headline, subheadline, live badge, description
2. **Subscribe** — email form with duplicate protection, whitespace trimming, validation
3. **Live Metrics** — flip clock counters for subscriber count and notifications sent (live from Airtable)
4. **Value Proposition** — quantified savings with editorial treatment
5. **How It Works** — three-step process cards
6. **Trust Footer** — no-spam guarantee, SGD-only notice, hourly check frequency

---

# 🚀 What This Bot Does

Every hour between **08:00 – 22:00 SGT**, the bot:

1. Scrapes gold prices from Mustafa Jewellery
2. Extracts 22k (916) and 24k (999) jewellery prices + last updated timestamp
3. Sends an email notification to all Airtable subscribers
4. Notifies even on scrape failure (with error details)

---

# 🏗 Architecture

```
Streamlit UI (subscription form)
        ↓
Airtable (subscriber email store)
        ↓
GitHub Actions (hourly cron · 08:00–22:00 SGT)
        ↓
Python Scraper (retry + timeout logic)
        ↓
Gmail SMTP
        ↓
Email Notification 📧
```

---

# 🧠 Reliability Features

- ✅ Max 3 retry attempts per scrape
- ✅ 10-second total scrape deadline
- ✅ Exponential backoff (0.5s → 1s)
- ✅ Numeric validation of prices
- ✅ Structured failure notifications
- ✅ Serverless execution (GitHub Actions)
- ✅ Duplicate email subscription protection
- ✅ Airtable-backed subscriber store
- ✅ Live subscriber count on landing page

---

# 📲 Example Notification

**On Success**

```
Gold Price Update (SGD)

22k (916): 204.40
24k (999): 222.00

Last updated on source: 26-02-2026 07:17:03 AM
Job run time: 2026-02-26 08:00:02 (SGT)

Status: OK
```

**On Failure**

```
Gold Price Update (SGD) - STALE

Job run time: 2026-02-26 08:00:02 (SGT)

Status: FAILED
Error: <error details>
```

---

# 🔐 Setup Instructions

## 1️⃣ Clone Repo

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

## 2️⃣ Install Dependencies

```bash
pip install -r scraper/requirements.txt
pip install -r streamlit_app/requirements.txt
```

## 3️⃣ Configure Gmail SMTP

Use a **Google App Password**, not your normal Gmail password.

1. Enable **2-Step Verification** on your Google account
2. Go to **Google Account → Security → App Passwords**
3. Generate a password for `Mail / Other`

Google will give a **16-character password**.

## 4️⃣ Add GitHub Secrets

Go to `Repo → Settings → Secrets and variables → Actions` and add:

| Secret | Description |
|---|---|
| `AIRTABLE_API_KEY` | Airtable personal access token |
| `AIRTABLE_BASE_ID` | Airtable base ID |
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Google App Password |

## 5️⃣ Add Streamlit Secrets

In Streamlit Community Cloud, add to `secrets.toml`:

```toml
AIRTABLE_API_KEY = "your_key"
AIRTABLE_BASE_ID = "your_base_id"
```

---

# ⏰ Scheduling

Cron configured in `.github/workflows/goldrates.yml`:

```yaml
0 0-14 * * *   # Runs hourly 00:00–14:00 UTC = 08:00–22:00 SGT
```

| UTC | Singapore |
|-----|-----------|
| 00:00 | 08:00 |
| 01:00 | 09:00 |
| ... | ... |
| 14:00 | 22:00 |

---

# 🛠 Core Scraper Logic

Targets Mustafa Jewellery website. Extracts elements by ID:

```
22k_price1        → 22k (916) gold price
24k_price1        → 24k (999) gold price
date_update_gold  → source last-updated date
time_updates_gold → source last-updated time
```

Retry strategy: 3 attempts max · 10s global deadline · exponential backoff

---

# 📈 Future Enhancements

- Store historical prices in Airtable/Google Sheets
- Price change detection (alert only on delta)
- Daily gold price chart in email
- Price threshold alerts (notify only below X)
- Support multiple pricing sources
- Unsubscribe link in email footer

---

# ⚠ Disclaimer

This project scrapes publicly available pricing data for **personal monitoring purposes only**. Ensure compliance with the target website's terms of service before deploying at scale.

---

# 🧑‍💻 Author

Built as a lightweight automation project to monitor Singapore gold prices using serverless infrastructure.

---

⭐ Star this repo if you found it useful
