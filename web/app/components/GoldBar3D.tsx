'use client'

import { useEffect, useRef } from 'react'

export default function GoldBar3D() {
  const barRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let rafId: number
    let lastScrollY = window.scrollY

    const update = () => {
      const scrollY = window.scrollY
      // Map scroll 0→800px to Y-rotation -28→+28 degrees
      const progress = Math.min(scrollY / 800, 1)
      const ry = -28 + progress * 56
      // Slight X tilt eases back toward -8deg as you scroll (less dramatic tilt)
      const rx = -14 + progress * 6
      barRef.current?.style.setProperty('--bar-ry', `${ry.toFixed(2)}deg`)
      barRef.current?.style.setProperty('--bar-rx', `${rx.toFixed(2)}deg`)
      lastScrollY = scrollY
    }

    const onScroll = () => {
      cancelAnimationFrame(rafId)
      rafId = requestAnimationFrame(update)
    }

    // Set initial position
    update()

    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      cancelAnimationFrame(rafId)
    }
  }, [])

  return (
    <div className="gold3d-scene" aria-hidden="true">
      <div className="gold3d-glow" />
      <div className="gold3d-float">
        <div className="gold3d-bar" ref={barRef}>
          {/* Top face — brightest, most visible */}
          <div className="gold3d-face gold3d-top">
            <div className="gold3d-shine gold3d-shine-top" />
          </div>
          {/* Front face — main face with engravings */}
          <div className="gold3d-face gold3d-front">
            <div className="gold3d-engraving">
              <span className="gold3d-fineness">999.9</span>
              <span className="gold3d-label">FINE GOLD</span>
              <span className="gold3d-mass">1 KG · 32.15 OZ t</span>
            </div>
            <div className="gold3d-bevel-tl" />
            <div className="gold3d-bevel-br" />
            <div className="gold3d-shine gold3d-shine-front" />
          </div>
          {/* Right face */}
          <div className="gold3d-face gold3d-right" />
          {/* Left face */}
          <div className="gold3d-face gold3d-left" />
          {/* Back face */}
          <div className="gold3d-face gold3d-back" />
          {/* Bottom face */}
          <div className="gold3d-face gold3d-bottom" />
        </div>
        <div className="gold3d-shadow" />
      </div>
    </div>
  )
}
