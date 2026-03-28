"""
Daily Alert — sends the 5pm SGT email to all subscribers.
Compares today's latest scraped prices against the 24-hour average
from Airtable price history.

Run via: python notifications/daily_alert.py
"""

import os
import time
from datetime import datetime, timedelta, timezone

import pytz
from pyairtable import Api

from gold_bot import (
    get_price_history,
    generate_price_chart,
    send_email_to_all,
    get_subscribers,
    SEPARATOR,
    SITE_URL,
    SGT,
)
from price_tracker import calculate_percentage_change, format_change

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]


def get_24h_averages() -> dict:
    """
    Returns the 24h average prices per shop from Airtable history.
    Structure: { shop_name: { "p22": float, "p24": float } }
    """
    history = get_price_history()
    cutoff  = datetime.now(timezone.utc).astimezone(SGT) - timedelta(hours=24)
    window  = [r for r in history if r["dt"] >= cutoff]

    averages = {}
    shops    = set(r["shop"] for r in window)
    for shop in shops:
        shop_data = [r for r in window if r["shop"] == shop]
        avg_22    = sum(r["p22"] for r in shop_data) / len(shop_data)
        avg_24    = sum(r["p24"] for r in shop_data) / len(shop_data)
        averages[shop] = {"p22": round(avg_22, 2), "p24": round(avg_24, 2)}

    return averages


def get_latest_prices() -> dict:
    """
    Returns the most recently scraped price per shop.
    Structure: { shop_name: { "p22": float, "p24": float } }
    """
    history = get_price_history()
    latest  = {}
    for r in reversed(history):  # history is sorted ascending
        shop = r["shop"]
        if shop not in latest:
            latest[shop] = {"p22": r["p22"], "p24": r["p24"]}
    return latest


def build_daily_message(latest: dict, averages: dict) -> str:
    sgt_now = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")
    lines   = [f"📊 Daily Gold Price Update (SGD)\n", f"As at {sgt_now} SGT\n"]

    shops = [
        "Mustafa Jewellery",
        "Malabar Gold SG",
        "Joyalukkas SG",
        "GRT Jewels SG",
    ]

    for shop in shops:
        lines.append(SEPARATOR)
        if shop not in latest:
            lines.append(f"🏪 {shop}\nStatus: No data scraped yet\n")
            continue

        p22 = latest[shop]["p22"]
        p24 = latest[shop]["p24"]

        avg = averages.get(shop)
        if avg:
            chg22 = format_change(calculate_percentage_change(str(p22), str(avg["p22"])))
            chg24 = format_change(calculate_percentage_change(str(p24), str(avg["p24"])))
            avg_line = (
                f"  24h avg: 22k S${avg['p22']}  |  24k S${avg['p24']}"
            )
        else:
            chg22 = chg24 = ""
            avg_line = "  24h avg: insufficient data"

        lines.append(
            f"🏪 {shop}\n"
            f"  22k (916): S${p22}" + (f"  {chg22}" if chg22 else "") + "\n"
            f"  24k (999): S${p24}" + (f"  {chg24}" if chg24 else "") + "\n"
            f"{avg_line}\n"
        )

    lines.append(SEPARATOR)
    lines.append(f"\nTo unsubscribe: {SITE_URL}/unsubscribe")
    lines.append("Questions? Contact us: alerts@goldnotifier.com")
    return "\n".join(lines)


if __name__ == "__main__":
    print("=== Daily Alert ===")

    latest   = get_latest_prices()
    averages = get_24h_averages()

    print(f"Latest prices:   {latest}")
    print(f"24h averages:    {averages}")

    message = build_daily_message(latest, averages)

    print("\n" + SEPARATOR)
    print("📨 EMAIL TO SEND")
    print(SEPARATOR)
    print(message)
    print(SEPARATOR)

    history     = get_price_history()
    chart_bytes = generate_price_chart(history)

    send_email_to_all(message, chart_bytes)
    print("=== Done ===")
