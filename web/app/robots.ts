import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/trigger'],
    },
    sitemap: 'https://www.goldnotifier.com/sitemap.xml',
  }
}
