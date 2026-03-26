import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://www.goldnotifier.com',
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: 'https://www.goldnotifier.com/unsubscribe',
      lastModified: new Date(),
      changeFrequency: 'never',
      priority: 0.3,
    },
  ]
}
