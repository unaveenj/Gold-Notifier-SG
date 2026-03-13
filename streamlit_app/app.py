import streamlit as st
import streamlit.components.v1 as components
from pyairtable import Table

# ── Airtable ───────────────────────────────────────────────────────────────────
API_KEY = st.secrets["AIRTABLE_API_KEY"]
BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
table   = Table(API_KEY, BASE_ID, "subscribers")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GoldAlert SG",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Data helpers ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_subscriber_count():
    try:
        return len(table.all())
    except Exception:
        return 0


@st.cache_data(ttl=60)
def get_notifications_count():
    try:
        notif_table = Table(API_KEY, BASE_ID, "notifications")
        return len(notif_table.all())
    except Exception:
        return 0


def subscribe_email(email: str):
    existing = table.all(formula=f"{{email}}='{email}'")
    if existing:
        return "duplicate"
    table.create({"email": email})
    return "success"


# ── Global CSS injection ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500&family=DM+Mono:wght@300;400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

/* ── CSS variables ── */
:root {
  --gold:          #c8a84b;
  --gold-light:    #e4c56a;
  --gold-dim:      rgba(200,168,75,0.15);
  --gold-glow:     rgba(200,168,75,0.08);
  --bg:            #050507;
  --surface:       #0b0b0f;
  --surface-raised:#0f0f14;
  --border:        rgba(200,168,75,0.12);
  --border-subtle: rgba(255,255,255,0.05);
  --text:          #f2ede8;
  --text-muted:    rgba(242,237,232,0.45);
  --text-faint:    rgba(242,237,232,0.2);
  --font-display:  'Cormorant Garamond', Georgia, serif;
  --font-mono:     'DM Mono', 'Courier New', monospace;
  --font-body:     'Outfit', system-ui, sans-serif;
  --radius:        16px;
  --radius-sm:     10px;
  --shadow-gold:   0 0 40px rgba(200,168,75,0.12);
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Global ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
}

/* ── Hide chrome ── */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarCollapsedControl"],
footer, #MainMenu { display: none !important; }

/* ── Remove default padding ── */
[data-testid="stAppViewContainer"] > .main { padding: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 99px; }

/* ── Email input ── */
[data-testid="stTextInput"] {
  margin-bottom: 0.75rem;
}
[data-testid="stTextInput"] label {
  display: none !important;
}
[data-testid="stTextInput"] input {
  background: rgba(200,168,75,0.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
  font-size: 0.95rem !important;
  font-weight: 400 !important;
  padding: 0.85rem 1.1rem !important;
  letter-spacing: 0.01em !important;
  transition: border-color 0.25s, box-shadow 0.25s !important;
  caret-color: var(--gold) !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: rgba(200,168,75,0.45) !important;
  box-shadow: 0 0 0 3px rgba(200,168,75,0.08), 0 0 20px rgba(200,168,75,0.06) !important;
  outline: none !important;
  background: rgba(200,168,75,0.06) !important;
}
[data-testid="stTextInput"] input::placeholder {
  color: var(--text-faint) !important;
  font-style: italic;
}

/* ── Button ── */
[data-testid="stButton"] > button {
  background: transparent !important;
  border: 1px solid var(--gold) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--gold) !important;
  font-family: var(--font-body) !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  padding: 0.85rem 1.5rem !important;
  width: 100% !important;
  position: relative !important;
  overflow: hidden !important;
  transition: color 0.3s, background 0.3s, box-shadow 0.3s !important;
}
[data-testid="stButton"] > button::before {
  content: '' !important;
  position: absolute !important;
  inset: 0 !important;
  background: linear-gradient(135deg, var(--gold), #a07830) !important;
  opacity: 0 !important;
  transition: opacity 0.3s !important;
}
[data-testid="stButton"] > button:hover {
  color: #050507 !important;
  box-shadow: 0 0 30px rgba(200,168,75,0.25) !important;
}
[data-testid="stButton"] > button:hover::before { opacity: 1 !important; }
[data-testid="stButton"] > button span { position: relative; z-index: 1; }

/* ── Alerts ── */
[data-testid="stAlert"] {
  background: rgba(200,168,75,0.05) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-muted) !important;
  font-family: var(--font-body) !important;
  font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Flip clock component ───────────────────────────────────────────────────────
def flip_clock_component(subscribers: int, notifications: int) -> None:
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;500;600&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  background: transparent;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 260px;
  padding: 1.5rem;
  font-family: 'Outfit', sans-serif;
}}

