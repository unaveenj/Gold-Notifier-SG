import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Unsubscribe — Gold Notifier',
  description: 'Unsubscribe from Gold Notifier email alerts. Takes less than a minute.',
  robots: { index: false, follow: false },
}

export default function UnsubscribeLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
