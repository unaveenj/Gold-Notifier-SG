import type { Metadata, Viewport } from 'next'
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

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export const metadata: Metadata = {
  metadataBase: new URL('https://www.goldnotifier.com'),
  title: 'Gold Notifier — Free Gold Price Alerts for Singapore',
  description:
    'Free email alerts for 22k & 24k gold prices at Mustafa, Malabar, Joyalukkas & GRT in Singapore. No account needed. Updated every 2 hours.',
  keywords:
    'gold price Singapore, Mustafa gold price, 22k gold Singapore, 24k gold Singapore, Malabar gold, Joyalukkas Singapore, GRT Jewellers, gold alert Singapore',
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'Gold Notifier — Never Miss a Gold Price Drop in Singapore',
    description:
      'Free email alerts for Singapore gold prices. 22k & 24k monitoring across Mustafa, Malabar, Joyalukkas & GRT.',
    type: 'website',
    url: 'https://www.goldnotifier.com',
    images: [
      {
        url: '/opengraph-image',
        width: 1200,
        height: 630,
        alt: 'Gold Notifier — Free Gold Price Alerts for Singapore',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Gold Notifier — Never Miss a Gold Price Drop in Singapore',
    description:
      'Free email alerts for Singapore gold prices. 22k & 24k monitoring across Mustafa, Malabar, Joyalukkas & GRT.',
    images: ['/opengraph-image'],
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
                  '@type': 'Organization',
                  '@id': 'https://www.goldnotifier.com/#organization',
                  name: 'Gold Notifier',
                  url: 'https://www.goldnotifier.com',
                  logo: 'https://www.goldnotifier.com/opengraph-image',
                  contactPoint: {
                    '@type': 'ContactPoint',
                    email: 'alerts@goldnotifier.com',
                    contactType: 'customer support',
                  },
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
                {
                  '@type': 'FAQPage',
                  '@id': 'https://www.goldnotifier.com/#faq',
                  mainEntity: [
                    {
                      '@type': 'Question',
                      name: 'Which jewellers does Gold Notifier monitor?',
                      acceptedAnswer: {
                        '@type': 'Answer',
                        text: 'Gold Notifier tracks 22k and 24k gold prices at four major Singapore jewellers: Mustafa Jewellery, Malabar Gold & Diamonds, Joyalukkas, and GRT Jewels.',
                      },
                    },
                    {
                      '@type': 'Question',
                      name: 'Is Gold Notifier free to use?',
                      acceptedAnswer: {
                        '@type': 'Answer',
                        text: 'Yes, Gold Notifier is completely free. No account, no credit card, and no subscription required — just enter your email to start receiving alerts.',
                      },
                    },
                    {
                      '@type': 'Question',
                      name: 'How often are gold prices updated?',
                      acceptedAnswer: {
                        '@type': 'Answer',
                        text: 'Prices are checked every 2 hours between 9am and 11pm SGT daily.',
                      },
                    },
                    {
                      '@type': 'Question',
                      name: 'How do I unsubscribe from gold price alerts?',
                      acceptedAnswer: {
                        '@type': 'Answer',
                        text: 'You can unsubscribe at any time by clicking the unsubscribe link at the bottom of any alert email, or by visiting goldnotifier.com/unsubscribe.',
                      },
                    },
                    {
                      '@type': 'Question',
                      name: 'Which gold types are monitored?',
                      acceptedAnswer: {
                        '@type': 'Answer',
                        text: 'Gold Notifier monitors both 22k and 24k gold prices across all four jewellers.',
                      },
                    },
                  ],
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
