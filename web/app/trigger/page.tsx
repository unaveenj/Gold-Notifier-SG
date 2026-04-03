'use client'

import { useState } from 'react'

export default function TriggerPage() {
  const [token, setToken]   = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  async function handleTrigger() {
    if (!token.trim()) return
    setStatus('loading')
    setMessage('')

    try {
      const res = await fetch('/api/trigger', {
        method: 'POST',
        headers: { 'x-trigger-token': token.trim() },
      })
      const data = await res.json()

      if (res.ok) {
        setStatus('success')
        setMessage('Workflow triggered! Check GitHub Actions.')
      } else {
        setStatus('error')
        setMessage(data.error || 'Something went wrong.')
      }
    } catch {
      setStatus('error')
      setMessage('Network error. Try again.')
    }
  }

  return (
    <main style={{
      minHeight: '100vh',
      background: '#070708',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      fontFamily: 'sans-serif',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '360px',
        background: '#111',
        border: '1px solid #222',
        borderRadius: '12px',
        padding: '32px 24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
      }}>
        <h1 style={{ color: '#c8a84b', margin: 0, fontSize: '20px', textAlign: 'center' }}>
          Gold Notifier
        </h1>
        <p style={{ color: '#888', margin: 0, fontSize: '13px', textAlign: 'center' }}>
          Send daily alert email now
        </p>

        <input
          type="password"
          placeholder="Enter trigger token"
          value={token}
          onChange={e => setToken(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleTrigger()}
          style={{
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #333',
            background: '#1a1a1a',
            color: '#e8dfc8',
            fontSize: '15px',
            outline: 'none',
          }}
        />

        <button
          onClick={handleTrigger}
          disabled={status === 'loading'}
          style={{
            padding: '14px',
            borderRadius: '8px',
            border: 'none',
            background: status === 'loading' ? '#555' : '#c8a84b',
            color: '#070708',
            fontWeight: 700,
            fontSize: '15px',
            cursor: status === 'loading' ? 'not-allowed' : 'pointer',
          }}
        >
          {status === 'loading' ? 'Sending...' : 'Send Alert Now'}
        </button>

        {message && (
          <p style={{
            margin: 0,
            fontSize: '13px',
            textAlign: 'center',
            color: status === 'success' ? '#81C784' : '#e57373',
          }}>
            {message}
          </p>
        )}
      </div>
    </main>
  )
}
