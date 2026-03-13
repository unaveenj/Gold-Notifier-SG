import streamlit as st
from pyairtable import Table

API_KEY = st.secrets["AIRTABLE_API_KEY"]
BASE_ID = st.secrets["AIRTABLE_BASE_ID"]

table = Table(API_KEY, BASE_ID, "subscribers")

st.set_page_config(page_title="Gold Price Alerts", page_icon="🪙")

st.title("🪙 Gold Price Email Alerts")

st.write("Subscribe to receive automated gold price updates.")

email_input = st.text_input("Enter your email")

if st.button("Subscribe"):

    email = email_input.strip().lower()

    if email == "":
        st.warning("Please enter an email address")
        st.stop()

    try:
        # Check for existing subscriber
        existing = table.all(formula=f"{{email}}='{email}'")

        if existing:
            st.warning("⚠️ Email already subscribed")
        else:
            table.create({"email": email})
            st.success("✅ Subscription successful!")

    except Exception as e:
        st.error(f"Database error: {e}")