.metrics-wrap {{
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
  max-width: 720px;
}}

.metric-card {{
  flex: 1;
  min-width: 260px;
  max-width: 320px;
  background: #0b0b0f;
  border: 1px solid rgba(200,168,75,0.14);
  border-radius: 18px;
  padding: 2rem 2rem 1.75rem;
  position: relative;
  overflow: hidden;
}}

/* Corner accent */
.metric-card::before {{
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 60px; height: 60px;
  background: linear-gradient(135deg, rgba(200,168,75,0.12) 0%, transparent 60%);
  border-radius: 0 0 60px 0;
}}

.metric-card::after {{
  content: '';
  position: absolute;
  bottom: -40px; right: -40px;
  width: 120px; height: 120px;
  background: radial-gradient(circle, rgba(200,168,75,0.06) 0%, transparent 70%);
  pointer-events: none;
}}

.metric-label {{
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(200,168,75,0.6);
  margin-bottom: 1.4rem;
  display: flex;
  align-items: center;
  gap: 8px;
}}

.metric-label::before {{
  content: '';
  width: 16px; height: 1px;
  background: rgba(200,168,75,0.4);
}}

/* ── Flip clock ── */
.flip-row {{
  display: flex;
  align-items: center;
  gap: 5px;
  min-height: 78px;
}}

.flip-sep {{
  font-family: 'DM Mono', monospace;
  font-size: 2.4rem;
  font-weight: 400;
  color: rgba(200,168,75,0.2);
  line-height: 1;
  margin: 0 1px;
  align-self: center;
  padding-bottom: 4px;
}}

.flip-digit {{
  position: relative;
  width: 50px;
  height: 76px;
  perspective: 300px;
}}

/* Two static halves */
.face {{
  position: absolute;
  left: 0; right: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #111118;
  border: 1px solid rgba(200,168,75,0.1);
}}

.face-top {{
  top: 0; height: 50%;
  border-radius: 10px 10px 0 0;
  border-bottom: 1px solid rgba(0,0,0,0.6);
  align-items: flex-end;
}}

.face-bottom {{
  bottom: 0; height: 50%;
  border-radius: 0 0 10px 10px;
  border-top: none;
  align-items: flex-start;
}}

.face .num {{
  font-family: 'DM Mono', monospace;
  font-size: 2.8rem;
  font-weight: 400;
  color: #f2ede8;
  line-height: 1;
  letter-spacing: -0.04em;
  user-select: none;
  position: absolute;
}}

.face-top .num  {{ top: 50%; transform: translateY(-50%); }}
.face-bottom .num {{ top: -50%; transform: translateY(-50%) translateY(76px); }}

/* Animated flap */
.flap {{
  position: absolute;
  left: 0; right: 0;
  top: 0; height: 50%;
  overflow: hidden;
  transform-origin: bottom center;
  transform-style: preserve-3d;
  border-radius: 10px 10px 0 0;
  border: 1px solid rgba(200,168,75,0.1);
  border-bottom: none;
  background: #111118;
  z-index: 10;
}}

.flap.animate {{
  animation: flipFlap 0.5s cubic-bezier(0.4,0,0.2,1) forwards;
}}

@keyframes flipFlap {{
  0%   {{ transform: rotateX(0deg); box-shadow: none; }}
  40%  {{ box-shadow: 0 8px 20px rgba(0,0,0,0.6); }}
  100% {{ transform: rotateX(-180deg); box-shadow: none; }}
}}

