import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from pyairtable import Table
from dotenv import load_dotenv
from pathlib import Path

# --------------------------------------------------
# Load .env only for local development
# GitHub Actions will supply environment variables
# --------------------------------------------------

if not os.getenv("AIRTABLE_API_KEY"):
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# --------------------------------------------------
# Environment variables
# --------------------------------------------------

AIRTABLE_API_KEY  = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID  = os.getenv("AIRTABLE_BASE_ID")
GMAIL_USER        = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# --------------------------------------------------
# Config
# --------------------------------------------------

MUSTAFA_URL    = "https://mustafajewellery.com/"
MALABAR_URL    = "https://www.malabargoldanddiamonds.com/stores/singapore"
JOYALUKKAS_GQL = "https://www.joyalukkas.com/graphql"
MAX_ATTEMPTS = 3
TOTAL_DEADLINE_SECONDS = 15
USER_AGENT   = "Mozilla/5.0 (compatible; GoldRateBot/1.0)"
SEPARATOR    = "=" * 33

SGT = pytz.timezone("Asia/Singapore")

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


def fetch_html(url: str, timeout_seconds: float) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
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
        emoji22 = emoji24 = ""

        if last_prices:
            try:
                if float(p22) > float(last_prices["price_22k_916"]):
                    emoji22 = " ↑"
                elif float(p22) < float(last_prices["price_22k_916"]):
                    emoji22 = " ↓"
            except Exception:
                pass
            try:
                if float(p24) > float(last_prices["price_24k_999"]):
                    emoji24 = " ↑"
                elif float(p24) < float(last_prices["price_24k_999"]):
                    emoji24 = " ↓"
            except Exception:
                pass

        return (
            f"🏪 {shop}\n"
            f"22k (916): S${p22}{emoji22}\n"
            f"24k (999): S${p24}{emoji24}\n\n"
            f"Last updated on source: {result.get('shop_last_updated', 'N/A')}\n"
            f"Job run time: {result['scrape_time_sgt']} (SGT)\n"
            f"Status: OK"
        )

    else:
        return (
            f"🏪 {shop}\n"
            f"Status: FAILED\n"
            f"Error: {result.get('error')}\n"
            f"Job run time: {result['scrape_time_sgt']} (SGT)"
        )


# --------------------------------------------------
# Build combined email message
# --------------------------------------------------

def build_message(mustafa_result: dict, malabar_result: dict, joyalukkas_result: dict,
                  mustafa_last: dict, malabar_last: dict, joyalukkas_last: dict) -> str:

    mustafa_section    = build_shop_section(mustafa_result, mustafa_last)
    malabar_section    = build_shop_section(malabar_result, malabar_last)
    joyalukkas_section = build_shop_section(joyalukkas_result, joyalukkas_last)

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
        f"{SEPARATOR}"
    )


# --------------------------------------------------
# Send email notifications
# --------------------------------------------------

def send_email_to_all(message: str):
    subscribers = get_subscribers()

    if not subscribers:
        print("No subscribers found. Skipping email.")
        return

    print(f"Sending to {len(subscribers)} subscriber(s)...")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)

            for email in subscribers:
                msg = MIMEText(message)
                msg["Subject"] = "📊 Gold Price Update"
                msg["From"]    = GMAIL_USER
                msg["To"]      = email

                server.send_message(msg)
                print(f"  ✉️  Sent to {email}")
                time.sleep(1)  # Avoid Gmail rate limiting

    except Exception as e:
        print("Email sending failed:", e)


# --------------------------------------------------
# Main execution
# --------------------------------------------------

if __name__ == "__main__":

    # Scrape all sources
    mustafa_result    = scrape_with_retry(MUSTAFA_URL, parse_mustafa_rates, "Mustafa Jewellery")
    malabar_result    = scrape_with_retry(MALABAR_URL, parse_malabar_rates, "Malabar Gold SG")
    joyalukkas_result = fetch_joyalukkas_rates("Joyalukkas SG")

    # Fetch last prices per shop for trend arrows
    mustafa_last    = get_last_prices("Mustafa Jewellery")
    malabar_last    = get_last_prices("Malabar Gold SG")
    joyalukkas_last = get_last_prices("Joyalukkas SG")

    # Build and send combined email
    message = build_message(
        mustafa_result, malabar_result, joyalukkas_result,
        mustafa_last, malabar_last, joyalukkas_last,
    )

    print("\n" + SEPARATOR)
    print("📨 EMAIL TO SEND")
    print(SEPARATOR)
    print(message)
    print(SEPARATOR)

    send_email_to_all(message)

    # Save prices to Airtable (only on success)
    if mustafa_result["status"] == "OK":
        save_prices(mustafa_result["price_22k_916"], mustafa_result["price_24k_999"], "Mustafa Jewellery")

    if malabar_result["status"] == "OK":
        save_prices(malabar_result["price_22k_916"], malabar_result["price_24k_999"], "Malabar Gold SG")

    if joyalukkas_result["status"] == "OK":
        save_prices(joyalukkas_result["price_22k_916"], joyalukkas_result["price_24k_999"], "Joyalukkas SG")
