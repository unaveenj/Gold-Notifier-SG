# Gold Notifier — Technical Documentation

> Last updated: 2026-03-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Data Flow](#3-data-flow)
4. [Scheduler — GitHub Actions](#4-scheduler--github-actions)
5. [Scraper — gold_bot.py](#5-scraper--gold_botpy)
   - [Retry and Deadline Model](#51-retry-and-deadline-model)
   - [Mustafa Jewellery](#52-mustafa-jewellery)
   - [Malabar Gold SG](#53-malabar-gold-sg)
   - [Joyalukkas SG](#54-joyalukkas-sg-graphql)
   - [GRT Jewels SG](#55-grt-jewels-sg)
   - [Failure Fallback](#56-failure-fallback-with-old-rates)
6. [Announcement System](#6-announcement-system)
7. [Price Chart Generation](#7-price-chart-generation)
8. [Email Notification System](#8-email-notification-system)
9. [Error Handling](#9-error-handling)
10. [Airtable Data Model](#10-airtable-data-model)
11. [Web Frontend — Next.js](#11-web-frontend--nextjs)
12. [API Routes](#12-api-routes)
13. [Environment Variables](#13-environment-variables)
14. [Key Engineering Challenges and Solutions](#14-key-engineering-challenges-and-solutions)
15. [Reliability Mechanisms](#15-reliability-mechanisms)
16. [Local Development Setup](#16-local-development-setup)
17. [Glossary](#17-glossary)

---

## 1. Overview

**Gold Notifier** is a fully serverless system that monitors live gold prices across four Singapore jewellers and sends email alerts to subscribers when prices are scraped. It targets buyers of 22k (916 purity) and 24k (999 purity) gold.

**Website:** https://www.goldnotifier.com
**Contact:** alerts@goldnotifier.com

**Key properties:**
- Zero infrastructure cost — no servers, no databases to manage
- Fully automated — scraping, alerting, and subscriber management are end-to-end automated
- Fault-tolerant — individual scraper failures do not stop the email from sending
- No user account required — subscribe and unsubscribe with only an email address

---

## 2. System Architecture

> Diagram: [`docs/diagrams/architecture.drawio`](diagrams/architecture.drawio)
> Open in [diagrams.net](https://app.diagrams.net) to view or edit.

The system has two independent halves that share only Airtable as a data store:

**Scraper half** (Python · GitHub Actions):
- `gold_bot.py` — scrapes prices and sends alerts, triggered by cron or manual `/api/trigger`
- `announcement.py` — sends custom announcements to all subscribers, triggered manually via GitHub Actions UI

**Web half** (Next.js · Vercel):
- Landing page at `goldnotifier.com`
- API routes for subscribe, unsubscribe, metrics, visitor count, and manual trigger

```
GitHub Actions Cron ──────────────────► gold_bot.py
Manual Trigger (goldnotifier.com/trigger) ───► GitHub API ──► gold_bot.py
Announcement Workflow (GitHub UI) ──────────► announcement.py

gold_bot.py ──► 4 shop scrapers (retry loop)
             ──► Airtable (read/write prices & subscribers)
             ──► Namecheap SMTP ──► Subscribers

Next.js / Vercel ◄──► Users (browser / mobile)
                 ◄──► Airtable (subscribe · unsubscribe · metrics)
```

---

## 3. Data Flow

> Diagram: [`docs/diagrams/dataflow.drawio`](diagrams/dataflow.drawio)

### Scraping and alert run

```
1.  Scrape all 4 shops (sequence, each with its own retry loop)
2.  Fetch last known price per shop from Airtable (for trend arrows)
3.  Build email body — one section per shop, with ↑/↓ indicators
4.  Fetch full price history from Airtable (for chart)
5.  Generate dual-subplot PNG chart (22k top, 24k bottom)
6.  Fetch subscriber list from Airtable
7.  Send one HTML email per subscriber via Namecheap SMTP
        └── plain text fallback + HTML body + inline CID chart image
8.  Save scraped prices to Airtable (only for shops where status=OK)
```

> **Note:** Step 8 (saving prices) happens **after** sending the email. This is intentional — the chart is generated from historical data only. Current prices appear in the email text but are not yet in the history chart.

### Subscription flow

```
User enters email → POST /api/subscribe
  → Airtable duplicate check (filterByFormula)
  → If duplicate: return HTTP 409
  → If new: create record in `subscribers` table → return HTTP 200
```

### Unsubscription flow (OTP-verified)

> Diagram: [`docs/diagrams/unsubscribe_flow.drawio`](diagrams/unsubscribe_flow.drawio)

```
User enters email → POST /api/unsubscribe/request
  → Look up email in `subscribers` table
  → If not found: return HTTP 200 silently (prevents enumeration)
  → Generate 6-digit OTP, delete any existing OTP, save new OTP
  → Send OTP via Namecheap SMTP
  → Return HTTP 200

User enters OTP → POST /api/unsubscribe/confirm
  → Query (email, otp) in `otps` table
  → If not found: return HTTP 400
  → Check createdTime against 10-minute TTL
  → If expired: delete OTP record, return HTTP 400
  → If valid: delete subscriber + OTP records → return HTTP 200
```

---

## 4. Scheduler — GitHub Actions

**File:** `.github/workflows/goldrates.yml`

The workflow runs on a UTC cron schedule mapping to Singapore business hours (SGT = UTC+8):

| UTC time | SGT time |
|----------|----------|
| 00:05    | 08:05    |
| 02:05    | 10:05    |
| 04:05    | 12:05    |
| 06:05    | 14:05    |
| 08:05    | 16:05    |
| 10:05    | 18:05    |
| 12:05    | 20:05    |

**Cron expression:** `"5 0,2,4,6,8,10,12 * * *"`

**Why `:05` past the hour?**
GitHub's shared cron queue is congested at `:00`. Scheduling at `:05` reduces queue delay and keeps runs close to their intended time.

The workflow also supports `workflow_dispatch` — allowing a manual trigger from GitHub Actions UI or via the `/api/trigger` endpoint.

**GitHub Actions secrets required:**

```yaml
env:
  AIRTABLE_API_KEY: ${{ secrets.AIRTABLE_API_KEY }}
  AIRTABLE_BASE_ID: ${{ secrets.AIRTABLE_BASE_ID }}
  EMAIL_USER:       ${{ secrets.EMAIL_USER }}
  EMAIL_PASSWORD:   ${{ secrets.EMAIL_PASSWORD }}
```

---

## 5. Scraper — gold_bot.py

**File:** `scraper/gold_bot.py`

**Dependencies** (`scraper/requirements.txt`):

| Package | Purpose |
|---|---|
| `requests` | HTTP fetching for Mustafa, Malabar, Joyalukkas |
| `cloudscraper` | Bot-bypass HTTP client for GRT (mimics Chrome TLS fingerprint) |
| `beautifulsoup4` | HTML parsing for Mustafa, Malabar, GRT |
| `pytz` | SGT timezone handling |
| `pyairtable` | Airtable read/write operations |
| `python-dotenv` | Local `.env` loading (skipped in CI) |
| `matplotlib` | Headless PNG chart generation |

Environment detection: if `AIRTABLE_API_KEY` is not set as an env var, it loads `.env` from the project root. No code changes needed between local and CI.

---

### 5.1 Retry and Deadline Model

All scrapers use `scrape_with_retry()` or equivalent per-shop functions.

**Parameters:**
- `MAX_ATTEMPTS = 3`
- `TOTAL_DEADLINE_SECONDS = 45`

**How it works:**

```
start = time.time()

for attempt in 1..3:
    remaining = 45 - (time.time() - start)
    if remaining <= 0: break

    try:
        html = fetch(url, timeout=remaining)
        parse and return result
    except:
        backoff = 0.5 × 2^(attempt-1)   ← 0.5s, 1.0s, 2.0s
        sleep(backoff) if time allows
```

`remaining` is passed directly as the HTTP timeout — each retry gets the full remaining budget, not a fixed slice.

---

### 5.2 Mustafa Jewellery

**URL:** `https://mustafajewellery.com/`
**Method:** `requests.get` + BeautifulSoup

| Element ID | Content |
|---|---|
| `#22k_price1` | 22k (916) price, e.g. `204.40` |
| `#24k_price1` | 24k (999) price |
| `#date_update_gold` | Source last-updated date |
| `#time_updates_gold` | Source last-updated time |

Prices are validated with `is_numberish()` before use. Empty or non-numeric values raise `ValueError` caught by the retry loop.

---

### 5.3 Malabar Gold SG

**URL:** `https://www.malabargoldanddiamonds.com/stores/singapore`
**Method:** `requests.get` + BeautifulSoup

Singapore's country code on Malabar's platform is `85`:

| Element ID | Content |
|---|---|
| `#price22kt_85` | 22k price, format `179.00 SGD` |
| `#price24kt_85` | 24k price |
| `#updatedtime_85` | Source last-updated timestamp |

Currency suffix stripped with `re.sub(r"[^\d.]", "", raw)`.

---

### 5.4 Joyalukkas SG (GraphQL)

**Endpoint:** `https://www.joyalukkas.com/graphql`
**Method:** `requests.post` — direct API call, not HTML scraping.

```python
query   = "{getgoldrates{metal_rate_time Data{GOLD_22KT_RATE GOLD_24KT_RATE}}}"
headers = {
    "Content-Type": "application/json",
    "Store":        "sg",    # selects Singapore store and SGD pricing
}
```

**Response path:**
```
data.getgoldrates.Data[0].GOLD_22KT_RATE  → "169.00"
data.getgoldrates.Data[0].GOLD_24KT_RATE  → "184.00"
data.getgoldrates.metal_rate_time          → last updated timestamp
```

---

### 5.5 GRT Jewels SG

**URL:** `https://www.grtjewels.com/asia/`
**Method:** `cloudscraper` + BeautifulSoup

`cloudscraper` bypasses Cloudflare WAF by mimicking Chrome's TLS fingerprint:

```python
scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)
```

**The dropdown problem:** GRT's prices are inside a CSS hover dropdown — visually hidden but present in the initial HTML. No JavaScript execution needed.

**CSS navigation path:**
```
li.menu-item-has-children
  └─ a[text contains "Today's Rate"]
  └─ ul.sub-menu.sf-sub-indicator
       └─ a: "GOLD - 22KT - 1. g - SGD $ 169.90"
       └─ a: "GOLD - 24KT - 1. g - SGD $ 184.60"
```

**Price extraction (`_extract_price_from_text`):**
- **Primary:** match `SGD\s*\$?\s*(\d{2,4}...)` pattern
- **Fallback:** scan for any number in the 80–600 SGD per-gram range

---

### 5.6 Failure Fallback with Old Rates

When a scraper exhausts all retries (`status: FAILED`), the email section still shows the last known price from Airtable:

```
🏪 [Shop Name]
22k (916): S$169.90 (Old rate — server error)
24k (999): S$184.60 (Old rate — server error)

Status: FAILED — <error detail>
Check latest: <shop URL>
```

If no historical price exists, only the failure status and error are shown.

---

## 6. Announcement System

**Files:**
- `scraper/announcement.py` — standalone sender script
- `.github/workflows/announcement.yml` — manual workflow

### How it works

1. Edit `ANNOUNCEMENT_SUBJECT` and `ANNOUNCEMENT_BODY` directly in `announcement.py`
2. Commit and push
3. Go to GitHub Actions → **Send Announcement** → **Run workflow**

The script fetches all subscribers from Airtable and sends a branded HTML email to each one using the same Namecheap SMTP setup.

```python
ANNOUNCEMENT_SUBJECT = "Your subject here"
ANNOUNCEMENT_BODY    = """Dear Subscriber, ..."""
```

### Workflow

```yaml
on:
  workflow_dispatch:   # manual only — never runs on a schedule

env:
  EMAIL_USER:     ${{ secrets.EMAIL_USER }}
  EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
```

### Output

```
Sending announcement to N subscriber(s)...
  Sent to user@example.com
  ...
Done. Sent: N  Failed: 0
```

---

## 7. Price Chart Generation

**Function:** `generate_price_chart(history: list) -> bytes | None`

Dual-subplot PNG rendered headlessly with matplotlib `Agg` backend.

| Property | Value |
|---|---|
| Backend | `matplotlib.use("Agg")` — no display required |
| Size | 12 × 7 inches at 150 DPI |
| Layout | 2 subplots sharing x-axis: 22K top, 24K bottom |
| Background | Near-black `#0d0d0d` (figure), `#161616` (axes) |
| Title color | Gold `#c8a84b` |
| X-axis | SGT datetime, `"DD Mon"` format, auto-spaced |

**Shop colors:**

| Shop | Color | Hex |
|---|---|---|
| Mustafa Jewellery | Light blue | `#4FC3F7` |
| Malabar Gold SG | Light green | `#81C784` |
| Joyalukkas SG | Amber | `#FFB74D` |
| GRT Jewels SG | Lavender | `#CE93D8` |

**Output:** Raw PNG bytes via `BytesIO`. Returns `None` if price history is empty — email is sent without a chart.

---

## 8. Email Notification System

**Transport:** Namecheap Private Email SMTP

| Setting | Value |
|---|---|
| Host | `mail.privateemail.com` |
| Port | `587` |
| Encryption | STARTTLS (`server.ehlo()` → `server.starttls()` → `server.ehlo()`) |
| From | `Gold Notifier <alerts@goldnotifier.com>` |
| Auth | `EMAIL_USER` / `EMAIL_PASSWORD` env vars |

### send_email function

```python
def send_email(to_email, subject, body, html_body=None, chart_bytes=None) -> bool
```

Returns `True` on success, `False` on failure — never raises. Each subscriber gets an independent SMTP connection.

### Email MIME structure

```
MIMEMultipart("related")
├── MIMEMultipart("alternative")
│   ├── MIMEText(plain_text, "plain")    ← fallback for non-HTML clients
│   └── MIMEText(html_body, "html")      ← dark-themed HTML with chart
└── MIMEImage(chart_png)                 ← inline CID image: <goldchart>
```

The HTML references the chart via `<img src="cid:goldchart">` — the image is embedded inside the email, not fetched from a remote URL.

**Subject format:** `Gold Prices · 27 Mar 10:05 AM`

**Rate limiting:** 1-second sleep between subscribers (`time.sleep(1)`) to avoid SMTP throttling.

---

## 9. Error Handling

### Scraper (gold_bot.py)

| Scenario | Handling |
|---|---|
| HTTP timeout / network error | Caught by `except Exception` in retry loop; exponential backoff then retry |
| Non-numeric price parsed | `is_numberish()` raises `ValueError`; caught by retry loop |
| All 3 attempts fail | Returns `{"status": "FAILED", "error": "..."}` dict |
| Failed shop in email | `build_shop_section()` uses last Airtable price with `(Old rate — server error)` label |
| No last price in Airtable | Shows failure status and error only; email still sends |
| Airtable write fails | `save_prices()` wraps in `try/except`; prints error; does not crash |
| EMAIL_USER/PASSWORD missing | `send_email()` checks env vars; prints `Email skipped`; returns `False` |
| SMTP auth failure | Caught by `except Exception`; prints `type(e).__name__: message`; returns `False` |
| One subscriber email fails | Loop continues to next subscriber; partial send is acceptable |

### Web API (Next.js)

| Scenario | Handling |
|---|---|
| Missing env vars | Returns `HTTP 503 { "error": "Service unavailable" }` |
| Airtable API error | Caught in try/catch; returns appropriate HTTP 4xx/5xx |
| Invalid email format | Returns `HTTP 400 { "error": "Invalid email address" }` |
| Duplicate subscription | Returns `HTTP 409 { "error": "already_subscribed" }` |
| OTP not found | Returns `HTTP 400 { "error": "..." }` |
| OTP expired (>10 min) | Deletes OTP record; returns `HTTP 400 { "error": "OTP expired" }` |
| Invalid trigger token | `/api/trigger` returns `HTTP 401 { "error": "Unauthorized" }` |
| GitHub API dispatch fails | `/api/trigger` returns the GitHub API error with status code |

### Announcement (announcement.py)

| Scenario | Handling |
|---|---|
| Empty subject or body | Prints error and calls `SystemExit(1)` — fails loudly |
| No subscribers | Prints message and calls `SystemExit(0)` — exits cleanly |
| SMTP failure per subscriber | Caught by `except Exception`; increments `failed` counter; continues loop |
| Missing credentials | `send_email()` prints `Email skipped` and returns `False` |

---

## 10. Airtable Data Model

### `subscribers`

| Field | Type | Notes |
|---|---|---|
| `email` | Single line text | Uniqueness enforced by app logic |

### `prices`

| Field | Type | Notes |
|---|---|---|
| `shop` | Single line text | One of the four shop name strings |
| `price_22k_916` | Number/text | Per-gram SGD price for 22k gold |
| `price_24k_999` | Number/text | Per-gram SGD price for 24k gold |
| `createdTime` | Auto (Airtable) | Chart x-axis timestamps |

One record per shop per successful run. Failed scrapes produce no record.

### `visitors`

| Field | Type | Notes |
|---|---|---|
| `count` | Number | Incremented on each new browser session |

Single record. Display value = `count + VISITOR_SEED (200)`.

### `otps`

| Field | Type | Notes |
|---|---|---|
| `email` | Single line text | Subscriber requesting unsubscription |
| `otp` | Single line text | 6-digit numeric code |
| `createdTime` | Auto (Airtable) | 10-minute TTL enforced against this |

Only one OTP per email at any time — existing records deleted before new ones are saved.

---

## 11. Web Frontend — Next.js

**Location:** `web/`
**Framework:** Next.js 14 App Router · Deployed to Vercel (root directory: `web/`)

**SEO:**
- `web/app/robots.ts` — robots.txt (allows all, disallows `/api/`, points to sitemap)
- `web/app/sitemap.ts` — XML sitemap with `/` (priority 1.0) and `/unsubscribe` (0.3)
- `web/app/layout.tsx` — title, meta description, OG image with dimensions, Twitter card, JSON-LD schema (WebSite + Organization + Service)
- Google Search Console verification: `web/public/google299bd36b9558fcc6.html`

**Fonts** (loaded via `next/font/google`):

| Variable | Font | Use |
|---|---|---|
| `--font-cormorant` | Cormorant Garamond | Display headings |
| `--font-outfit` | Outfit | Body text |
| `--font-mono` | JetBrains Mono | Numbers and metrics |

**Page components** (`web/app/page.tsx`):

| Component | Description |
|---|---|
| `GoldCanvas` | Full-page canvas animation: 130 gold dust particles + 7 glow orbs. `aria-hidden="true"`. Cleaned up on unmount. |
| `VisitorBadge` | Session-aware visitor counter using `sessionStorage`. POST on first visit, GET on return. |
| `SubscribeForm` | 5-state form: `idle / loading / success / error / duplicate`. Fires `metrics-refresh` event on success. |
| `LiveMetrics` | Polls `/api/metrics` every 30 seconds. Listens for `metrics-refresh` event. |

**Unsubscribe page** (`web/app/unsubscribe/page.tsx`):
- 3-step client component: `email → otp → done`
- OTP message is privacy-safe: does not confirm whether email is subscribed

---

## 12. API Routes

All routes in `web/app/api/`.

### POST /api/subscribe

| | |
|---|---|
| **Body** | `{ "email": "user@example.com" }` |
| **200** | `{ "success": true }` |
| **409** | `{ "error": "already_subscribed" }` |
| **400** | `{ "error": "Invalid email address" }` |
| **503** | `{ "error": "Service unavailable" }` (env missing) |

### GET /api/metrics

```
{ "subscribers": 42, "notifications": 1347 }
```

Notifications derived: `floor(price_records / 4) × subscribers + 1000`

### GET/POST /api/visitors

| Method | Behaviour |
|---|---|
| `GET` | Returns `{ "count": SEED + stored }` |
| `POST` | Increments by 1, returns new count |

`VISITOR_SEED = 200`

### POST /api/unsubscribe/request

Always returns `HTTP 200` regardless of whether email exists (prevents enumeration).

### POST /api/unsubscribe/confirm

| | |
|---|---|
| **Body** | `{ "email": "...", "otp": "123456" }` |
| **200** | `{ "ok": true }` |
| **400** | `{ "error": "Invalid OTP" }` or `{ "error": "OTP expired" }` |

OTP TTL: `OTP_TTL_MS = 600000` (10 minutes).

### POST /api/trigger

| | |
|---|---|
| **Header** | `x-trigger-token: <TRIGGER_TOKEN>` |
| **200** | `{ "ok": true, "message": "Workflow triggered" }` |
| **401** | `{ "error": "Unauthorized" }` |
| **500** | `{ "error": "GitHub PAT not configured" }` |

Calls GitHub API to dispatch `goldrates.yml` workflow on `master` branch.

---

## 13. Environment Variables

### Scraper (GitHub Actions secrets)

| Variable | Description |
|---|---|
| `AIRTABLE_API_KEY` | Airtable personal access token |
| `AIRTABLE_BASE_ID` | Airtable base ID (starts with `app`) |
| `EMAIL_USER` | `alerts@goldnotifier.com` |
| `EMAIL_PASSWORD` | Namecheap Private Email mailbox password |

### Web App (Vercel environment variables)

| Variable | Description |
|---|---|
| `AIRTABLE_API_KEY` | Same token as above |
| `AIRTABLE_BASE_ID` | Same base ID as above |
| `TRIGGER_TOKEN` | Secret string for `/api/trigger` authentication |
| `GITHUB_PAT` | GitHub personal access token with `workflow` scope |

### Optional (scraper)

| Variable | Default | Description |
|---|---|---|
| `SITE_URL` | `https://www.goldnotifier.com` | Unsubscribe link in email footer |

---

## 14. Key Engineering Challenges and Solutions

### 1. GRT Jewels — Price hidden in CSS hover dropdown

**Problem:** WAF blocked plain `requests` calls. Prices are CSS-hidden in a nav hover dropdown.

**Solution:**
- Switched to `cloudscraper` to bypass Cloudflare WAF
- Confirmed via DevTools that price data is in the initial HTML — no JS needed
- Navigate to `li.menu-item-has-children[text=Today's Rate] → ul.sub-menu`
- Parse `"GOLD - 22KT - 1. g - SGD $ 169.90"` with regex

> **Future risk:** If GRT moves to JS-injected prices, Playwright would be needed.

### 2. Malabar — Read timeouts consuming entire retry budget

**Problem:** Original 15-second total deadline meant one slow attempt consumed everything.

**Solution:** Increased `TOTAL_DEADLINE_SECONDS` from 15 to 45. Each of the 3 retries now has a realistic budget.

### 3. Email From header — RFC 5322 violation with emoji

**Problem:** Namecheap's SMTP rejected the original `"Gold Notifier 🔔 <alerts@goldnotifier.com>"` From header with error `5.7.1 — invalid From header`.

**Solution:** Removed the emoji. From header is now `Gold Notifier <alerts@goldnotifier.com>` — plain ASCII, RFC 5322 compliant.

### 4. Gmail → Namecheap SMTP migration

**Problem:** Migrated from personal Gmail to business email (`alerts@goldnotifier.com`).

**Changes:**
- SMTP: `smtplib.SMTP_SSL("smtp.gmail.com", 465)` → `smtplib.SMTP("mail.privateemail.com", 587)` + `starttls()`
- Env vars: `GMAIL_USER` / `GMAIL_APP_PASSWORD` → `EMAIL_USER` / `EMAIL_PASSWORD`
- Added `server.ehlo()` before and after `starttls()` for compatibility

### 5. GitHub Actions cron drift at top of hour

**Problem:** `:00` crons were delayed 30–60 minutes due to GitHub's shared runner queue load.

**Solution:** Shifted all crons to `:05` past the hour.

### 6. Joyalukkas — Dynamic page bypassed with GraphQL

**Problem:** Joyalukkas loads prices via JavaScript after page load.

**Solution:** DevTools network inspection revealed a public GraphQL endpoint. Direct POST with `Store: sg` header returns structured SGD pricing with no HTML parsing needed.

### 7. Price chart — Headless rendering and inline email embedding

**Solution:**
- `matplotlib.use("Agg")` for headless rendering in GitHub Actions
- Chart rendered to `BytesIO`, returned as PNG bytes
- Embedded as CID inline image — travels inside the email, not as a remote URL

### 8. Visitor counter — Session-based deduplication

**Solution:** `sessionStorage` key `ga_visited` — first visit in a session triggers `POST` (increment), subsequent loads trigger `GET` (read only).

---

## 15. Reliability Mechanisms

| Mechanism | Implementation |
|---|---|
| Per-shop retry loop | Up to 3 attempts with exponential backoff (0.5s, 1.0s, 2.0s) |
| Sliding timeout budget | `remaining = TOTAL_DEADLINE_SECONDS - elapsed` passed as HTTP timeout |
| Numeric price validation | `is_numberish()` validates all parsed prices before storing |
| Failure fallback | Failed shops show last Airtable price with `(Old rate — server error)` |
| Independent shop scrapers | One failure does not block others or the email send |
| Prices saved only on success | `save_prices()` called only when `status == "OK"` |
| Duplicate subscription guard | `filterByFormula` check before insert; HTTP 409 to client |
| OTP expiry | 10-minute TTL using Airtable `createdTime`; expired records deleted |
| Subscriber enumeration protection | `/api/unsubscribe/request` always returns 200 |
| Env var guard | All API routes return 503 if credentials are missing |
| Email never crashes the script | `send_email()` wraps SMTP in try/except and returns bool |

---

## 16. Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Airtable base with four tables: `subscribers`, `prices`, `visitors`, `otps`
- Namecheap Private Email mailbox or SMTP credentials

### Scraper

```bash
pip install -r scraper/requirements.txt

# Create .env in repo root
echo "AIRTABLE_API_KEY=your_token"    >> .env
echo "AIRTABLE_BASE_ID=appXXXXXXX"   >> .env
echo "EMAIL_USER=alerts@goldnotifier.com" >> .env
echo "EMAIL_PASSWORD=your_password"   >> .env

python scraper/gold_bot.py
```

### Web App

```bash
cd web
npm install
cp .env.local.example .env.local
# Edit .env.local: AIRTABLE_API_KEY, AIRTABLE_BASE_ID, TRIGGER_TOKEN, GITHUB_PAT

npm run dev   # http://localhost:3000
```

### Vercel Deployment

1. Import repo at [vercel.com/new](https://vercel.com/new)
2. Set **Root Directory** → `web`
3. Add environment variables: `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `TRIGGER_TOKEN`, `GITHUB_PAT`
4. Deploy

### GitHub Actions Setup

Add secrets under **Settings → Secrets and variables → Actions**:
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`
- `EMAIL_USER`
- `EMAIL_PASSWORD`

---

## 17. Glossary

| Term | Definition |
|---|---|
| **22k / 916** | 22-karat gold — 91.6% purity, most common for jewellery in Singapore |
| **24k / 999** | 24-karat gold — 99.9% purity, investment-grade |
| **SGT** | Singapore Standard Time — UTC+8, no daylight saving |
| **WAF** | Web Application Firewall — server-side bot detection |
| **cloudscraper** | Python library mimicking Chrome's TLS fingerprint to bypass WAF |
| **CID (Content-ID)** | Email MIME mechanism for embedding inline images |
| **STARTTLS** | Upgrade a plain TCP connection to TLS mid-session (port 587) |
| **Airtable offset** | Pagination token for fetching all records across multiple pages |
| **OTP** | One-Time Password — short-lived code for identity verification |
| **Agg backend** | matplotlib's headless renderer — works without a display |
| **filterByFormula** | Airtable REST query parameter equivalent to SQL WHERE |
| **workflow_dispatch** | GitHub Actions trigger type that allows manual workflow runs |
| **PAT** | Personal Access Token — GitHub auth token used by `/api/trigger` |
