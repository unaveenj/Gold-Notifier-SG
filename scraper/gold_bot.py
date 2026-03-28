import os
import re
import time
import requests
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import matplotlib
matplotlib.use("Agg")  # headless — no display needed
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pyairtable import Table
from dotenv import load_dotenv
from pathlib import Path
from price_tracker import calculate_percentage_change, format_change

# --------------------------------------------------
# Load .env only for local development
# GitHub Actions will supply environment variables
# --------------------------------------------------

if not os.getenv("AIRTABLE_API_KEY"):
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# --------------------------------------------------
# Environment variables
# --------------------------------------------------

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
EMAIL_USER       = os.getenv("EMAIL_USER")
EMAIL_PASSWORD   = os.getenv("EMAIL_PASSWORD")

# --------------------------------------------------
# Config
# --------------------------------------------------

SITE_URL       = os.getenv("SITE_URL", "https://www.goldnotifier.com")
MUSTAFA_URL    = "https://mustafajewellery.com/"
MALABAR_URL    = "https://www.malabargoldanddiamonds.com/stores/singapore"
JOYALUKKAS_GQL = "https://www.joyalukkas.com/graphql"
GRT_URL        = "https://www.grtjewels.com/asia/"
MAX_ATTEMPTS = 3
TOTAL_DEADLINE_SECONDS = 45   # 15s per attempt × 3

SHOP_URLS = {
    "Mustafa Jewellery":  MUSTAFA_URL,
    "Malabar Gold SG":    MALABAR_URL,
    "Joyalukkas SG":      "https://www.joyalukkas.com/sg/",
    "GRT Jewels SG":      GRT_URL,
}
USER_AGENT   = "Mozilla/5.0 (compatible; GoldRateBot/1.0)"
# GRT blocks simple bots — use full browser headers to pass their bot check
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}
SEPARATOR    = "=" * 33

SGT = pytz.timezone("Asia/Singapore")

SHOP_COLORS = {
    "Mustafa Jewellery": "#4FC3F7",   # light blue
    "Malabar Gold SG":   "#81C784",   # light green
    "Joyalukkas SG":     "#FFB74D",   # amber
    "GRT Jewels SG":     "#CE93D8",   # lavender
}

# --------------------------------------------------
# Airtable tables
# --------------------------------------------------

airtable_subscribers = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "subscribers")
airtable_prices      = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "prices")

# --------------------------------------------------
# Airtable helpers
# --------------------------------------------------

def get_subscribers():
    records = airtable_subscribers.all()
    return [r["fields"]["email"] for r in records if "email" in r.get("fields", {})]


def get_last_prices(shop: str):
    """Return the most recent price record for the given shop."""
    records = airtable_prices.all()
    shop_records = [r for r in records if r.get("fields", {}).get("shop") == shop]
    if not shop_records:
        print(f"No previous prices found for {shop}.")
        return None
    shop_records.sort(key=lambda r: r["id"], reverse=True)
    fields = shop_records[0]["fields"]
    print(f"Last prices for {shop}: {fields}")
    return {
        "price_22k_916": fields.get("price_22k_916"),
        "price_24k_999": fields.get("price_24k_999"),
    }


def save_prices(price_22k, price_24k, shop: str):
    try:
        airtable_prices.create({
            "price_22k_916": price_22k,
            "price_24k_999": price_24k,
            "shop": shop,
        })
        print(f"Prices saved to Airtable for {shop}.")
    except Exception as e:
        print(f"Failed to save prices for {shop}: {e}")


# --------------------------------------------------
# Price history + chart
# --------------------------------------------------

def get_price_history() -> list:
    """Fetch all price records from Airtable and return as a sorted list of dicts."""
    records = airtable_prices.all()
    history = []
    for r in records:
        fields  = r.get("fields", {})
        created = r.get("createdTime")
        shop    = fields.get("shop")
        p22     = fields.get("price_22k_916")
        p24     = fields.get("price_24k_999")
        if not (created and shop and p22 and p24):
            continue
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00")).astimezone(SGT)
            history.append({"dt": dt, "shop": shop, "p22": float(p22), "p24": float(p24)})
        except (ValueError, TypeError):
            continue
    history.sort(key=lambda x: x["dt"])
    return history


