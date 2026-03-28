import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

import pytz
from pyairtable import Table
from dotenv import load_dotenv

# --------------------------------------------------
# Load .env only for local development
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

SITE_URL = os.getenv("SITE_URL", "https://www.goldnotifier.com")

# --------------------------------------------------
# Announcement content — edit here before triggering
# --------------------------------------------------

ANNOUNCEMENT_SUBJECT = "Gold Notifier — Daily Alerts & 24h Price Comparison"

ANNOUNCEMENT_BODY = """Dear Subscriber,

Thank you for being part of Gold Notifier. We have made some improvements
to how alerts work and wanted to keep you in the loop.

WHAT'S CHANGED
--------------

Once-a-Day Alert at 5 PM SGT
Based on feedback, we have moved from sending alerts every 2 hours to
one daily summary at 5 PM SGT. This gives you a clean end-of-day
snapshot without filling up your inbox.

24-Hour Price Comparison
Each alert now compares today's prices against the 24-hour average
across all 4 jewellers. You will see the current price alongside the
percentage change so you can quickly spot whether prices are trending
up or down on the day.

We Still Scrape Every 2 Hours
Price data is still collected every 2 hours throughout the day so the
24-hour average is accurate — you just receive one concise email at 5 PM.

----------
As always, Gold Notifier is completely free. No app, no login — just
your inbox.

Warm regards,
The Gold Notifier Team
alerts@goldnotifier.com
https://www.goldnotifier.com

To unsubscribe: https://www.goldnotifier.com/unsubscribe
"""
SGT      = pytz.timezone("Asia/Singapore")

# --------------------------------------------------
# Airtable
# --------------------------------------------------

def get_subscribers() -> list[str]:
    table   = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "subscribers")
    records = table.all()
    return [r["fields"]["email"] for r in records if "email" in r.get("fields", {})]


# --------------------------------------------------
# Email
# --------------------------------------------------

def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send a plain-text announcement email. Returns True on success."""
    html_body = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:24px;background:#070708;color:#e8dfc8;font-family:'Courier New',monospace;max-width:700px;">
  <h2 style="color:#c8a84b;margin-top:0;">Gold Notifier — Announcement</h2>
  <pre style="white-space:pre-wrap;font-size:13px;line-height:1.7;color:#e8dfc8;background:#111;padding:16px;border-radius:6px;border:1px solid #222;">{body}</pre>
  <p style="font-size:11px;color:#666;margin-top:24px;">
    To unsubscribe: <a href="{SITE_URL}/unsubscribe" style="color:#c8a84b;">{SITE_URL}/unsubscribe</a><br>
    Questions? Contact us: <a href="mailto:alerts@goldnotifier.com" style="color:#c8a84b;">alerts@goldnotifier.com</a>
  </p>
</body>
</html>"""

    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("  Email skipped: EMAIL_USER or EMAIL_PASSWORD not set.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = "Gold Notifier <alerts@goldnotifier.com>"
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("mail.privateemail.com", 587, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"  Sent to {to_email}")
        return True
    except Exception as e:
        print(f"  Failed for {to_email}: {type(e).__name__}: {e}")
        return False


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    subscribers = get_subscribers()
    if not subscribers:
        print("No subscribers found. Exiting.")
        raise SystemExit(0)

    print(f"Sending announcement to {len(subscribers)} subscriber(s)...")
    print(f"Subject : {ANNOUNCEMENT_SUBJECT}")
    print(f"Body    : {ANNOUNCEMENT_BODY[:80]}{'...' if len(ANNOUNCEMENT_BODY) > 80 else ''}")
    print()

    sent = failed = 0
    for email in subscribers:
        ok = send_email(email, ANNOUNCEMENT_SUBJECT, ANNOUNCEMENT_BODY)
        if ok:
            sent += 1
        else:
            failed += 1
        time.sleep(1)

    print()
    print(f"Done. Sent: {sent}  Failed: {failed}")
