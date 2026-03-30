'use client'

import { useState, useCallback } from 'react'

type FormStatus = 'idle' | 'loading' | 'success' | 'error' | 'duplicate'

export default function SubscribeForm({ size = 'default' }: { size?: 'default' | 'large' }) {
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