def generate_price_chart(history: list) -> bytes | None:
    """
    Render a dual-subplot dark-theme chart (22K top, 24K bottom),
    one color-coded line per shop, and return PNG bytes.
    """
    if not history:
        print("No price history — skipping chart.")
        return None

    fig, (ax22, ax24) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.patch.set_facecolor("#0d0d0d")

    for ax in (ax22, ax24):
        ax.set_facecolor("#161616")
        ax.tick_params(colors="#aaaaaa", labelsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a2a")
        ax.grid(True, color="#222222", linestyle="--", linewidth=0.6, alpha=0.8)
        ax.yaxis.label.set_color("#cccccc")
        ax.title.set_color("#e0e0e0")

    shops = list(dict.fromkeys(r["shop"] for r in history))  # preserve insertion order

    for shop in shops:
        color     = SHOP_COLORS.get(shop, "#ffffff")
        shop_data = [r for r in history if r["shop"] == shop]
        dts  = [r["dt"]  for r in shop_data]
        p22s = [r["p22"] for r in shop_data]
        p24s = [r["p24"] for r in shop_data]
        ax22.plot(dts, p22s, label=shop, color=color, linewidth=1.8, marker="o", markersize=3)
        ax24.plot(dts, p24s, label=shop, color=color, linewidth=1.8, marker="o", markersize=3)

    ax22.set_title("22K Gold  (916 purity) — S$ per gram", fontsize=11, pad=6)
    ax24.set_title("24K Gold  (999 purity) — S$ per gram", fontsize=11, pad=6)
    ax22.set_ylabel("Price (S$)", color="#cccccc", fontsize=9)
    ax24.set_ylabel("Price (S$)", color="#cccccc", fontsize=9)
    ax24.set_xlabel("Date (SGT)", color="#cccccc", fontsize=9)

    ax24.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax24.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate(rotation=30, ha="right")

    legend = ax22.legend(
        facecolor="#1e1e1e", edgecolor="#333333",
        labelcolor="white", fontsize=9, loc="upper left"
    )

    fig.suptitle("Gold Notifier — Price History", color="#c8a84b", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# --------------------------------------------------
# Utility
# --------------------------------------------------

def now_sgt():
    return datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")


def is_numberish(x: str) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def must_text(tag, label: str) -> str:
    if tag is None:
        raise ValueError(f"Missing element: {label}")
    value = tag.get_text(strip=True)
    if not value:
        raise ValueError(f"Empty value for: {label}")
    return value


def fetch_html(url: str, timeout_seconds: float, use_browser_headers: bool = False) -> str:
    headers = BROWSER_HEADERS if use_browser_headers else {"User-Agent": USER_AGENT, "Accept": "text/html"}
    r = requests.get(url, headers=headers, timeout=timeout_seconds)
    r.raise_for_status()
    return r.text


# --------------------------------------------------
# Mustafa parser
# --------------------------------------------------

def parse_mustafa_rates(html: str):
    soup = BeautifulSoup(html, "html.parser")

    p22_tag  = soup.find(id="22k_price1")
    p24_tag  = soup.find(id="24k_price1")
    date_tag = soup.find(id="date_update_gold")
    time_tag = soup.find(id="time_updates_gold")

    p22 = must_text(p22_tag, "22k_price1")
    p24 = must_text(p24_tag, "24k_price1")

    if not is_numberish(p22) or not is_numberish(p24):
        raise ValueError(f"Prices not numeric. Got 22k={p22}, 24k={p24}")

    last_updated = None
    if date_tag and time_tag:
        last_updated = f"{date_tag.get_text(strip=True)} {time_tag.get_text(strip=True)}"

    return p22, p24, last_updated


# --------------------------------------------------
# Malabar parser
# Singapore country code on Malabar site = 85
# element IDs: price22kt_85, price24kt_85, updatedtime_85
# Price format: "179.00 SGD" — strip " SGD" suffix
# --------------------------------------------------

def parse_malabar_rates(html: str):
    soup = BeautifulSoup(html, "html.parser")

    p22_tag  = soup.find(id="price22kt_85")
    p24_tag  = soup.find(id="price24kt_85")
    time_tag = soup.find(id="updatedtime_85")

    p22_raw = must_text(p22_tag, "price22kt_85")
    p24_raw = must_text(p24_tag, "price24kt_85")

    # Strip currency suffix e.g. "179.00 SGD" → "179.00"
    p22 = re.sub(r"[^\d.]", "", p22_raw).strip()
    p24 = re.sub(r"[^\d.]", "", p24_raw).strip()

    if not is_numberish(p22) or not is_numberish(p24):
        raise ValueError(f"Prices not numeric. Got 22k={p22_raw}, 24k={p24_raw}")

    last_updated = time_tag.get_text(strip=True) if time_tag else None

    return p22, p24, last_updated


# --------------------------------------------------
# GRT Jewels parser
# URL: https://www.grtjewels.com/asia/
# The "Today's Rate" dropdown is CSS-hidden on page load and revealed on hover.
# The price data IS present in the initial HTML — no JS execution needed.
# Element selectors to verify in DevTools:
#   - Inspect the "Today's Rate" nav item → find the hidden dropdown
#   - Look for elements containing "22K" / "24K" text with a price value nearby
#
# NOTE: If GRT moves price loading to a JS/API call in future, you will need
# Playwright. Install with: pip install playwright && playwright install chromium
# Then replace this parser with a Playwright fetch (see comment at end of function).
# --------------------------------------------------

def fetch_grt_html(timeout_seconds: float) -> str:
    """
    Fetch GRT page via cloudscraper, which rotates browser fingerprints and
    solves Cloudflare/WAF JS challenges that block plain requests calls.
    """
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "mobile": False})
    r = scraper.get(GRT_URL, timeout=timeout_seconds)
    r.raise_for_status()
    return r.text


