'use client'

export default function GoldBar3D() {
  return (
    <div className="gold3d-scene" aria-hidden="true">
      <div className="gold3d-glow" />
      <div className="gold3d-float">
        <div className="gold3d-bar">
          {/* Top face — brightest, most visible */}
          <div className="gold3d-face gold3d-top">
            <div className="gold3d-shine gold3d-shine-top" />
          </div>
          {/* Front face — main face with engravings */}
          <div className="gold3d-face gold3d-front">
            <div className="gold3d-engraving">
              <span className="gold3d-fineness">999.9</span>
              <span className="gold3d-label">FINE GOLD</span>
              <span className="gold3d-mass">1 KG · 32.15 OZ</span>
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
