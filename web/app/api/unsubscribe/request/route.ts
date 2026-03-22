import { NextResponse } from 'next/server'
import nodemailer from 'nodemailer'

const BASE_URL = `https://api.airtable.com/v0/${process.env.AIRTABLE_BASE_ID}`
const AUTH = { Authorization: `Bearer ${process.env.AIRTABLE_API_KEY}` }

async function findSubscriber(email: string): Promise<string | null> {
  const url = new URL(`${BASE_URL}/subscribers`)
  url.searchParams.set('filterByFormula', `{email}="${email}"`)
  url.searchParams.set('maxRecords', '1')
  const res = await fetch(url.toString(), { headers: AUTH, cache: 'no-store' })
  if (!res.ok) return null
  const data = await res.json()
  return data.records?.[0]?.id ?? null
}

async function deleteExistingOtps(email: string) {
  const url = new URL(`${BASE_URL}/otps`)
  url.searchParams.set('filterByFormula', `{email}="${email}"`)
  const res = await fetch(url.toString(), { headers: AUTH, cache: 'no-store' })
  if (!res.ok) return
  const data = await res.json()
  for (const record of data.records ?? []) {
    await fetch(`${BASE_URL}/otps/${record.id}`, {
      method: 'DELETE',
      headers: AUTH,
    })
  }
}

async function saveOtp(email: string, otp: string) {
  await fetch(`${BASE_URL}/otps`, {
    method: 'POST',
    headers: { ...AUTH, 'Content-Type': 'application/json' },
    body: JSON.stringify({ fields: { email, otp } }),
  })
}

async function sendOtpEmail(email: string, otp: string) {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.GMAIL_USER,
      pass: process.env.GMAIL_APP_PASSWORD,
    },
  })

  await transporter.sendMail({
    from: process.env.GMAIL_USER,
    to: email,
    subject: 'GoldAlert SG — Unsubscribe Confirmation',
    text: [
      'You requested to unsubscribe from GoldAlert SG.',
      '',
      `Your confirmation code is: ${otp}`,
      '',
      'This code expires in 10 minutes.',
      '',
      'If you did not request this, ignore this email — your subscription is safe.',
    ].join('\n'),
  })
}

export async function POST(req: Request) {
  const { email } = await req.json().catch(() => ({}))

  if (!email || !email.includes('@')) {
    return NextResponse.json({ error: 'Invalid email.' }, { status: 400 })
  }

  const normalised = email.trim().toLowerCase()

  if (!process.env.AIRTABLE_API_KEY || !process.env.AIRTABLE_BASE_ID) {
    return NextResponse.json({ error: 'Service unavailable.' }, { status: 503 })
  }

  const subscriberId = await findSubscriber(normalised)
  if (!subscriberId) {
    // Don't reveal whether email exists — return same response
    return NextResponse.json({ ok: true })
  }

  const otp = String(Math.floor(100000 + Math.random() * 900000))

  await deleteExistingOtps(normalised)
  await saveOtp(normalised, otp)
  await sendOtpEmail(normalised, otp)

  return NextResponse.json({ ok: true })
}
