# Project Restructure Design
**Date:** 2026-03-28

## Problem

The `scraper/` folder contains scripts that are not scrapers (announcement mailer, daily alert, test utility). Root-level clutter includes a duplicate GSC verification file and a stray `drawio/` plugin folder. `docs/` contains Python utility scripts that have nothing to do with documentation.

## Target Structure

```
Gold-Notifier-SG/
├── scraper/                    ← data layer (was: scraper/)
│   ├── gold_bot.py             ← unchanged
│   └── price_tracker.py        ← unchanged
├── notifications/              ← email layer (new folder, split from scraper/)
│   ├── announcement.py         ← moved from scraper/
│   ├── daily_alert.py          ← moved from scraper/
│   └── test_email.py           ← moved from scraper/
├── requirements.txt            ← moved from scraper/ to root (shared)
├── scripts/                    ← dev/utility scripts (new folder)
│   ├── build_docx.py           ← moved from docs/
│   └── demo_video.py           ← moved from docs/
├── docs/                       ← documentation only
│   ├── superpowers/
│   ├── screenshots/
│   ├── architecture.drawio
│   ├── architecture.svg
│   ├── medium_article.md
│   ├── medium_article.docx
│   ├── GoldAlert_SG_Technical_Documentation.pdf
│   └── TECHNICAL_DOCUMENTATION.md
├── web/                        ← Next.js frontend (unchanged)
├── .github/workflows/          ← all 4 workflow path references updated
└── README.md
```

## What Changes

| File | From | To |
|---|---|---|
| `announcement.py` | `scraper/` | `notifications/` |
| `daily_alert.py` | `scraper/` | `notifications/` |
| `test_email.py` | `scraper/` | `notifications/` |
| `requirements.txt` | `scraper/` | root |
| `build_docx.py` | `docs/` | `scripts/` |
| `demo_video.py` | `docs/` | `scripts/` |
| `google299bd36b9558fcc6.html` | root | deleted (duplicate of `web/public/`) |
| `drawio/` | root | `docs/drawio/` |

## Workflow Updates Required

All 4 workflows reference `scraper/requirements.txt`. After the move:
- `goldrates.yml` → `requirements.txt` (root), `scraper/gold_bot.py` (unchanged)
- `announcement.yml` → `requirements.txt` (root), `notifications/announcement.py`
- `daily_alert.yml` → `requirements.txt` (root), `notifications/daily_alert.py`
- `test_email.yml` → `requirements.txt` (root), `notifications/test_email.py`

## Out of Scope

- No changes to `web/` (Next.js frontend)
- No changes to Python script internals
- No changes to GitHub secrets or Airtable config