.flap .num {{
  font-family: 'DM Mono', monospace;
  font-size: 2.8rem;
  font-weight: 400;
  color: #f2ede8;
  line-height: 1;
  letter-spacing: -0.04em;
  user-select: none;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) translateY(-50%) translateY(38px);
}}

/* Entrance animation */
@keyframes slideUp {{
  from {{ opacity:0; transform: translateY(16px); }}
  to   {{ opacity:1; transform: translateY(0); }}
}}

.flip-digit {{
  opacity: 0;
  animation: slideUp 0.5s cubic-bezier(0.4,0,0.2,1) forwards;
}}

.metric-foot {{
  margin-top: 1.25rem;
  display: flex;
  align-items: center;
  gap: 7px;
}}

.live-dot {{
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34,197,94,0.9);
  animation: blink 2.4s ease-in-out infinite;
  flex-shrink: 0;
}}

@keyframes blink {{
  0%,100% {{ opacity:1; }}
  50%      {{ opacity:0.35; }}
}}

.live-text {{
  font-size: 0.7rem;
  color: rgba(242,237,232,0.28);
  letter-spacing: 0.03em;
}}
</style>
</head>
<body>
<div class="metrics-wrap">

  <!-- Subscribers -->
  <div class="metric-card">
    <div class="metric-label">Active Subscribers</div>
    <div class="flip-row" id="subs-row"></div>
    <div class="metric-foot">
      <div class="live-dot"></div>
      <span class="live-text">Live · refreshes every 60 seconds</span>
    </div>
  </div>

  <!-- Notifications -->
  <div class="metric-card">
    <div class="metric-label">Notifications Sent</div>
    <div class="flip-row" id="notif-row"></div>
    <div class="metric-foot">
      <div class="live-dot"></div>
      <span class="live-text">Tracked via Airtable</span>
    </div>
  </div>

</div>

<script>
const SUBS  = {subscribers};
const NOTIF = {notifications};

function buildFlipRow(containerId, value) {{
  const container = document.getElementById(containerId);
  const str = value.toLocaleString('en-US');

  container.innerHTML = '';
  let delay = 0;

  for (let i = 0; i < str.length; i++) {{
    const ch = str[i];

    if (ch === ',') {{
      const sep = document.createElement('div');
      sep.className = 'flip-sep';
      sep.textContent = ',';
      container.appendChild(sep);
      continue;
    }}

    const wrapper = document.createElement('div');
    wrapper.className = 'flip-digit';
    wrapper.style.animationDelay = delay + 's';
    delay += 0.06;

    // Top static face
    const faceTop = document.createElement('div');
    faceTop.className = 'face face-top';
    const numTop = document.createElement('div');
    numTop.className = 'num';
    numTop.textContent = ch;
    faceTop.appendChild(numTop);

    // Bottom static face
    const faceBot = document.createElement('div');
    faceBot.className = 'face face-bottom';
    const numBot = document.createElement('div');
    numBot.className = 'num';
    numBot.textContent = ch;
    faceBot.appendChild(numBot);

    wrapper.appendChild(faceTop);
    wrapper.appendChild(faceBot);
    container.appendChild(wrapper);
  }}
}}

// Initial render with flip entrance
buildFlipRow('subs-row',  SUBS);
buildFlipRow('notif-row', NOTIF);

