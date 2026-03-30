import { Fragment } from 'react'
import Link from 'next/link'
import GoldCanvas from './components/GoldCanvas'
import SubscribeForm from './components/SubscribeForm'
import LiveMetrics from './components/LiveMetrics'
import VisitorBadge from './components/VisitorBadge'
import RevealObserver from './components/RevealObserver'
import ScrollToFormButton from './components/ScrollToFormButton'

const FEATURES = [
  {
    icon: '💛',
    title: '4 Shops, One Alert',
    desc: 'Compare 22k and 24k gold prices across Mustafa, Malabar, Joyalukkas and GRT — all delivered in a single email.',
  },
  {
    icon: '⚡',
    title: 'Instant Email Alerts',
    desc: 'Receive a notification the moment prices change, with trend indicators showing whether rates moved up ↑ or down ↓.',
  },
  {
    icon: '🔄',
    title: 'Regular Updates',
    desc: 'Prices are checked every 2 hours from 9am to 11pm SGT daily, so you never miss a buying opportunity.',
  },
  {
    icon: '🔒',
    title: 'Zero Friction',
    desc: 'No account, no password, no app to download. Just your email — and unsubscribe any time with one click.',
  },
]

const STEPS = [
  {
    icon: '✉️',
    title: 'Subscribe',
    desc: 'Enter your email below. No password, no credit card. Takes under 10 seconds.',
  },
  {
    icon: '🔍',
    title: 'We Monitor',
    desc: 'Our system scrapes live gold prices every 2 hours during market hours.',
  },
  {
    icon: '🔔',
    title: "You're Alerted",
    desc: 'Receive a clear email with current 22k & 24k prices and price trend direction.',
  },
]

const STATS = [
  { value: '4', label: 'Shops Monitored' },
  { value: '22k & 24k', label: 'Gold Purities Tracked' },
  { value: '100%', label: 'Free Forever' },
]

const TESTIMONIALS = [
  {
    quote:
      'I saved over S$300 buying at the right time thanks to the alerts! The emails are concise and come at the perfect moment.',
    detail: 'Gold buyer, Singapore',
  },
  {
    quote:
      "The alerts helped me plan my purchase around a price dip I'd been waiting weeks for. Bought 50g at just the right moment — couldn't have timed it without Gold Notifier.",
    detail: 'Regular gold investor, Singapore',
  },
]

