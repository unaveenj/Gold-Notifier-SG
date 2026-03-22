import type { Metadata } from 'next'
import { Cormorant_Garamond, Outfit, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const cormorant = Cormorant_Garamond({
  subsets: ['latin'],
  weight: ['300', '400', '600', '700'],
  style: ['normal', 'italic'],
  variable: '--font-cormorant',
  display: 'swap',
})

const outfit = Outfit({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600'],
  variable: '--font-outfit',
  display: 'swap',
})

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'GoldAlert SG — Free Gold Price Alerts for Singapore',
  description:
    'Get instant email alerts when 22k and 24k gold prices change at Mustafa Jewellery. Free, no account needed. Updated every 2 hours, 9am–11pm SGT.',
  openGraph: {
    title: 'GoldAlert SG — Never Miss a Gold Price Drop',
    description:
      'Free email alerts for Singapore gold prices. 22k & 24k monitoring from Mustafa Jewellery.',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${cormorant.variable} ${outfit.variable} ${jetbrains.variable}`}
    >
      <body>{children}</body>
    </html>
  )
}
