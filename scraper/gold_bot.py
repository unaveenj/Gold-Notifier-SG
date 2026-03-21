import os
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

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# --------------------------------------------------
# Config
# --------------------------------------------------

URL = "https://mustafajewellery.com/"
MAX_ATTEMPTS = 3
TOTAL_DEADLINE_SECONDS = 10
USER_AGENT = "Mozilla/5.0 (compatible; GoldRateBot/1.0)"

SGT = pytz.timezone("Asia/Singapore")

# --------------------------------------------------
# Airtable connection
# --------------------------------------------------

airtable = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "subscribers")
airtable_prices = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "prices")

# --------------------------------------------------
# Airtable subscriber fetch
# --------------------------------------------------

def get_subscribers():
    records = airtable.all()
    emails = []

    for record in records:
        fields = record.get("fields", {})
        if "email" in fields:
            emails.append(fields["email"])

    return emails


# --------------------------------------------------
# Airtable last prices fetch
# --------------------------------------------------

def get_last_prices():
    records = airtable_prices.all()
    if not records:
        print("No previous prices found in Airtable.")
        return None
    # Sort by id descending to get latest
    records.sort(key=lambda r: r['id'], reverse=True)
    fields = records[0]['fields']
    print(f"Last prices fetched: {fields}")
    return {
        'price_22k_916': fields.get('price_22k_916'),
        'price_24k_999': fields.get('price_24k_999'),
    }


# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def now_sgt():
    return datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")


def fetch_html(timeout_seconds: float) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    r = requests.get(URL, headers=headers, timeout=timeout_seconds)
    r.raise_for_status()
    return r.text


def must_text(tag, label: str) -> str:

    if tag is None:
        raise ValueError(f"Missing element: {label}")

    value = tag.get_text(strip=True)

    if not value:
        raise ValueError(f"Empty value for: {label}")

    return value


def is_numberish(x: str) -> bool:
    try:
        float(x)
        return True
    except:
        return False


# --------------------------------------------------
# Parse gold prices
# --------------------------------------------------

def parse_gold_rates(html: str):

    soup = BeautifulSoup(html, "html.parser")

    p22_tag = soup.find(id="22k_price1")
    p24_tag = soup.find(id="24k_price1")
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
# Scrape with retry logic
# --------------------------------------------------

def scrape_with_retry():

    start = time.time()
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        elapsed = time.time() - start
        remaining = TOTAL_DEADLINE_SECONDS - elapsed

        if remaining <= 0:
            break

        print(f"\n🔎 Attempt {attempt} (remaining time: {round(remaining, 2)}s)")

        try:

            html = fetch_html(timeout_seconds=remaining)
            p22, p24, last_updated = parse_gold_rates(html)

            print("✅ SCRAPE SUCCESS")

            return {
                "status": "OK",
                "scrape_time_sgt": now_sgt(),
                "price_22k_916": p22,
                "price_24k_999": p24,
                "shop_last_updated": last_updated,
            }

        except Exception as e:

            last_error = str(e)
            print(f"❌ Attempt {attempt} failed: {last_error}")

            backoff = 0.5 * (2 ** (attempt - 1))

            if (
                (time.time() - start + backoff) < TOTAL_DEADLINE_SECONDS
                and attempt < MAX_ATTEMPTS
            ):
                time.sleep(backoff)

    print("\n🚨 ALL ATTEMPTS FAILED")

    return {
        "status": "FAILED",
        "scrape_time_sgt": now_sgt(),
        "error": last_error or "Unknown error",
    }


# --------------------------------------------------
# Build email message
# --------------------------------------------------

def build_message(result: dict, last_prices: dict = None) -> str:

    if result["status"] == "OK":

        p22 = result['price_22k_916']
        p24 = result['price_24k_999']
        emoji22 = ''
        emoji24 = ''

        if last_prices:
            try:
                last22 = float(last_prices['price_22k_916'])
                curr22 = float(p22)
                if curr22 > last22:
                    emoji22 = ' ↑'
                elif curr22 < last22:
                    emoji22 = ' ↓'
                print(f"22k: last={last22}, curr={curr22}, emoji='{emoji22}'")
            except Exception as e:
                print(f"Error comparing 22k prices: {e}")
                pass
            try:
                last24 = float(last_prices['price_24k_999'])
                curr24 = float(p24)
                if curr24 > last24:
                    emoji24 = ' ↑'
                elif curr24 < last24:
                    emoji24 = ' ↓'
                print(f"24k: last={last24}, curr={curr24}, emoji='{emoji24}'")
            except Exception as e:
                print(f"Error comparing 24k prices: {e}")
                pass

        return (
            "Gold Price Update (SGD)\n"
            f"22k (916): {p22}{emoji22}\n"
            f"24k (999): {p24}{emoji24}\n\n"
            f"Last updated on source: {result.get('shop_last_updated')}\n"
            f"Job run time: {result['scrape_time_sgt']} (SGT)\n"
            "Status: OK"
        )

    else:

        return (
            "Gold Price Update (SGD) - STALE\n\n"
            f"Job run time: {result['scrape_time_sgt']} (SGT)\n"
            "Status: FAILED\n"
            f"Error: {result.get('error')}"
        )


# --------------------------------------------------
# Send email notifications
# --------------------------------------------------

def send_email_to_all(message):

    subscribers = get_subscribers()

    if not subscribers:
        print("No subscribers found. Skipping email.")
        return

    print(f"Subscribers found: {len(subscribers)}")
    print("Sending emails...")

    try:

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:

            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)

            for email in subscribers:

                msg = MIMEText(message)
                msg["Subject"] = "📊 Gold Price Update"
                msg["From"] = GMAIL_USER
                msg["To"] = email

                server.send_message(msg)

                print(f"Email sent to {email}")

                # Prevent Gmail rate limiting
                time.sleep(1)

    except Exception as e:
        print("Email sending failed:", e)


# --------------------------------------------------
# Main execution
# --------------------------------------------------

if __name__ == "__main__":

    result = scrape_with_retry()
    last_prices = get_last_prices()
    message = build_message(result, last_prices)

    print("\n==============================")
    print("📨 MESSAGE TO SEND")
    print("==============================")
    print(message)
    print("==============================")

    send_email_to_all(message)

    # Update prices if scrape was successful
    if result["status"] == "OK":
        try:
            airtable_prices.create({
                'price_22k_916': result['price_22k_916'],
                'price_24k_999': result['price_24k_999'],
            })
            print("Prices updated in Airtable.")
        except Exception as e:
            print("Failed to update prices:", e)