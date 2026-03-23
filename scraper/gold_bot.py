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

SITE_URL       = os.getenv("SITE_URL", "https://goldalert-sg.vercel.app")
MUSTAFA_URL    = "https://mustafajewellery.com/"
MALABAR_URL    = "https://www.malabargoldanddiamonds.com/stores/singapore"
JOYALUKKAS_GQL = "https://www.joyalukkas.com/graphql"
GRT_URL        = "https://www.grtjewels.com/asia/"
MAX_ATTEMPTS = 3
TOTAL_DEADLINE_SECONDS = 15
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
    """Fetch GRT page with full browser headers to bypass their bot detection."""
    r = requests.get(GRT_URL, headers=BROWSER_HEADERS, timeout=timeout_seconds)
    r.raise_for_status()
    return r.text


def parse_grt_rates(html: str):
    """
    Navigate the exact DOM path confirmed via Chrome DevTools XPath:
      /html/body/div[1]/div[1]/header/div[4]/nav/div/ul/li[7]/ul/li[2]/a
                                                              ^^^^
                                             li[7] = "Today's Rate" nav item
                                             Its submenu has:
                                               li[1] = 22K rate
                                               li[2] = 24K rate  ← XPath the user found
    """
    soup = BeautifulSoup(html, "html.parser")

    try:
        # Walk the exact path: header > div[4] > nav > div > ul > li[7] > ul
        header   = soup.find("header")
        div4     = header.find_all("div", recursive=False)[3]   # div[4], 0-indexed = [3]
        nav      = div4.find("nav")
        nav_div  = nav.find("div")
        main_ul  = nav_div.find("ul")
        li7      = main_ul.find_all("li", recursive=False)[6]   # li[7], 0-indexed = [6]
        sub_ul   = li7.find("ul")
        sub_lis  = sub_ul.find_all("li", recursive=False)

        # Extract text from all sub-items and match 22K / 24K by label
        p22 = p24 = None
        last_updated = None

        for li in sub_lis:
            text = li.get_text(separator=" ", strip=True)
            # Confirmed format: "GOLD - 22KT -  1. g  -  SGD  $ 169.90"
            if re.search(r"22\s*KT|22\s*[Kk]|916", text):
                p22 = _extract_price_from_text(text)
            elif re.search(r"24\s*KT|24\s*[Kk]|999", text):
                p24 = _extract_price_from_text(text)

        # Fallback: if labels aren't found, assign by position (li[1]=22K, li[2]=24K)
        if (p22 is None or p24 is None) and len(sub_lis) >= 2:
            p22 = p22 or _extract_price_from_text(sub_lis[0].get_text(strip=True))
            p24 = p24 or _extract_price_from_text(sub_lis[1].get_text(strip=True))

    except (AttributeError, IndexError) as e:
        raise ValueError(
            f"GRT: DOM path navigation failed — page structure may have changed. "
            f"Re-check XPath in DevTools. Error: {e}"
        )

    if not p22 or not p24:
        raise ValueError(
            "GRT: Could not extract 22K/24K prices from the Today's Rate dropdown. "
            f"Sub-menu text: {[li.get_text(strip=True) for li in sub_lis]}"
        )

    if not is_numberish(p22) or not is_numberish(p24):
        raise ValueError(f"GRT: Prices not numeric. Got 22k={p22}, 24k={p24}")

    # Look for a date/time string anywhere on the page
    ts_match = re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", html)
    if ts_match:
        last_updated = ts_match.group(0)

    return p22, p24, last_updated


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
        f"To unsubscribe: {SITE_URL}/unsubscribe"
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
    grt_result        = fetch_grt_rates("GRT Jewels SG")

    # Fetch last prices per shop for trend arrows
    mustafa_last    = get_last_prices("Mustafa Jewellery")
    malabar_last    = get_last_prices("Malabar Gold SG")
    joyalukkas_last = get_last_prices("Joyalukkas SG")
    grt_last        = get_last_prices("GRT Jewels SG")

    # Build and send combined email
    message = build_message(
        mustafa_result, malabar_result, joyalukkas_result, grt_result,
        mustafa_last, malabar_last, joyalukkas_last, grt_last,
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

    if grt_result["status"] == "OK":
        save_prices(grt_result["price_22k_916"], grt_result["price_24k_999"], "GRT Jewels SG")
