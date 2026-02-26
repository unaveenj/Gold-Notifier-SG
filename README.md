# 🪙 Gold Rate WhatsApp Bot

An automated gold price monitoring bot that scrapes Gold price
gold rates and sends WhatsApp notifications 3 times per day.

Built with: - Python - BeautifulSoup - Twilio WhatsApp Sandbox - GitHub
Actions (serverless scheduler)

------------------------------------------------------------------------

## 🚀 What This Bot Does

Every day at:

-   🕗 08:00 SGT\
-   🕐 13:00 SGT\
-   🕗 20:00 SGT

It:

1.  Scrapes gold prices from xxx
2.  Extracts:
    -   22k (916) jewellery price
    -   24k (999) jewellery price
    -   Shop "Last Updated" timestamp
3.  Sends the result to WhatsApp
4.  Notifies even if scraping fails (with error details)

------------------------------------------------------------------------

## 🏗 Architecture

    GitHub Actions (cron 3× daily)
            ↓
    Python Scraper (Retry + Timeout logic)
            ↓
    Twilio WhatsApp API
            ↓
    My WhatsApp 📲

------------------------------------------------------------------------

## 🧠 Reliability Features

-   ✅ Max 3 retry attempts
-   ✅ 10-second total scrape deadline
-   ✅ Exponential backoff
-   ✅ Numeric validation of prices
-   ✅ Structured failure notifications
-   ✅ Runs serverlessly (no VM needed)

------------------------------------------------------------------------

## 📲 Example Notification

### On Success

    Gold Rates (SGD)
    22k (916): 204.40
    24k (999): 222.00

    Shop last updated: 26-02-2026 07:17:03 AM (SGT)
    Job run time: 2026-02-26 08:00:02 (SGT)
    Status: OK

### On Failure

    Gold Rates (SGD) - STALE

    Job run time: 2026-02-26 08:00:02 (SGT)
    Status: FAILED
    Error: <error details>

------------------------------------------------------------------------

## 🔐 Setup Instructions

### 1️⃣ Clone Repo

``` bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

------------------------------------------------------------------------

### 2️⃣ Install Dependencies (Local Testing)

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

### 3️⃣ Configure Twilio WhatsApp Sandbox

1.  Create Twilio account
2.  Enable WhatsApp Sandbox
3.  Join sandbox from your WhatsApp:
    -   Send the provided `join xxxxxx` code
4.  Collect:
    -   Account SID
    -   Auth Token
    -   Sandbox WhatsApp number

------------------------------------------------------------------------

### 4️⃣ Add GitHub Secrets

Go to:

Repo → Settings → Secrets and variables → Actions

Add:

  Secret Name            Description
  ---------------------- ------------------------------
  `TWILIO_ACCOUNT_SID`   Twilio Account SID
  `TWILIO_AUTH_TOKEN`    Twilio Auth Token
  `TWILIO_FROM`          e.g. `whatsapp:+14155238886`
  `TWILIO_TO`            e.g. `whatsapp:+65XXXXXXXX`

------------------------------------------------------------------------

## ⏰ Scheduling

Configured in:

.github/workflows/goldrates.yml

Cron (UTC):

``` yaml
0 0 * * *   # 08:00 SGT
0 5 * * *   # 13:00 SGT
0 12 * * *  # 20:00 SGT
```

------------------------------------------------------------------------

## 🛠 Core Logic

The scraper:

-   Uses `requests`
-   Parses HTML with BeautifulSoup
-   Extracts elements by ID:
    -   `22k_price1`
    -   `24k_price1`
    -   `date_update_gold`
    -   `time_updates_gold`

Retry Strategy: - 3 attempts max - 10 second global deadline -
Exponential backoff (0.5s → 1s)

------------------------------------------------------------------------

## 📈 Future Enhancements

-   Store historical prices in Google Sheets
-   Add price change detection
-   Send alerts only on significant movement
-   Add dashboard (Grafana)
-   Support multiple jewellery shops
-   Migrate to WhatsApp Cloud API (lower cost long-term)

------------------------------------------------------------------------

## ⚠ Disclaimer

This project scrapes publicly available price data for personal
monitoring purposes.\
Ensure compliance with website terms before deploying at scale.

------------------------------------------------------------------------

## 🧑‍💻 Author

Built as a lightweight automation project to monitor gold prices
efficiently using serverless infrastructure.

------------------------------------------------------------------------

## ⭐ If You Found This Useful

Star the repo 😄