// Trigger flap animation on entrance for drama
setTimeout(() => {{
  document.querySelectorAll('.flip-digit').forEach((digit, idx) => {{
    const flap = digit.querySelector('.flap');
    if (flap) {{
      setTimeout(() => flap.classList.add('animate'), idx * 60);
    }}
  }});
}}, 200);
</script>
</body>
</html>"""
    components.html(html, height=290, scrolling=False)


# ── Page sections ──────────────────────────────────────────────────────────────

def render_navbar():
    st.markdown("""
    <nav style="
      display:flex; align-items:center; justify-content:space-between;
      padding: 1.2rem 3rem;
      border-bottom: 1px solid rgba(200,168,75,0.08);
      background: rgba(5,5,7,0.85);
      backdrop-filter: blur(16px) saturate(1.2);
      -webkit-backdrop-filter: blur(16px) saturate(1.2);
      position: sticky; top: 0; z-index: 999;
    ">
      <div style="display:flex; align-items:center; gap:10px;">
        <div style="
          width:28px; height:28px; border-radius:7px;
          background: linear-gradient(135deg, #c8a84b 0%, #8a6e2a 100%);
          display:flex; align-items:center; justify-content:center;
          font-size:0.8rem; box-shadow:0 4px 12px rgba(200,168,75,0.25);
        ">🪙</div>
        <span style="
          font-family:'Outfit',sans-serif; font-weight:700;
          font-size:0.9rem; color:#f2ede8; letter-spacing:-0.01em;
        ">Gold<span style="color:#c8a84b;">Alert</span> <span style="
          font-size:0.75rem; color:rgba(200,168,75,0.6);
          font-weight:400; letter-spacing:0.04em;
        ">SG</span></span>
      </div>
      <div style="display:flex; align-items:center; gap:1rem;">
        <span style="
          font-size:0.7rem; color:rgba(200,168,75,0.5);
          letter-spacing:0.1em; text-transform:uppercase; font-family:'Outfit',sans-serif;
        ">Free · Singapore</span>
      </div>
    </nav>
    """, unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <section style="
      position: relative;
      min-height: 88vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 6rem 2rem 5rem;
      overflow: hidden;
    ">

      <!-- Noise texture overlay -->
      <div style="
        position:absolute; inset:0;
        background-image: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22300%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.9%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22300%22 height=%22300%22 filter=%22url(%23n)%22 opacity=%220.04%22/%3E%3C/svg%3E');
        opacity: 0.6;
        pointer-events:none;
        z-index:0;
      "></div>

      <!-- Radial gold glow -->
      <div style="
        position:absolute; top:-10%; left:50%; transform:translateX(-50%);
        width:800px; height:500px;
        background: radial-gradient(ellipse at center,
          rgba(200,168,75,0.07) 0%,
          rgba(200,168,75,0.03) 35%,
          transparent 70%);
        pointer-events:none; z-index:0;
      "></div>

      <!-- Thin horizontal rule decoration -->
      <div style="
        position:absolute; top:50%; left:0; right:0;
        height:1px;
        background: linear-gradient(90deg, transparent, rgba(200,168,75,0.06) 30%, rgba(200,168,75,0.06) 70%, transparent);
        pointer-events:none; z-index:0;
      "></div>

      <!-- Content -->
      <div style="position:relative; z-index:1; max-width:680px; margin:0 auto;">

        <!-- Eyebrow tag -->
        <div style="
          display:inline-flex; align-items:center; gap:8px;
          border:1px solid rgba(200,168,75,0.2);
          border-radius:99px;
          padding:0.3rem 1rem 0.3rem 0.6rem;
          margin-bottom:2.5rem;
          background:rgba(200,168,75,0.04);
        ">
          <span style="
            display:inline-block; width:6px; height:6px;
            border-radius:50%; background:#c8a84b;
            box-shadow:0 0 10px rgba(200,168,75,1);
          "></span>
          <span style="
            font-family:'Outfit',sans-serif;
            font-size:0.72rem; font-weight:500;
            letter-spacing:0.1em; text-transform:uppercase;
            color:rgba(200,168,75,0.8);
          ">Live Price Monitoring · Singapore</span>
        </div>

        <!-- Headline -->
        <h1 style="
          font-family:'Cormorant Garamond', Georgia, serif;
          font-size: clamp(3rem, 7vw, 5.5rem);
          font-weight: 600;
          line-height: 1.0;
          letter-spacing: -0.02em;
          color: #f2ede8;
          margin-bottom: 0.5rem;
        ">Gold Price Alerts</h1>
        <h1 style="
          font-family:'Cormorant Garamond', Georgia, serif;
          font-size: clamp(3rem, 7vw, 5.5rem);
          font-weight: 300;
          font-style: italic;
          line-height: 1.0;
          letter-spacing: -0.02em;
          background: linear-gradient(135deg, #c8a84b 0%, #e4c56a 45%, #a07830 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 2rem;
        ">for Singapore.</h1>

        <!-- Sub-headline -->
        <p style="
          font-family:'Outfit',sans-serif;
          font-size: clamp(1rem, 2.5vw, 1.2rem);
          font-weight: 400;
          color: rgba(242,237,232,0.65);
          line-height: 1.6;
          margin-bottom: 0.6rem;
          letter-spacing: -0.01em;
        ">Never miss the best time to buy gold.</p>
        <p style="
          font-family:'Outfit',sans-serif;
          font-size: 0.9rem;
          color: rgba(242,237,232,0.35);
          line-height: 1.6;
          max-width: 400px;
          margin: 0 auto 4rem;
        ">Track jewellery gold prices automatically and receive
        alerts when the market moves.</p>

      </div>
    </section>
    """, unsafe_allow_html=True)


