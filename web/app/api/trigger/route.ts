import { NextRequest, NextResponse } from 'next/server'

const GITHUB_OWNER    = 'unaveenj'
const GITHUB_REPO     = 'Gold-Notifier-SG'
const WORKFLOW_FILE   = 'goldrates.yml'

export async function POST(req: NextRequest) {
  const token        = process.env.TRIGGER_TOKEN
  const githubToken  = process.env.GITHUB_PAT

  // Validate secret token from request header
  const authHeader = req.headers.get('x-trigger-token')
  if (!token || authHeader !== token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  if (!githubToken) {
    return NextResponse.json({ error: 'GitHub PAT not configured' }, { status: 500 })
  }

  const res = await fetch(
    `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${githubToken}`,
        Accept: 'application/vnd.github+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ref: 'master' }),
    }
  )

  if (res.status === 204) {
    console.log('[trigger] Workflow dispatched successfully')
    return NextResponse.json({ ok: true, message: 'Workflow triggered' })
  }

  const body = await res.text()
  console.error('[trigger] GitHub API error:', res.status, body)
  return NextResponse.json({ error: 'Failed to trigger workflow', detail: body }, { status: res.status })
}