export default function HomePage() {
  return (
    <>
      <GoldCanvas />
      <VisitorBadge />
      <RevealObserver />

      {/* ── Announcement Bar ── */}
      <div className="announcement-bar" role="banner">
        <span className="announcement-star">✦</span>
        &nbsp;100% Free for Life &mdash; Limited Early Access&nbsp;
        <span className="announcement-star">✦</span>
        <span className="announcement-secondary">&nbsp;· No credit card · No account · Unsubscribe anytime</span>
      </div>

      {/* ── Nav ── */}
      <nav className="nav">
        <div className="nav-logo">
          <span className="nav-logo-icon">🪙</span>
          Gold&nbsp;<span className="nav-logo-sg">Notifier</span>
        </div>
        <div className="nav-actions">
          <Link href="/unsubscribe" className="nav-unsub-link">Unsubscribe</Link>
          <ScrollToFormButton />
        </div>
      </nav>

      <main>
        {/* ── Hero ── */}
        <section className="hero" id="hero">
          <div className="hero-content">
            <div className="live-badge">
              <span className="live-badge-dot" />
              Live Gold Price Monitoring · Singapore
            </div>

            <h1 className="hero-headline">
              Never Miss a<br />
              <span className="hero-headline-shimmer">Gold Price Drop</span>
              <span className="hero-headline-small">in Singapore</span>
            </h1>

            <div className="gold-divider" />

            <p className="hero-subtext">
              Get instant email alerts when 22k and 24k gold prices change.
              <br />Free forever. No account needed.
            </p>

            <div id="subscribe">
              <SubscribeForm size="large" />
            </div>

            <LiveMetrics />

            <p className="hero-source">
              4 top Singapore jewellers · Updated every 2 hours · 9am – 11pm SGT
            </p>
          </div>

          <div className="scroll-cue" aria-hidden="true">
            <div className="scroll-arrow" />
          </div>
        </section>

        {/* ── Stats Band ── */}
        <div className="stats-band">
          {STATS.map(s => (
            <div key={s.label} className="stat-item">
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {/* ── Features ── */}
        <section className="section features-section">
          <div className="section-inner">
            <p className="section-label reveal">Why Gold Notifier</p>
            <h2 className="section-title reveal reveal-d1">
              Everything You Need<br />to Track Gold Prices
            </h2>
            <div className="gold-rule reveal reveal-d2" />
            <p className="section-sub reveal reveal-d2">
              A simple, free service built for Singapore gold buyers who want to buy smart.
            </p>

            <div className="features-grid">
              {FEATURES.map((f, i) => (
                <div
                  key={f.title}
                  className={`feature-card reveal reveal-d${(i % 2) + 1}`}
                >
                  <span className="feature-icon">{f.icon}</span>
                  <h3 className="feature-title">{f.title}</h3>
                  <p className="feature-desc">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Testimonials ── */}
        <section className="section testimonial-section">
          <div className="section-inner">
            <p className="section-label reveal">What Subscribers Say</p>
            <h2 className="section-title reveal reveal-d1">Real Results,<br />Real Savings</h2>
            <div className="gold-rule reveal reveal-d2" />
            <div className="testimonials-grid">
              {TESTIMONIALS.map((t, i) => (
                <div key={t.detail} className={`testimonial-card reveal reveal-d${i + 1}`}>
                  <span className="testimonial-quote-mark" aria-hidden="true">&ldquo;</span>
                  <p className="testimonial-text">{t.quote}</p>
                  <div className="testimonial-footer">
                    <p className="testimonial-detail">— {t.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── How It Works ── */}
        <section className="section how-section">
          <div className="section-inner">
            <p className="section-label reveal">Simple Process</p>
            <h2 className="section-title reveal reveal-d1">How It Works</h2>
            <div className="gold-rule reveal reveal-d2" />

            <div className="steps-container">
              {STEPS.map((step, i) => (
                <Fragment key={step.title}>
                  <div className={`step-card reveal reveal-d${i + 1}`}>
                    <div className="step-number">0{i + 1}</div>
                    <span className="step-icon">{step.icon}</span>
                    <h3 className="step-title">{step.title}</h3>
                    <p className="step-desc">{step.desc}</p>
                  </div>
                  {i < STEPS.length - 1 && (
                    <div className="step-connector">
                      <div className="step-connector-line" />
                    </div>
                  )}
                </Fragment>
              ))}
            </div>
          </div>
        </section>

        {/* ── Value Prop ── */}
        <section className="section value-section">
          <div className="section-inner">
            <p className="value-eyebrow reveal">The Smart Buyer&apos;s Advantage</p>
            <h2 className="value-headline reveal reveal-d1">
              Save up to<br />
              <span className="value-amount">S$350</span><br />
              per 100g of gold
            </h2>
            <div className="gold-rule reveal reveal-d2" />
            <p className="value-sub reveal reveal-d2">
              Gold prices fluctuate throughout the day. Our alerts help you
              time your purchase — and keep more money in your pocket.
            </p>
          </div>
        </section>

        {/* ── CTA ── */}
        <section className="section cta-section">
          <div className="section-inner">
            <h2 className="cta-headline reveal">
              Start Getting Gold Alerts<br />Today
            </h2>
            <p className="cta-sub reveal reveal-d1">
              Free · No account · Unsubscribe anytime
            </p>

            <div className="reveal reveal-d2" style={{ display: 'flex', justifyContent: 'center' }}>
              <SubscribeForm size="large" />
            </div>

            <div className="cta-perks reveal reveal-d3">
              {['Free forever', 'No password', 'Instant alerts', 'One-click unsubscribe'].map(p => (
                <span key={p} className="cta-perk">
                  <span className="cta-perk-check">◆</span> {p}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="footer">
          <div className="footer-logo">🪙 Gold Notifier</div>
          <p className="footer-tagline">Free Gold Price Alerts for Singapore</p>
          <p className="footer-copy">
            Powered by automated monitoring across 4 Singapore jewellers
          </p>
          <p className="footer-legal">© 2026 Gold Notifier · Free Service · Singapore</p>
          <Link href="/unsubscribe" className="footer-unsub">Unsubscribe</Link>
        </footer>
      </main>
    </>
  )
}
