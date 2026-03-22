import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const apiKey = process.env.AIRTABLE_API_KEY
  const baseId = process.env.AIRTABLE_BASE_ID

  if (!apiKey || !baseId) {
    return NextResponse.json({ error: 'Service unavailable' }, { status: 503 })
  }

  let body: { email?: string }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 })
  }

  const email = body.email?.trim().toLowerCase()
  if (!email || !email.includes('@') || !email.includes('.')) {
    return NextResponse.json({ error: 'Invalid email address' }, { status: 400 })
  }

  const base = `https://api.airtable.com/v0/${baseId}`
  const headers = {
    Authorization: `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  }

  try {
    // Check for duplicate
    const checkUrl = new URL(`${base}/subscribers`)
    checkUrl.searchParams.set('filterByFormula', `({email}="${email}")`)
    checkUrl.searchParams.set('fields[]', 'email')
    checkUrl.searchParams.set('maxRecords', '1')

    const checkRes = await fetch(checkUrl.toString(), { headers })
    if (!checkRes.ok) throw new Error('Airtable check failed')

    const checkData = await checkRes.json()
    if (checkData.records?.length > 0) {
      return NextResponse.json({ error: 'already_subscribed' }, { status: 409 })
    }

    // Create subscriber
    const createRes = await fetch(`${base}/subscribers`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ records: [{ fields: { email } }] }),
    })

    if (!createRes.ok) throw new Error('Airtable create failed')

    return NextResponse.json({ success: true })
  } catch {
    return NextResponse.json({ error: 'Service error' }, { status: 500 })
  }
}