def parse_grt_rates(html: str):
    """
    Exact HTML structure confirmed by user:
      <li class="menu-item menu-item-has-children">
        <a href="#">Today's Rate ...</a>
        <ul class="sub-menu sf-sub-indicator">
          <li><a href="#">GOLD - 22KT -  1. g  -  SGD  $ 169.90</a></li>
          <li><a href="#">GOLD - 24KT -  1. g  - SGD $ 184.60</a></li>
        </ul>
      </li>
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find the "Today's Rate" nav item by its anchor text
    todays_rate_li = None
    for li in soup.find_all("li", class_="menu-item-has-children"):
        a = li.find("a", recursive=False)
        if a and "today" in a.get_text(strip=True).lower() and "rate" in a.get_text(strip=True).lower():
            todays_rate_li = li
            break

    if todays_rate_li is None:
        raise ValueError("GRT: Could not find 'Today's Rate' menu item in page HTML.")

    sub_menu = todays_rate_li.find("ul", class_="sub-menu")
    if sub_menu is None:
        raise ValueError("GRT: Found 'Today's Rate' item but sub-menu is missing.")

    sub_links = [a.get_text(strip=True) for a in sub_menu.find_all("a")]

    p22 = p24 = None
    for text in sub_links:
        if re.search(r"22\s*KT", text, re.IGNORECASE):
            p22 = _extract_price_from_text(text)
        elif re.search(r"24\s*KT", text, re.IGNORECASE):
            p24 = _extract_price_from_text(text)

    if not p22 or not p24:
        raise ValueError(
            f"GRT: Could not extract 22K/24K from sub-menu. Got: {sub_links}"
        )

    if not is_numberish(p22) or not is_numberish(p24):
        raise ValueError(f"GRT: Prices not numeric. Got 22k={p22}, 24k={p24}")

    return p22, p24, None


def _extract_price_from_text(text: str) -> str | None:
    """
    Pull the gold-per-gram SGD price from GRT's confirmed text format:
      "GOLD - 22KT -  1. g  -  SGD  $ 169.90"
    Primary: match the value after 'SGD' and optional '$'
    Fallback: first number in the 80–600 SGD range
    """
    # Primary: explicit "SGD [optional $] <price>" pattern
    sgd_match = re.search(r"SGD\s*\$?\s*(\d{2,4}(?:\.\d{1,2})?)", text, re.IGNORECASE)
    if sgd_match:
        return sgd_match.group(1)

    # Fallback: any plausible per-gram price in SGD (80–600)
    for match in re.finditer(r"\b(\d{2,4}(?:\.\d{1,2})?)\b", text):
        val = match.group(1)
        try:
            if 80.0 <= float(val) <= 600.0:
                return val
        except ValueError:
            continue
    return None


def fetch_grt_rates(shop: str) -> dict:
    start      = time.time()
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        elapsed   = time.time() - start
        remaining = TOTAL_DEADLINE_SECONDS - elapsed
        if remaining <= 0:
            break

        print(f"\n🔎 [{shop}] Attempt {attempt} (remaining: {round(remaining, 2)}s)")
        try:
            html = fetch_grt_html(timeout_seconds=remaining)
            p22, p24, last_updated = parse_grt_rates(html)
            print(f"✅ [{shop}] SCRAPE SUCCESS — 22k={p22}, 24k={p24}")
            return {
                "status":            "OK",
                "shop":              shop,
                "scrape_time_sgt":   now_sgt(),
                "price_22k_916":     p22,
                "price_24k_999":     p24,
                "shop_last_updated": last_updated,
            }
        except Exception as e:
            last_error = str(e)
            print(f"❌ [{shop}] Attempt {attempt} failed: {last_error}")
            backoff = 0.5 * (2 ** (attempt - 1))
            if (time.time() - start + backoff) < TOTAL_DEADLINE_SECONDS and attempt < MAX_ATTEMPTS:
                time.sleep(backoff)

    print(f"\n🚨 [{shop}] ALL ATTEMPTS FAILED")
    return {
        "status":          "FAILED",
        "shop":            shop,
        "scrape_time_sgt": now_sgt(),
        "error":           last_error or "Unknown error",
    }


# --------------------------------------------------
# Joyalukkas scraper (GraphQL API)
# Store header "sg" returns SG-specific rates in SGD
# --------------------------------------------------

def fetch_joyalukkas_rates(shop: str) -> dict:
    query = "{getgoldrates{metal_rate_time Data{GOLD_22KT_RATE GOLD_24KT_RATE}}}"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Store": "sg",
    }
    start      = time.time()
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        elapsed   = time.time() - start
        remaining = TOTAL_DEADLINE_SECONDS - elapsed
        if remaining <= 0:
            break

        print(f"\n🔎 [{shop}] Attempt {attempt} (remaining: {round(remaining, 2)}s)")
        try:
            r = requests.post(
                JOYALUKKAS_GQL,
                json={"query": query},
                headers=headers,
                timeout=remaining,
            )
            r.raise_for_status()
            gql_data = r.json()["data"]["getgoldrates"]
            entry    = gql_data["Data"][0]
            p22      = entry["GOLD_22KT_RATE"].strip()
            p24      = entry["GOLD_24KT_RATE"].strip()

            if not is_numberish(p22) or not is_numberish(p24):
                raise ValueError(f"Prices not numeric: 22k={p22}, 24k={p24}")

            last_updated = gql_data.get("metal_rate_time")
            print(f"✅ [{shop}] SCRAPE SUCCESS — 22k={p22}, 24k={p24}")
            return {
                "status":            "OK",
                "shop":              shop,
                "scrape_time_sgt":   now_sgt(),
                "price_22k_916":     p22,
                "price_24k_999":     p24,
                "shop_last_updated": last_updated,
            }

        except Exception as e:
            last_error = str(e)
            print(f"❌ [{shop}] Attempt {attempt} failed: {last_error}")
            backoff = 0.5 * (2 ** (attempt - 1))
            if (time.time() - start + backoff) < TOTAL_DEADLINE_SECONDS and attempt < MAX_ATTEMPTS:
                time.sleep(backoff)

    print(f"\n🚨 [{shop}] ALL ATTEMPTS FAILED")
    return {
        "status":          "FAILED",
        "shop":            shop,
        "scrape_time_sgt": now_sgt(),
        "error":           last_error or "Unknown error",
    }


# --------------------------------------------------
# Generic scraper with retry
# --------------------------------------------------

def scrape_with_retry(url: str, parser_fn, shop: str) -> dict:
    start      = time.time()
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        elapsed   = time.time() - start
        remaining = TOTAL_DEADLINE_SECONDS - elapsed

        if remaining <= 0:
            break

        print(f"\n🔎 [{shop}] Attempt {attempt} (remaining: {round(remaining, 2)}s)")

        try:
            html = fetch_html(url, timeout_seconds=remaining)
            p22, p24, last_updated = parser_fn(html)
            print(f"✅ [{shop}] SCRAPE SUCCESS — 22k={p22}, 24k={p24}")
            return {
                "status":           "OK",
                "shop":             shop,
                "scrape_time_sgt":  now_sgt(),
                "price_22k_916":    p22,
                "price_24k_999":    p24,
                "shop_last_updated": last_updated,
            }

        except Exception as e:
            last_error = str(e)
            print(f"❌ [{shop}] Attempt {attempt} failed: {last_error}")
            backoff = 0.5 * (2 ** (attempt - 1))
            if (time.time() - start + backoff) < TOTAL_DEADLINE_SECONDS and attempt < MAX_ATTEMPTS:
                time.sleep(backoff)

    print(f"\n🚨 [{shop}] ALL ATTEMPTS FAILED")
    return {
        "status":          "FAILED",
        "shop":            shop,
        "scrape_time_sgt": now_sgt(),
        "error":           last_error or "Unknown error",
    }


# --------------------------------------------------
# Build shop section (used inside the combined email)
# --------------------------------------------------

def build_shop_section(result: dict, last_prices: dict) -> str:
    shop = result["shop"]

    if result["status"] == "OK":
        p22 = result["price_22k_916"]
        p24 = result["price_24k_999"]

        change_22 = change_24 = ""
        if last_prices:
            change_22 = format_change(calculate_percentage_change(p22, last_prices.get("price_22k_916")))
            change_24 = format_change(calculate_percentage_change(p24, last_prices.get("price_24k_999")))

        line_22 = f"22k (916): S${p22}" + (f"\n{change_22}" if change_22 else "")
        line_24 = f"24k (999): S${p24}" + (f"\n{change_24}" if change_24 else "")

        return (
            f"🏪 {shop}\n"
            f"{line_22}\n"
            f"{line_24}\n\n"
            f"Last updated on source: {result.get('shop_last_updated', 'N/A')}\n"
            f"Job run time: {result['scrape_time_sgt']} (SGT)\n"
            f"Status: OK"
        )

    else:
        shop_url = SHOP_URLS.get(shop, "")
        url_line = f'\nCheck latest: <a href="{shop_url}" style="color:#c8a84b;">{shop_url}</a>' if shop_url else ""
        if last_prices and last_prices.get("price_22k_916") and last_prices.get("price_24k_999"):
            p22 = last_prices["price_22k_916"]
            p24 = last_prices["price_24k_999"]
            return (
                f"🏪 {shop}\n"
                f"22k (916): S${p22} (Old rate — server error)\n"
                f"24k (999): S${p24} (Old rate — server error)\n\n"
                f"Last updated on source: N/A\n"
                f"Job run time: {result['scrape_time_sgt']} (SGT)\n"
                f"Status: FAILED — {result.get('error')}"
                f"{url_line}"
            )
        return (
            f"🏪 {shop}\n"
            f"Status: FAILED\n"
            f"Error: {result.get('error')}\n"
            f"Job run time: {result['scrape_time_sgt']} (SGT)"
            f"{url_line}"
        )


# --------------------------------------------------
# Build combined email message
# --------------------------------------------------

def build_message(mustafa_result: dict, malabar_result: dict, joyalukkas_result: dict,
                  grt_result: dict,
                  mustafa_last: dict, malabar_last: dict, joyalukkas_last: dict,
                  grt_last: dict) -> str:

    mustafa_section    = build_shop_section(mustafa_result, mustafa_last)
    malabar_section    = build_shop_section(malabar_result, malabar_last)
    joyalukkas_section = build_shop_section(joyalukkas_result, joyalukkas_last)
    grt_section        = build_shop_section(grt_result, grt_last)

    return (
        f"📊 Gold Price Update (SGD)\n\n"
        f"{SEPARATOR}\n"
        f"{mustafa_section}\n"
        f"{SEPARATOR}\n\n"
        f"{SEPARATOR}\n"
        f"{malabar_section}\n"
        f"{SEPARATOR}\n\n"
        f"{SEPARATOR}\n"
        f"{joyalukkas_section}\n"
        f"{SEPARATOR}\n\n"
        f"{SEPARATOR}\n"
        f"{grt_section}\n"
        f"{SEPARATOR}\n\n"
        f"To unsubscribe: {SITE_URL}/unsubscribe\n"
        f"Questions? Contact us: alerts@goldnotifier.com"
    )


# --------------------------------------------------
# Send email notifications
# --------------------------------------------------

def send_email(to_email: str, subject: str, body: str,
               html_body: str | None = None,
               chart_bytes: bytes | None = None) -> bool:
    """
    Send a single email via Namecheap Private Email (SMTP + STARTTLS).

    Returns True on success, False on failure — never raises.
    """
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"]    = "Gold Notifier <alerts@goldnotifier.com>"
    msg["To"]      = to_email

    alt = MIMEMultipart("alternative")
    msg.attach(alt)
    alt.attach(MIMEText(body, "plain"))
    if html_body:
        alt.attach(MIMEText(html_body, "html"))

    if chart_bytes:
        img = MIMEImage(chart_bytes)
        img.add_header("Content-ID", "<goldchart>")
        img.add_header("Content-Disposition", "inline", filename="gold_prices.png")
        msg.attach(img)

    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("  Email skipped: EMAIL_USER or EMAIL_PASSWORD not set.")
        return False

    try:
        with smtplib.SMTP("mail.privateemail.com", 587, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"  ✉️  Sent to {to_email}")
        return True
    except Exception as e:
        print(f"  Email failed for {to_email}: {type(e).__name__}: {e}")
        return False


def send_email_to_all(message: str, chart_bytes: bytes | None = None):
    subscribers = get_subscribers()

    if not subscribers:
        print("No subscribers found. Skipping email.")
        return

    print(f"Sending to {len(subscribers)} subscriber(s)...")

    chart_tag = (
        '<img src="cid:goldchart" style="width:100%;max-width:680px;'
        'border-radius:8px;margin-bottom:20px;" alt="Gold price chart">'
        if chart_bytes else ""
    )

    html_body = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:24px;background:#070708;color:#e8dfc8;font-family:'Courier New',monospace;max-width:700px;">
  <h2 style="color:#c8a84b;margin-top:0;">&#x1F4CA; Gold Price Update (SGD)</h2>
  {chart_tag}
  <pre style="white-space:pre-wrap;font-size:13px;line-height:1.7;color:#e8dfc8;background:#111;padding:16px;border-radius:6px;border:1px solid #222;">{message}</pre>
</body>
</html>"""

    sgt_now = datetime.now(pytz.timezone("Asia/Singapore"))
    subject = f"Gold Prices \u00b7 {sgt_now.strftime('%-d %b %I:%M %p')}"

    for email in subscribers:
        send_email(email, subject, message, html_body, chart_bytes)
        time.sleep(1)


