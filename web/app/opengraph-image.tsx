import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#070708',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Subtle gold glow background */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 700,
            height: 700,
            borderRadius: '50%',
            background:
              'radial-gradient(circle, rgba(200,168,75,0.12) 0%, rgba(200,168,75,0) 70%)',
          }}
        />

        {/* Coin icon */}
        <div style={{ fontSize: 80, marginBottom: 16, display: 'flex' }}>🪙</div>

        {/* Brand */}
        <div
          style={{
            fontSize: 72,
            fontWeight: 700,
            color: '#c8a84b',
            letterSpacing: '-1px',
            display: 'flex',
          }}
        >
          Gold Notifier
        </div>

        {/* Gold divider line */}
        <div
          style={{
            width: 80,
            height: 3,
            background: '#c8a84b',
            borderRadius: 2,
            margin: '20px 0',
            display: 'flex',
          }}
        />

        {/* Tagline */}
        <div
          style={{
            fontSize: 30,
            color: '#e8dfc8',
            textAlign: 'center',
            maxWidth: 700,
            lineHeight: 1.4,
            display: 'flex',
          }}
        >
          Free Gold Price Alerts for Singapore
        </div>

        {/* Sub-tagline */}
        <div
          style={{
            fontSize: 22,
            color: '#888',
            marginTop: 16,
            display: 'flex',
          }}
        >
          22k & 24k · Mustafa · Malabar · Joyalukkas · GRT
        </div>

        {/* Domain badge */}
        <div
          style={{
            position: 'absolute',
            bottom: 36,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: 'rgba(200,168,75,0.12)',
            border: '1px solid rgba(200,168,75,0.3)',
            borderRadius: 24,
            padding: '8px 20px',
            color: '#c8a84b',
            fontSize: 20,
          }}
        >
          goldnotifier.com
        </div>
      </div>
    ),
    { ...size },
  )
}
