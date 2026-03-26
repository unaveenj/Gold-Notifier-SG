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
  metadataBase: new URL('https://www.goldnotifier.com'),
  title: 'Gold Notifier — Free Gold Price Alerts for Singapore',
  description:
    'Get instant email alerts when 22k and 24k gold prices change at Mustafa Jewellery. Free, no account needed. Updated every 2 hours, 9am–11pm SGT.',
  openGraph: {
    title: 'Gold Notifier — Never Miss a Gold Price Drop in Singapore',
    description:
      'Free email alerts for Singapore gold prices. 22k & 24k monitoring across Mustafa, Malabar, Joyalukkas & GRT.',
    type: 'website',
    url: 'https://www.goldnotifier.com',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Gold Notifier — Singapore Gold Price Alerts',
      },
    ],
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${cormorant.variable} ${outfit.variable} ${jetbrains.variable}`}
    >
      <body>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@graph': [
                {
                  '@type': 'WebSite',
                  '@id': 'https://www.goldnotifier.com/#website',
                  url: 'https://www.goldnotifier.com',
                  name: 'Gold Notifier',
                  description: 'Free gold price alerts for Singapore',
                },
                {
                  '@type': 'Service',
                  '@id': 'https://www.goldnotifier.com/#service',
                  name: 'Gold Notifier — Singapore Gold Price Alerts',
                  description:
                    'Free email alerts for 22k and 24k gold price changes at Mustafa, Malabar, Joyalukkas, and GRT jewellers in Singapore.',
                  url: 'https://www.goldnotifier.com',
                  provider: {
                    '@type': 'Organization',
                    name: 'Gold Notifier',
                    url: 'https://www.goldnotifier.com',
                  },
                  areaServed: { '@type': 'Country', name: 'Singapore' },
                  serviceType: 'Price Alert Service',
                  offers: { '@type': 'Offer', price: '0', priceCurrency: 'SGD' },
                },
              ],
            }),
          }}
        />
        {children}
      </body>
    </html>
  )
}
