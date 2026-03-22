import { NextResponse } from 'next/server'

const BASE_URL = `https://api.airtable.com/v0/${process.env.AIRTABLE_BASE_ID}`
const AUTH = { Authorization: `Bearer ${process.env.AIRTABLE_API_KEY}` }
const OTP_TTL_MS = 10 * 60 * 1000 // 10 minutes

async function findOtpRecord(email: string, otp: string) {
  const url = new URL(`${BASE_URL}/otps`)
  url.searchParams.set('filterByFormula', `AND({email}="${email}", {otp}="${otp}")`)
  url.searchParams.set('maxRecords', '1')
  const res = await fetch(url.toString(), { headers: AUTH, cache: 'no-store' })
  if (!res.ok) return null
  const data = await res.json()
  return data.records?.[0] ?? null
}

async function findSubscriber(email: string): Promise<string | null> {
  const url = new URL(`${BASE_URL}/subscribers`)
  url.searchParams.set('filterByFormula', `{email}="${email}"`)
  url.searchParams.set('maxRecords', '1')
  const res = await fetch(url.toString(), { headers: AUTH, cache: 'no-store' })
  if (!res.ok) return null
  const data = await res.json()
  return data.records?.[0]?.id ?? null
}

async function deleteRecord(table: string, id: string) {
  await fetch(`${BASE_URL}/${table}/${id}`, { method: 'DELETE', headers: AUTH })
}

export async function POST(req: Request) {
  const { email, otp } = await req.json().catch(() => ({}))

  if (!email || !otp) {
    return NextResponse.json({ error: 'Email and OTP are required.' }, { status: 400 })
  }

  const normalised = email.trim().toLowerCase()
  const otpClean = String(otp).trim()

  if (!process.env.AIRTABLE_API_KEY || !process.env.AIRTABLE_BASE_ID) {
    return NextResponse.json({ error: 'Service unavailable.' }, { status: 503 })
  }

  const otpRecord = await findOtpRecord(normalised, otpClean)

  if (!otpRecord) {
    return NextResponse.json({ error: 'Invalid or expired code.' }, { status: 400 })
  }

  // Check expiry using Airtable's createdTime
  const created = new Date(otpRecord.createdTime).getTime()
  if (Date.now() - created > OTP_TTL_MS) {
    await deleteRecord('otps', otpRecord.id)
    return NextResponse.json({ error: 'Code has expired. Please request a new one.' }, { status: 400 })
  }

  const subscriberId = await findSubscriber(normalised)
  if (subscriberId) {
    await deleteRecord('subscribers', subscriberId)
  }

  await deleteRecord('otps', otpRecord.id)

  return NextResponse.json({ ok: true })
}
