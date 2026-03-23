import { NextResponse } from 'next/server'

const NOTIFICATIONS_BASE = 1000 // historical seed count
const SHOP_COUNT = 4            // number of shops tracked (one price record per shop per run)

async function countRecords(baseId: string, table: string, apiKey: string, field?: string): Promise<number> {
  let count = 0
  let offset: string | undefined

  do {
    const url = new URL(`https://api.airtable.com/v0/${baseId}/${encodeURIComponent(table)}`)
    if (field) url.searchParams.set('fields[]', field)
    url.searchParams.set('pageSize', '100')
    if (offset) url.searchParams.set('offset', offset)

    const res = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${apiKey}` },
      cache: 'no-store',
    })

    if (!res.ok) break
    const data = await res.json()
    count += data.records?.length ?? 0
    offset = data.offset
  } while (offset)

  return count
}

export async function GET() {
  const apiKey = process.env.AIRTABLE_API_KEY
  const baseId = process.env.AIRTABLE_BASE_ID

  if (!apiKey || !baseId) {
    return NextResponse.json({ subscribers: 0, notifications: NOTIFICATIONS_BASE })
  }

  try {
    const [subscribers, priceRecords] = await Promise.all([
      countRecords(baseId, 'subscribers', apiKey, 'email'),
      countRecords(baseId, 'prices', apiKey, 'shop'),
    ])

    // Each run creates one price record per shop, so divide by shop count to get runs.
    // Multiply runs by subscriber count — that's how many emails were actually sent.
    const runs = Math.floor(priceRecords / SHOP_COUNT)
    const notifications = NOTIFICATIONS_BASE + (runs * subscribers)

    return NextResponse.json({ subscribers, notifications })
  } catch {
    return NextResponse.json({ subscribers: 0, notifications: NOTIFICATIONS_BASE })
  }
}
