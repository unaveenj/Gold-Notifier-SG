# 🪙 Gold Price Notifier Bot

An automated gold price monitoring bot that scrapes a public gold pricing website and sends **email notifications** on a scheduled basis.

Built with:
- Python
- BeautifulSoup
- Gmail SMTP
- GitHub Actions (serverless scheduler)

---

# 🚀 What This Bot Does

Every hour between:

- 🕗 08:00 SGT  
- 🕙 22:00 SGT  

The bot will:

1. Scrape gold prices from a public gold price website
2. Extract:
   - 22k (916) jewellery price
   - 24k (999) jewellery price
   - Website "Last Updated" timestamp
3. Send the result via **email notification**
4. Notify even if scraping fails (with error details)

---

# 🏗 Architecture

```
GitHub Actions (hourly cron)
        ↓
Python Scraper (Retry + Timeout logic)
        ↓
Gmail SMTP
        ↓
Email Notification 📧
```

---

# 🧠 Reliability Features

- ✅ Max 3 retry attempts
- ✅ 10-second total scrape deadline
- ✅ Exponential backoff
- ✅ Numeric validation of prices
- ✅ Structured failure notifications
- ✅ Serverless execution (GitHub Actions)
- ✅ Email spam protection (send once per run)

---

# 📲 Example Notification

## On Success

```
Gold Price Update (SGD)

22k (916): 204.40
24k (999): 222.00

Last updated on source: 26-02-2026 07:17:03 AM
Job run time: 2026-02-26 08:00:02 (SGT)

Status: OK
```

## On Failure

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

---

## 2️⃣ Install Dependencies (Local Testing)

```bash
pip install -r requirements.txt
```

---

# 📧 Configure Gmail SMTP

You must use a **Google App Password**, not your normal Gmail password.

Steps:

1. Enable **2-Step Verification** on your Google account
2. Go to **Google Account → Security → App Passwords**
3. Generate a password for:

```
App: Mail
Device: Other
```

Google will give a **16-character password**.

---

# 🔑 Add GitHub Secrets

Go to:

```
Repo → Settings → Secrets and variables → Actions
```

Add the following secrets:

| Secret Name | Description |
|-------------|-------------|
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Google App Password |

Example:

```
GMAIL_USER = your_email@gmail.com
GMAIL_APP_PASSWORD = abcd efgh ijkl mnop
```

---

# ⏰ Scheduling

Configured in:

```
.github/workflows/goldrates.yml
```

Cron (UTC):

```yaml
0 0-14 * * *
```

This equals:

| UTC | Singapore |
|-----|-----------|
| 00:00 | 08:00 |
| 01:00 | 09:00 |
| ... | ... |
| 14:00 | 22:00 |

So the bot runs **hourly between 08:00 – 22:00 SGT**.

---

# 🛠 Core Logic

The scraper:

- Uses `requests`
- Parses HTML with BeautifulSoup
- Extracts elements by ID:

```
22k_price1
24k_price1
date_update_gold
time_updates_gold
```

Retry Strategy:

- 3 attempts max
- 10 second global deadline
- Exponential backoff (0.5s → 1s)

---

# 📈 Future Enhancements

Possible improvements:

- Store historical prices in Google Sheets
- Generate daily gold price charts
- Add price change detection
- Send alerts only when price changes
- Support multiple pricing websites
- Add dashboard (Grafana)

---

# ⚠ Disclaimer

This project scrapes publicly available pricing data for **personal monitoring purposes only**.

Ensure compliance with the target website's terms of service before deploying at scale.

---

# 🧑‍💻 Author

Built as a lightweight automation project to monitor gold prices using serverless infrastructure.

---

# ⭐ If You Found This Useful

Consider starring the repo ⭐