# --------------------------------------------------
# Main execution
# --------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape-only", action="store_true",
                        help="Scrape and save prices to Airtable — skip email")
    args = parser.parse_args()

    # Scrape all sources
    mustafa_result    = scrape_with_retry(MUSTAFA_URL, parse_mustafa_rates, "Mustafa Jewellery")
    malabar_result    = scrape_with_retry(MALABAR_URL, parse_malabar_rates, "Malabar Gold SG")
    joyalukkas_result = fetch_joyalukkas_rates("Joyalukkas SG")
    grt_result        = fetch_grt_rates("GRT Jewels SG")

    # Save prices to Airtable (only on success)
    if mustafa_result["status"] == "OK":
        save_prices(mustafa_result["price_22k_916"], mustafa_result["price_24k_999"], "Mustafa Jewellery")

    if malabar_result["status"] == "OK":
        save_prices(malabar_result["price_22k_916"], malabar_result["price_24k_999"], "Malabar Gold SG")

    if joyalukkas_result["status"] == "OK":
        save_prices(joyalukkas_result["price_22k_916"], joyalukkas_result["price_24k_999"], "Joyalukkas SG")

    if grt_result["status"] == "OK":
        save_prices(grt_result["price_22k_916"], grt_result["price_24k_999"], "GRT Jewels SG")

    if args.scrape_only:
        print("Scrape-only mode — prices saved, email skipped.")
    else:
        # Fetch last prices per shop for trend arrows
        mustafa_last    = get_last_prices("Mustafa Jewellery")
        malabar_last    = get_last_prices("Malabar Gold SG")
        joyalukkas_last = get_last_prices("Joyalukkas SG")
        grt_last        = get_last_prices("GRT Jewels SG")

        message = build_message(
            mustafa_result, malabar_result, joyalukkas_result, grt_result,
            mustafa_last, malabar_last, joyalukkas_last, grt_last,
        )

        print("\n" + SEPARATOR)
        print("📨 EMAIL TO SEND")
        print(SEPARATOR)
        print(message)
        print(SEPARATOR)

        price_history = get_price_history()
        chart_bytes   = generate_price_chart(price_history)
        send_email_to_all(message, chart_bytes)
