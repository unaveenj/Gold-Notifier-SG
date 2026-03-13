import streamlit as st
from pyairtable import Table

# ── Airtable ───────────────────────────────────────────────────────────────────
API_KEY = st.secrets["AIRTABLE_API_KEY"]
BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
table   = Table(API_KEY, BASE_ID, "subscribers")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GoldAlert SG",
    page_icon="🪙",
    layout="centered",
)

# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_subscriber_count():
    try:
        return len(table.all())
    except Exception:
        return 0

@st.cache_data(ttl=60)
def get_notifications_count():
    try:
        return len(Table(API_KEY, BASE_ID, "notifications").all())
    except Exception:
        return 0

def subscribe_email(email: str):
    if table.all(formula=f"{{email}}='{email}'"):
        return "duplicate"
    table.create({"email": email})
    return "success"

# ── Hero ───────────────────────────────────────────────────────────────────────
st.title("🪙 Gold Price Alerts for Singapore")
st.subheader("Never miss the best time to buy gold.")
st.caption("Track jewellery gold prices automatically and receive alerts when the market moves.")

st.divider()

# ── Subscribe form ─────────────────────────────────────────────────────────────
st.subheader("Get Notified")

email_input = st.text_input(
    "Your email address",
    placeholder="you@example.com",
    key="sub_email",
)

if st.button("Subscribe to Gold Alerts", type="primary", use_container_width=True):
    email = email_input.strip().lower()
    if not email:
        st.warning("Please enter your email address.")
    elif "@" not in email or "." not in email.split("@")[-1]:
        st.warning("Enter a valid email address.")
    else:
        try:
            result = subscribe_email(email)
            if result == "duplicate":
                st.info("You're already subscribed — alerts are on their way.")
            else:
                st.success("Subscribed! Your first alert will arrive soon.")
                st.cache_data.clear()
        except Exception as e:
            st.error(f"Something went wrong. Try again. ({e})")

st.caption("🔒 No spam · 📊 Price changes only · 🇸🇬 SGD")

st.divider()

# ── Live metrics ───────────────────────────────────────────────────────────────
st.subheader("Live Metrics")

subscribers   = get_subscriber_count()
notifications = get_notifications_count()

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Active Subscribers", value=subscribers)

with col2:
    st.metric(label="Notifications Sent", value=notifications)

st.divider()

# ── Value proposition ──────────────────────────────────────────────────────────
st.subheader("💰 Why it matters")
st.markdown("### Save up to **S$350** per 100g by timing your purchase.")
st.write(
    "Gold prices fluctuate daily. Our alerts help you avoid buying at peak prices — "
    "so you only act when the market moves in your favour."
)

st.divider()

# ── How it works ───────────────────────────────────────────────────────────────
st.subheader("How it works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**① Subscribe**")
    st.caption("Enter your email once. No account, no password.")

with col2:
    st.markdown("**② We Monitor**")
    st.caption("Our bot checks Mustafa Jewellery prices every hour, around the clock.")

with col3:
    st.markdown("**③ You're Alerted**")
    st.caption("Receive an email the moment the price shifts. Act fast, buy smart.")

st.divider()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.caption("GoldAlert SG · Powered by Mustafa Jewellery live data · Free · Singapore")
