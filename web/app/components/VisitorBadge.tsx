'use client'

import { useState, useEffect } from 'react'

export default function VisitorBadge() {
  const [count, setCount] = useState<number | null>(null)

  useEffect(() => {
    const key = 'ga_visited'
    const visited = sessionStorage.getItem(key)
    const endpoint = '/api/visitors'

    if (!visited) {
      sessionStorage.setItem(key, '1')
      fetch(endpoint, { method: 'POST' })
        .then(r => r.json())
        .then(d => setCount(d.count))
        .catch(() => {})
    } else {
      fetch(endpoint)
        .then(r => r.json())
        .then(d => setCount(d.count))
        .catch(() => {})
    }
  }, [])

  if (count === null) return null

  return (
    <div className="visitor-badge" aria-label={`${count} visitors`}>
      <span className="visitor-badge-icon">👁</span>
      <span className="visitor-badge-count">{count.toLocaleString()}</span>
      <span className="visitor-badge-label">visitors</span>
    </div>
  )
}