def render_subscribe_form():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        # Card top
        st.markdown("""
        <div style="
          background:#0b0b0f;
          border:1px solid rgba(200,168,75,0.14);
          border-bottom:none;
          border-radius:18px 18px 0 0;
          padding:2rem 2rem 0;
          margin-top:-3rem;
          position:relative; z-index:10;
        ">
          <p style="
            font-family:'Outfit',sans-serif;
            font-size:0.68rem; font-weight:600;
            letter-spacing:0.14em; text-transform:uppercase;
            color:rgba(200,168,75,0.55);
            margin-bottom:0.4rem;
            display:flex; align-items:center; gap:8px;
          "><span style="width:14px;height:1px;background:rgba(200,168,75,0.35);display:inline-block;"></span>Subscribe</p>
          <h2 style="
            font-family:'Cormorant Garamond',serif;
            font-size:1.7rem; font-weight:600;
            color:#f2ede8; letter-spacing:-0.01em;
            margin-bottom:0.25rem;
          ">Get the alerts.</h2>
          <p style="
            font-family:'Outfit',sans-serif;
            font-size:0.8rem; color:rgba(242,237,232,0.35);
            margin-bottom:1.5rem;
          ">Free · No account · Unsubscribe anytime</p>
        </div>
        """, unsafe_allow_html=True)

        # Form inputs (Streamlit widgets)
        with st.container():
            st.markdown('<div style="background:#0b0b0f;border:1px solid rgba(200,168,75,0.14);border-top:none;border-bottom:none;padding:0 2rem;">', unsafe_allow_html=True)
            email_input = st.text_input(
                "email",
                placeholder="your@email.com",
                key="sub_email",
                label_visibility="collapsed",
            )
            subscribe_clicked = st.button("Subscribe to Gold Alerts", key="sub_btn")
            st.markdown('</div>', unsafe_allow_html=True)

        # Handle subscription
        if subscribe_clicked:
            email = email_input.strip().lower()
            if not email:
                st.warning("Please enter your email address.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.warning("Enter a valid email address.")
            else:
                try:
                    result = subscribe_email(email)
                    if result == "duplicate":
                        st.info("Already subscribed — alerts are coming to you.")
                    else:
                        st.success("Subscribed. Your first alert is on its way.")
                        st.cache_data.clear()
                except Exception as e:
                    st.error(f"Something went wrong. Try again. ({e})")

        # Card bottom
        st.markdown("""
        <div style="
          background:#0b0b0f;
          border:1px solid rgba(200,168,75,0.14);
          border-top:none;
          border-radius:0 0 18px 18px;
          padding:1.2rem 2rem;
          display:flex; align-items:center; justify-content:center; gap:1rem;
        ">
          <span style="font-size:0.75rem;color:rgba(242,237,232,0.22);font-family:'Outfit',sans-serif;">
            🔒 No spam &nbsp;·&nbsp; 📊 Price changes only &nbsp;·&nbsp; 🇸🇬 SGD
          </span>
        </div>
        """, unsafe_allow_html=True)


def render_metrics(subscribers: int, notifications: int):
    st.markdown("""
    <div style="
      text-align:center; padding:4rem 2rem 1.5rem;
    ">
      <p style="
        font-family:'Outfit',sans-serif;
        font-size:0.68rem; font-weight:600;
        letter-spacing:0.14em; text-transform:uppercase;
        color:rgba(200,168,75,0.45); margin-bottom:0.4rem;
        display:flex; align-items:center; justify-content:center; gap:10px;
      ">
        <span style="width:24px;height:1px;background:rgba(200,168,75,0.3);display:inline-block;"></span>
        Live Metrics
        <span style="width:24px;height:1px;background:rgba(200,168,75,0.3);display:inline-block;"></span>
      </p>
    </div>
    """, unsafe_allow_html=True)
    flip_clock_component(subscribers, notifications)


def render_value_prop():
    st.markdown("""
    <section style="padding: 5rem 2rem; max-width:800px; margin:0 auto;">

      <div style="
        position:relative;
        border:1px solid rgba(200,168,75,0.12);
        border-radius:20px;
        padding:3.5rem 3rem;
        background:#0b0b0f;
        overflow:hidden;
        text-align:center;
      ">
        <!-- Decorative lines -->
        <div style="
          position:absolute; top:0; left:50%; transform:translateX(-50%);
          width:1px; height:40px; background:linear-gradient(180deg,rgba(200,168,75,0.4),transparent);
        "></div>
        <div style="
          position:absolute; bottom:0; left:50%; transform:translateX(-50%);
          width:1px; height:40px; background:linear-gradient(0deg,rgba(200,168,75,0.4),transparent);
        "></div>

        <div style="
          font-family:'Cormorant Garamond',serif;
          font-size:5rem; font-weight:700;
          line-height:1;
          background:linear-gradient(135deg,#c8a84b 0%,#e4c56a 50%,#a07830 100%);
          -webkit-background-clip:text; -webkit-text-fill-color:transparent;
          background-clip:text;
          margin-bottom:0.8rem;
          letter-spacing:-0.03em;
        ">S$350</div>

        <p style="
          font-family:'Outfit',sans-serif;
          font-size:1.1rem; font-weight:500;
          color:#f2ede8; margin-bottom:0.8rem;
          letter-spacing:-0.01em;
        ">Save up to S$350 per 100g by timing your purchase right.</p>

        <p style="
          font-family:'Outfit',sans-serif;
          font-size:0.88rem; color:rgba(242,237,232,0.4);
          max-width:400px; margin:0 auto; line-height:1.65;
        ">
          Gold prices fluctuate daily. Our alerts help you avoid
          buying at peak prices — so you only act when the market moves in your favour.
        </p>
      </div>
    </section>
    """, unsafe_allow_html=True)


def render_how_it_works():
    st.markdown("""
    <section style="padding:1rem 2rem 5rem; max-width:900px; margin:0 auto;">
      <div style="text-align:center; margin-bottom:3rem;">
        <p style="
          font-family:'Outfit',sans-serif;
          font-size:0.68rem; font-weight:600;
          letter-spacing:0.14em; text-transform:uppercase;
          color:rgba(200,168,75,0.45); margin-bottom:0.5rem;
        ">Process</p>
        <h2 style="
          font-family:'Cormorant Garamond',serif;
          font-size:2.5rem; font-weight:500;
          color:#f2ede8; letter-spacing:-0.02em;
        ">Three steps. Fully automated.</h2>
      </div>
    </section>
    """, unsafe_allow_html=True)

    steps = [
        {
            "num": "I",
            "icon": "◎",
            "title": "Subscribe",
            "desc": "Enter your email once. No account required, no password to remember.",
        },
        {
            "num": "II",
            "icon": "◈",
            "title": "We Monitor",
            "desc": "Our bot checks Mustafa Jewellery prices every hour, around the clock.",
        },
        {
            "num": "III",
            "icon": "◉",
            "title": "You're Alerted",
            "desc": "Receive an email the moment the price shifts. Act fast, buy smart.",
        },
    ]

    _, mid, _ = st.columns([0.5, 9, 0.5])
    with mid:
        cols = st.columns(3, gap="medium")
        for i, step in enumerate(steps):
            with cols[i]:
                st.markdown(f"""
                <div style="
                  background:#0b0b0f;
                  border:1px solid rgba(200,168,75,0.1);
                  border-radius:16px;
                  padding:2rem 1.6rem;
                  position:relative;
                  height:100%;
                ">
                  <div style="
                    display:flex; align-items:center; justify-content:space-between;
                    margin-bottom:1.5rem;
                  ">
                    <span style="
                      font-family:'Cormorant Garamond',serif;
                      font-size:0.85rem; font-style:italic;
                      color:rgba(200,168,75,0.4); letter-spacing:0.05em;
                    ">{step['num']}</span>
                    <span style="
                      font-size:1rem; color:rgba(200,168,75,0.5);
                    ">{step['icon']}</span>
                  </div>
                  <h3 style="
                    font-family:'Outfit',sans-serif;
                    font-size:0.95rem; font-weight:600;
                    color:#f2ede8; margin-bottom:0.5rem;
                    letter-spacing:-0.01em;
                  ">{step['title']}</h3>
                  <p style="
                    font-family:'Outfit',sans-serif;
                    font-size:0.82rem; color:rgba(242,237,232,0.38);
                    line-height:1.65;
                  ">{step['desc']}</p>
                </div>
                """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <footer style="
      border-top:1px solid rgba(200,168,75,0.08);
      padding:3rem 2rem;
      text-align:center;
    ">
      <div style="
        display:flex; align-items:center; justify-content:center;
        gap:2rem; flex-wrap:wrap; margin-bottom:2.5rem;
      ">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:0.85rem;">🔒</span>
          <span style="
            font-family:'Outfit',sans-serif;
            font-size:0.8rem; color:rgba(242,237,232,0.32);
          ">No spam. Only price alerts.</span>
        </div>
        <div style="
          width:1px; height:14px;
          background:rgba(200,168,75,0.1);
        "></div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:0.85rem;">🇸🇬</span>
          <span style="
            font-family:'Outfit',sans-serif;
            font-size:0.8rem; color:rgba(242,237,232,0.32);
          ">Singapore · SGD pricing only</span>
        </div>
        <div style="
          width:1px; height:14px;
          background:rgba(200,168,75,0.1);
        "></div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:0.85rem;">⚡</span>
          <span style="
            font-family:'Outfit',sans-serif;
            font-size:0.8rem; color:rgba(242,237,232,0.32);
          ">Checks every hour, automatically</span>
        </div>
      </div>

      <!-- Divider -->
      <div style="
        display:flex; align-items:center; gap:1rem;
        max-width:300px; margin:0 auto 2rem;
      ">
        <div style="flex:1;height:1px;background:rgba(200,168,75,0.08);"></div>
        <span style="font-size:0.7rem;color:rgba(200,168,75,0.2);">🪙</span>
        <div style="flex:1;height:1px;background:rgba(200,168,75,0.08);"></div>
      </div>

      <p style="
        font-family:'Outfit',sans-serif;
        font-size:0.7rem; color:rgba(242,237,232,0.15);
        letter-spacing:0.04em;
      ">
        GoldAlert SG &nbsp;·&nbsp; Powered by Mustafa Jewellery live data
      </p>
    </footer>
    """, unsafe_allow_html=True)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    subscribers   = get_subscriber_count()
    notifications = get_notifications_count()

    render_navbar()
    render_hero()
    render_subscribe_form()
    render_metrics(subscribers, notifications)
    render_value_prop()
    render_how_it_works()
    render_footer()


main()
