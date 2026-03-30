'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'

type Step = 'email' | 'otp' | 'done'
type Status = 'idle' | 'loading' | 'error'

export default function UnsubscribePage() {
  const [step, setStep] = useState<Step>('email')
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [errorMsg, setErrorMsg] = useState('')

  const requestOtp = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    const normalised = email.trim().toLowerCase()
    if (!normalised.includes('@') || !normalised.includes('.')) {
      setErrorMsg('Please enter a valid email address.')
      setStatus('error')
      return
    }
    setStatus('loading')
    setErrorMsg('')
    try {
      const res = await fetch('/api/unsubscribe/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: normalised }),
      })
      if (!res.ok) throw new Error()
      // Always move to OTP step — don't reveal if email exists
      setStep('otp')
      setStatus('idle')
    } catch {
      setStatus('error')
      setErrorMsg('Something went wrong. Please try again.')
    }
  }, [email])

  const confirmOtp = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (otp.trim().length !== 6) {
      setErrorMsg('Please enter the 6-digit code from your email.')
      setStatus('error')
      return
    }
    setStatus('loading')
    setErrorMsg('')
    try {
      const res = await fetch('/api/unsubscribe/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), otp: otp.trim() }),
      })
      const data = await res.json()
      if (!res.ok) {
        setStatus('error')
        setErrorMsg(data.error ?? 'Invalid code. Please try again.')
        return
      }
      setStep('done')
      setStatus('idle')
    } catch {
      setStatus('error')
      setErrorMsg('Something went wrong. Please try again.')
    }
  }, [email, otp])

  return (
    <div className="unsub-page">
      <div className="unsub-card">
        <Link href="/" className="unsub-back">← Back</Link>

        <div className="unsub-logo">🪙 Gold Notifier</div>

        {step === 'email' && (
          <>
            <h1 className="unsub-title">Unsubscribe</h1>
            <p className="unsub-sub">
              Enter your email and we&apos;ll send a one-time code to confirm.
            </p>
            <form className="unsub-form" onSubmit={requestOtp}>
              <input
                type="email"
                className="subscribe-input"
                placeholder="your@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                disabled={status === 'loading'}
                autoFocus
              />
              <button
                type="submit"
                className="btn-gold"
                disabled={status === 'loading'}
              >
                {status === 'loading' ? 'Sending…' : 'Send Code'}
              </button>
              {status === 'error' && (
                <p className="form-feedback error">{errorMsg}</p>
              )}
            </form>
          </>
        )}

        {step === 'otp' && (
          <>
            <h1 className="unsub-title">Check Your Email</h1>
            <p className="unsub-sub">
              If <strong>{email}</strong> is subscribed, a 6-digit code was sent.
              Enter it below to confirm unsubscription.
            </p>
            <form className="unsub-form" onSubmit={confirmOtp}>
              <input
                type="text"
                className="subscribe-input unsub-otp-input"
                placeholder="000000"
                value={otp}
                onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                disabled={status === 'loading'}
                inputMode="numeric"
                autoFocus
                maxLength={6}
              />
              <button
                type="submit"
                className="btn-gold btn-danger"
                disabled={status === 'loading'}
              >
                {status === 'loading' ? 'Verifying…' : 'Confirm Unsubscribe'}
              </button>
              {status === 'error' && (
                <p className="form-feedback error">{errorMsg}</p>
              )}
            </form>
            <button
              className="unsub-resend"
              onClick={() => { setStep('email'); setOtp(''); setStatus('idle'); setErrorMsg('') }}
            >
              Use a different email
            </button>
          </>
        )}

        {step === 'done' && (
          <>
            <div className="unsub-success-icon">✓</div>
            <h1 className="unsub-title">Unsubscribed</h1>
            <p className="unsub-sub">
              You&apos;ve been removed from Gold Notifier. You won&apos;t receive any more alerts.
            </p>
            <Link href="/" className="btn-gold" style={{ display: 'inline-block', marginTop: '1rem', textAlign: 'center' }}>
              Back to Home
            </Link>
          </>
        )}
      </div>
    </div>
  )
}
