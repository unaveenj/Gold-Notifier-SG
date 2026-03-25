import { NextResponse } from 'next/server'

const VISITOR_SEED = 200

async function getRecord(baseId: string, apiKey: string) {
  const res = await fetch(
    `https://api.airtable.com/v0/${baseId}/visitors?pageSize=1`,
    { headers: { Authorization: `Bearer ${apiKey}` }, cache: 'no-store' }
  )
  if (!res.ok) return null
  const data = await res.json()
  return data.records?.[0] ?? null
}

// GET — return current count (no increment, for display)
export async function GET() {
  const apiKey = process.env.AIRTABLE_API_KEY
  const baseId = process.env.AIRTABLE_BASE_ID
  if (!apiKey || !baseId) return NextResponse.json({ count: VISITOR_SEED })

  try {
    const record = await getRecord(baseId, apiKey)
    const count = VISITOR_SEED + (record?.fields?.count ?? 0)
    return NextResponse.json({ count })
  } catch {
    return NextResponse.json({ count: VISITOR_SEED })
  }
}

// POST — increment count, return new value
export async function POST() {
  const apiKey = process.env.AIRTABLE_API_KEY
  const baseId = process.env.AIRTABLE_BASE_ID
  if (!apiKey || !baseId) return NextResponse.json({ count: VISITOR_SEED })

  try {
    const record = await getRecord(baseId, apiKey)
    if (!record) return NextResponse.json({ count: VISITOR_SEED })

    const newCount = (record.fields?.count ?? 0) + 1

    await fetch(`https://api.airtable.com/v0/${baseId}/visitors/${record.id}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fields: { count: newCount } }),
    })

    return NextResponse.json({ count: VISITOR_SEED + newCount })
  } catch {
    return NextResponse.json({ count: VISITOR_SEED })
  }
}
