'use client'

import { useEffect, useRef } from 'react'

interface Particle {
  x: number; y: number; size: number; speed: number
  opacity: number; color: string; phase: number; phaseSpeed: number
}
interface GlowOrb {
  x: number; y: number; radius: number; opacity: number; dx: number; dy: number
}

export default function GoldCanvas() {
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
