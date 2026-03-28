"""
Test script — scrapes live prices and sends the full alert email to a single address.
Overrides the subscriber list so real subscribers are never contacted.
Run from repo root: python scraper/test_email.py
"""

import os
import sys

# Must be run from repo root so gold_bot imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import gold_bot

TEST_EMAIL = os.environ.get("TEST_EMAIL", "unaveenj@gmail.com")

# Patch BEFORE send_email_to_all is called — it calls get_subscribers() internally
gold_bot.get_subscribers = lambda: [TEST_EMAIL]

print(f"=== TEST RUN — email will go only to {TEST_EMAIL} ===\n")

# Mirror the __main__ block exactly
mustafa_result    = gold_bot.scrape_with_retry(gold_bot.MUSTAFA_URL, gold_bot.parse_mustafa_rates, "Mustafa Jewellery")
malabar_result    = gold_bot.scrape_with_retry(gold_bot.MALABAR_URL, gold_bot.parse_malabar_rates, "Malabar Gold SG")
joyalukkas_result = gold_bot.fetch_joyalukkas_rates("Joyalukkas SG")
grt_result        = gold_bot.fetch_grt_rates("GRT Jewels SG")

mustafa_last    = gold_bot.get_last_prices("Mustafa Jewellery")
malabar_last    = gold_bot.get_last_prices("Malabar Gold SG")
joyalukkas_last = gold_bot.get_last_prices("Joyalukkas SG")
grt_last        = gold_bot.get_last_prices("GRT Jewels SG")

message = gold_bot.build_message(
    mustafa_result, malabar_result, joyalukkas_result, grt_result,
    mustafa_last, malabar_last, joyalukkas_last, grt_last,
)

print(message)

price_history = gold_bot.get_price_history()
chart_bytes   = gold_bot.generate_price_chart(price_history)

gold_bot.send_email_to_all(message, chart_bytes)

print(f"\n=== Done. Check {TEST_EMAIL} for the test email. ===")
