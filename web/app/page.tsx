'use client'

import { useEffect, useRef, useState, useCallback, Fragment } from 'react'
import Link from 'next/link'

/* ─── Types ─── */
interface Particle {
  x: number; y: number; size: number; speed: number
  opacity: number; color: string; phase: number; phaseSpeed: number
}
interface GlowOrb {
  x: number; y: number; radius: number; opacity: number; dx: number; dy: number
}

/* ─── Gold canvas animation ─── */
function GoldCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animId: number
    let particles: Particle[] = []
    let orbs: GlowOrb[] = []

    const COLORS = ['#c8a84b', '#d4b55c', '#e8c86d', '#f0d070', '#f5d87a', '#b89438', '#a07d30']

    function resize() {
      canvas!.width = window.innerWidth
      canvas!.height = window.innerHeight
    }

    function initParticles() {
      particles = Array.from({ length: 130 }, () => ({
        x: Math.random() * canvas!.width,
        y: Math.random() * canvas!.height,
        size: Math.random() * 1.8 + 0.4,
        speed: Math.random() * 0.55 + 0.15,
        opacity: Math.random() * 0.45 + 0.08,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        phase: Math.random() * Math.PI * 2,
        phaseSpeed: (Math.random() * 0.015) + 0.008,
      }))

      orbs = Array.from({ length: 7 }, () => ({
        x: Math.random() * canvas!.width,
        y: Math.random() * canvas!.height,
        radius: Math.random() * 220 + 80,
        opacity: Math.random() * 0.028 + 0.008,
        dx: (Math.random() - 0.5) * 0.25,
        dy: (Math.random() - 0.5) * 0.25,
      }))
    }

    function draw() {
      ctx!.clearRect(0, 0, canvas!.width, canvas!.height)

      // Glow orbs
      for (const orb of orbs) {
        const g = ctx!.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, orb.radius)
        g.addColorStop(0, `rgba(200,168,75,${orb.opacity})`)
        g.addColorStop(1, 'rgba(200,168,75,0)')
        ctx!.fillStyle = g
        ctx!.beginPath()
        ctx!.arc(orb.x, orb.y, orb.radius, 0, Math.PI * 2)
        ctx!.fill()

        orb.x += orb.dx
        orb.y += orb.dy
        if (orb.x < -orb.radius) orb.x = canvas!.width + orb.radius
        if (orb.x > canvas!.width + orb.radius) orb.x = -orb.radius
        if (orb.y < -orb.radius) orb.y = canvas!.height + orb.radius
        if (orb.y > canvas!.height + orb.radius) orb.y = -orb.radius
      }

      // Particles
      ctx!.save()
      for (const p of particles) {
        ctx!.globalAlpha = p.opacity
        ctx!.fillStyle = p.color
        ctx!.beginPath()
        ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx!.fill()

        p.phase += p.phaseSpeed
        p.y -= p.speed
        p.x += Math.sin(p.phase) * 0.28

        if (p.y < -p.size * 2) {
          p.y = canvas!.height + p.size
          p.x = Math.random() * canvas!.width
        }
        if (p.x < 0) p.x = canvas!.width
        if (p.x > canvas!.width) p.x = 0
      }
      ctx!.restore()

      animId = requestAnimationFrame(draw)
    }

    resize()
    initParticles()
    draw()

    const onResize = () => { resize(); initParticles() }
    window.addEventListener('resize', onResize)
    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  return <canvas ref={canvasRef} id="gold-canvas" aria-hidden="true" />
}

/* ─── Subscribe form ─── */
type FormStatus = 'idle' | 'loading' | 'success' | 'error' | 'duplicate'

