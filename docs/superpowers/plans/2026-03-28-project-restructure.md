# Project Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganise the repo so each folder has one clear responsibility — `scraper/` for data, `notifications/` for email, `scripts/` for dev utilities — and remove root-level clutter.

**Architecture:** Move files between folders, update the four GitHub Actions workflow files to reflect new paths, and delete the duplicate GSC verification file at root. No Python code changes.

**Tech Stack:** Bash (git mv), YAML (workflow edits)

---

## File Map

| Action | From | To |
|---|---|---|
| Move | `scraper/announcement.py` | `notifications/announcement.py` |
| Move | `scraper/daily_alert.py` | `notifications/daily_alert.py` |
| Move | `scraper/test_email.py` | `notifications/test_email.py` |
| Move | `scraper/requirements.txt` | `requirements.txt` (root) |
| Move | `docs/build_docx.py` | `scripts/build_docx.py` |
| Move | `docs/demo_video.py` | `scripts/demo_video.py` |
| Move | `drawio/` | `docs/drawio/` |
| Delete | `google299bd36b9558fcc6.html` (root) | — duplicate of `web/public/` |
| Update | `.github/workflows/goldrates.yml` | fix `requirements.txt` path |
| Update | `.github/workflows/announcement.yml` | fix paths |
| Update | `.github/workflows/daily_alert.yml` | fix paths |
| Update | `.github/workflows/test_email.yml` | fix paths |

---

### Task 1: Create `notifications/` and move email scripts

**Files:**
- Create dir: `notifications/`
- Move: `scraper/announcement.py` → `notifications/announcement.py`
- Move: `scraper/daily_alert.py` → `notifications/daily_alert.py`
- Move: `scraper/test_email.py` → `notifications/test_email.py`

- [ ] **Step 1: Move the three email scripts**

```bash
mkdir notifications
git mv scraper/announcement.py notifications/announcement.py
git mv scraper/daily_alert.py notifications/daily_alert.py
git mv scraper/test_email.py notifications/test_email.py
```

- [ ] **Step 2: Verify the moves**

```bash
ls notifications/
# Expected: announcement.py  daily_alert.py  test_email.py
ls scraper/
# Expected: gold_bot.py  price_tracker.py  requirements.txt
```

- [ ] **Step 3: Commit**

```bash
git add notifications/ scraper/
git commit -m "move email scripts to notifications/"
```

---

### Task 2: Move `requirements.txt` to root

**Files:**
- Move: `scraper/requirements.txt` → `requirements.txt`

- [ ] **Step 1: Move the file**

```bash
git mv scraper/requirements.txt requirements.txt
```

- [ ] **Step 2: Verify**

```bash
ls requirements.txt
# Expected: requirements.txt
ls scraper/
# Expected: gold_bot.py  price_tracker.py
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt scraper/
git commit -m "move requirements.txt to root"
```

---

### Task 3: Create `scripts/` and move dev utility scripts

**Files:**
- Create dir: `scripts/`
- Move: `docs/build_docx.py` → `scripts/build_docx.py`
- Move: `docs/demo_video.py` → `scripts/demo_video.py`

- [ ] **Step 1: Move the utility scripts**

```bash
mkdir scripts
git mv docs/build_docx.py scripts/build_docx.py
git mv docs/demo_video.py scripts/demo_video.py
```

- [ ] **Step 2: Verify**

```bash
ls scripts/
# Expected: build_docx.py  demo_video.py
ls docs/
# Expected: no build_docx.py or demo_video.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/ docs/
git commit -m "move dev utility scripts to scripts/"
```

---

### Task 4: Move `drawio/` into `docs/`

**Files:**
- Move: `drawio/` → `docs/drawio/`

- [ ] **Step 1: Move the folder**

```bash
git mv drawio docs/drawio
```

- [ ] **Step 2: Verify**

```bash
ls docs/drawio/
# Expected: SKILL.md  references/
ls drawio 2>/dev/null || echo "gone"
# Expected: gone
```

- [ ] **Step 3: Commit**

```bash
git add docs/drawio/ drawio/
git commit -m "move drawio/ into docs/"
```

---

### Task 5: Delete duplicate GSC verification file at root

**Files:**
- Delete: `google299bd36b9558fcc6.html` (root — duplicate of `web/public/google299bd36b9558fcc6.html`)

- [ ] **Step 1: Confirm the duplicate exists in web/public/**

```bash
ls web/public/google299bd36b9558fcc6.html
# Expected: web/public/google299bd36b9558fcc6.html
```

- [ ] **Step 2: Delete the root copy**

```bash
git rm google299bd36b9558fcc6.html
```

- [ ] **Step 3: Commit**

```bash
git commit -m "remove duplicate GSC verification file from root"
```

---

### Task 6: Update all four workflow files

**Files:**
- Modify: `.github/workflows/goldrates.yml`
- Modify: `.github/workflows/announcement.yml`
- Modify: `.github/workflows/daily_alert.yml`
- Modify: `.github/workflows/test_email.yml`

- [ ] **Step 1: Update `goldrates.yml`**

Change `pip install -r scraper/requirements.txt` → `pip install -r requirements.txt`
(`python scraper/gold_bot.py` path stays the same — file didn't move)

```yaml
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scraper
        ...
        run: python scraper/gold_bot.py --scrape-only
```

- [ ] **Step 2: Update `announcement.yml`**

```yaml
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Send announcement
        ...
        run: python notifications/announcement.py
```

- [ ] **Step 3: Update `daily_alert.yml`**

```yaml
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Send daily alert
        ...
        run: python notifications/daily_alert.py
```

- [ ] **Step 4: Update `test_email.yml`**

```yaml
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Send test email
        ...
        run: python notifications/test_email.py
```

- [ ] **Step 5: Verify no remaining stale references**

```bash
grep -r "scraper/requirements" .github/
# Expected: no output

grep -r "scraper/announcement\|scraper/daily_alert\|scraper/test_email" .github/
# Expected: no output
```

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/
git commit -m "update workflow paths after restructure"
```

---

### Task 7: Final verification

- [ ] **Step 1: Confirm final structure**

```bash
ls scraper/
# Expected: gold_bot.py  price_tracker.py

ls notifications/
# Expected: announcement.py  daily_alert.py  test_email.py

ls scripts/
# Expected: build_docx.py  demo_video.py

ls requirements.txt
# Expected: requirements.txt

ls docs/drawio/
# Expected: SKILL.md  references/

ls google299bd36b9558fcc6.html 2>/dev/null || echo "gone"
# Expected: gone
```

- [ ] **Step 2: Confirm no broken path references remain**

```bash
grep -r "scraper/requirements\|scraper/announcement\|scraper/daily_alert\|scraper/test_email" .github/ .
# Expected: no matches outside of scraper/ itself
```

- [ ] **Step 3: Confirm git status is clean**

```bash
git status
# Expected: nothing to commit, working tree clean
```
