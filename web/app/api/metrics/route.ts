import { NextResponse } from 'next/server'

async function countRecords(baseId: string, table: string, apiKey: string): Promise<number> {
  let count = 0
  let offset: string | undefined

  do {
    const url = new URL(`https://api.airtable.com/v0/${baseId}/${encodeURIComponent(table)}`)
    url.searchParams.set('fields[]', 'email')
    url.searchParams.set('pageSize', '100')
    if (offset) url.searchParams.set('offset', offset)

    const res = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${apiKey}` },
      next: { revalidate: 60 },
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
    return NextResponse.json({ subscribers: 0, notifications: 0 })
  }

  try {
    const [subscribers, notifications] = await Promise.all([
      countRecords(baseId, 'subscribers', apiKey),
      countRecords(baseId, 'notifications', apiKey),
    ])

    return NextResponse.json({ subscribers, notifications })
  } catch {
    return NextResponse.json({ subscribers: 0, notifications: 0 })
  }
}