function SubscribeForm({ size = 'default' }: { size?: 'default' | 'large' }) {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<FormStatus>('idle')
  const [message, setMessage] = useState('')

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (status === 'loading' || status === 'success') return

    const trimmed = email.trim().toLowerCase()
    if (!trimmed.includes('@') || !trimmed.includes('.')) {
      setStatus('error')
      setMessage('Please enter a valid email address.')
      return
    }

    setStatus('loading')
    setMessage('')

    try {
      const res = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: trimmed }),
      })

      if (res.status === 409) {
        setStatus('duplicate')
        setMessage("You're already subscribed — we'll keep sending alerts!")
        return
      }

      if (!res.ok) throw new Error('Server error')

      setStatus('success')
      setMessage('You\'re in! Expect your first alert soon.')
      setEmail('')
      window.dispatchEvent(new Event('metrics-refresh'))
    } catch {
      setStatus('error')
      setMessage('Something went wrong. Please try again.')
    }
  }, [email, status])

  const btnLabel: Record<FormStatus, string> = {
    idle:      'Get Free Alerts',
    loading:   'Subscribing…',
    success:   '✓ You\'re In!',
    error:     'Try Again',
    duplicate: '✓ Already In!',
  }

  const isLarge = size === 'large'

  return (
    <div className="subscribe-wrap">
      <form className="subscribe-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="subscribe-input"
          disabled={status === 'loading' || status === 'success'}
          aria-label="Email address"
          style={isLarge ? { fontSize: '1.05rem', padding: '1rem 1.4rem' } : {}}
        />
        <button
          type="submit"
          className={`btn-gold ${status === 'success' || status === 'duplicate' ? 'success' : ''}`}
          disabled={status === 'loading' || status === 'success' || status === 'duplicate'}
          style={isLarge ? { fontSize: '0.88rem', padding: '1rem 2.2rem' } : {}}
        >
          {btnLabel[status]}
        </button>
      </form>
      {message && (
        <p className={`form-feedback ${status}`} role="status">{message}</p>
      )}
    </div>
  )
}

/* ─── Live metrics ─── */
function LiveMetrics() {
  const [metrics, setMetrics] = useState({ subscribers: 0, notifications: 0 })
  const [updating, setUpdating] = useState(false)

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await fetch('/api/metrics')
      if (!res.ok) return
      const data = await res.json()
      setUpdating(true)
      setMetrics(data)
      setTimeout(() => setUpdating(false), 600)
    } catch { /* silent */ }
  }, [])

  useEffect(() => {
    fetchMetrics()
    const id = setInterval(fetchMetrics, 30_000)
    window.addEventListener('metrics-refresh', fetchMetrics)
    return () => {
      clearInterval(id)
      window.removeEventListener('metrics-refresh', fetchMetrics)
    }
  }, [fetchMetrics])

  return (
    <div className="metrics-strip">
      <div className="metric-item">
        <span className={`metric-value ${updating ? 'updating' : ''}`}>
          {metrics.subscribers.toLocaleString()}
        </span>
        <span className="metric-label">Subscribers</span>
      </div>
      <div className="metrics-divider" />
      <div className="metric-item">
        <span className={`metric-value ${updating ? 'updating' : ''}`}>
          {metrics.notifications.toLocaleString()}
        </span>
        <span className="metric-label">Alerts Sent</span>
      </div>
    </div>
  )
}

/* ─── Data ─── */
const FEATURES = [
  {
    icon: '💛',
    title: '3 Shops, One Alert',
    desc: 'Compare 22k and 24k gold prices across the top jewellers in Singapore — all delivered in a single email.',
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
  { value: '3', label: 'Shops Monitored' },
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
      "The alerts helped me plan my purchase around a price dip I'd been waiting weeks for. Bought 50g at just the right moment — couldn't have timed it without GoldAlert SG.",
    detail: 'Regular gold investor, Singapore',
  },
]

/* ─── Page ─── */
export default function HomePage() {
  // Scroll reveal
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible') }),
      { threshold: 0.12 }
    )
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  const scrollToForm = () => {
    document.getElementById('subscribe')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <>
      <GoldCanvas />

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
          GoldAlert&nbsp;<span className="nav-logo-sg">SG</span>
        </div>
        <button className="btn-gold-outline" onClick={scrollToForm}>
          Subscribe Free
        </button>
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
              3 top Singapore jewellers · Updated every 2 hours · 9am – 11pm SGT
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
            <p className="section-label reveal">Why GoldAlert SG</p>
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
          <div className="footer-logo">🪙 GoldAlert SG</div>
          <p className="footer-tagline">Free Gold Price Alerts for Singapore</p>
          <p className="footer-copy">
            Powered by automated monitoring across 3 Singapore jewellers
          </p>
          <p className="footer-legal">© 2025 GoldAlert SG · Free Service · Singapore</p>
          <Link href="/unsubscribe" className="footer-unsub">Unsubscribe</Link>
        </footer>
      </main>
    </>
  )
}
