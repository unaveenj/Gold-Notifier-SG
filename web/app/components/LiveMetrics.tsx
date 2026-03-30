'use client'

import { useState, useEffect, useCallback } from 'react'

export default function LiveMetrics() {
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
