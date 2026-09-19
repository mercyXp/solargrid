# SolarGrid — Team Task Checklists

**Deadline:** 12/10/2026 (IT212) + production polish  
**Goal:** Understand the Cursor-built system, fill gaps, redesign UI, pass demo, launch safely.

---

## Your roles

| Member | Role | Focus |
|--------|------|--------|
| **Mercy** | Technical Lead | Integration, code review, unblocks everyone, owns architecture |
| **Gilbert** | Database Architect | MySQL, ERD, SQL, migrations, data integrity |
| **Jemimah** | Frontend Developer | Landing page, dashboard, Chart.js, templates, CSS |
| **Elijah** | Backend Developer | Flask routes, services, auth, business logic, APIs |
| **Yves** | Software Tester & DevOps | pytest, manual QA, Railway, backup, security |
| **Linah** | Technical Writer | Reports, user guides, demo script, submission |

**Rule:** Cursor AI built v1. Your job is to **learn it, own it, improve it, and defend it** in oral examination.

---

## Phase 0 — Learn the system (Week 1, all members)

Everyone completes this before changing code.

### 0.1 Run it locally
- [ ] Follow [beginner-setup.md](beginner-setup.md) from clone to login
- [ ] Log in as `admin`, `opsmgr`, `finance`, `auditor`
- [ ] Note what each role can and cannot see

### 0.2 Understand the folder map

```
app/
├── __init__.py          ← App factory (creates Flask app)
├── models/              ← Database tables as Python classes
├── routes/              ← URLs + page logic (thin)
├── services/            ← Business rules + transactions (thick)
├── security/            ← Login, permissions, password hashing
├── templates/           ← HTML (Jinja2)
└── static/css, js       ← Styles and scripts

database/                ← SQL scripts (views, procedures, indexes)
migrations/              ← Schema version history
scripts/                 ← Seed data, setup
docs/                    ← Reports and guides
tests/                   ← Automated tests
```

### 0.3 Trace one full business flow (pair up)

**Installation flow — click then read code:**

1. Browser: Schedule installation → assign equipment → complete  
2. Code: `routes/installations.py` → `services/installation_service.py` → `models/`  
3. Database: MySQL Workbench → `installation`, `installation_detail`, `equipment`, `warranty`

Each member writes **5 sentences** explaining this flow in their own words (Linah collects for report).

### 0.4 Oral defence prep (shared)

Every member must be able to:
- [ ] Explain Customer → Site → Installation → Equipment
- [ ] Run one CRUD action in the app
- [ ] Run one SQL query (JOIN or procedure)
- [ ] Explain the complete-installation transaction

---

## Known gaps (Cursor v1 → your v2)

| Gap | Priority | Primary owner |
|-----|----------|---------------|
| Staff **change own password** | P0 | Elijah + Jemimah |
| **Forgot password** (email or admin reset) | P1 | Elijah + Gilbert |
| **Product catalog** — only 3 products, poor labeling | P0 | Gilbert + Jemimah |
| Landing page **redesign** | P1 | Jemimah |
| Dashboard **redesign** | P1 | Jemimah + Elijah |
| Chart.js charts **polish** | P1 | Jemimah |
| Equipment edit route | P2 | Elijah |
| Invoice line items / PDF | P2 | Elijah |
| Email notifications | P3 | Elijah (post-launch) |
| Production hardening | P0 | Yves + Mercy |

**Already exists (do not rebuild):**
- Admin can reset staff password via **Staff → Edit** (`app/routes/staff.py`)
- Login, RBAC, 8 roles, audit log, 5 reports, transactions

---

# Role checklists

---

## Mercy — Technical Lead

### Learn
- [ ] Read `app/__init__.py` — how blueprints register
- [ ] Read `config.py` — local vs Railway database
- [ ] Read `app/security/permissions.py` — all 8 roles
- [ ] Skim every file in `app/services/`

### Build & coordinate
- [ ] Create GitHub **Issues** or shared board from this doc
- [ ] Review every PR before merge (even small)
- [ ] Weekly 30-min standup (Mon + Thu)
- [ ] Pair with each member once on their first task
- [ ] Keep `main` branch deployable on Railway

### Integration tasks
- [ ] After Elijah adds change-password: test all roles
- [ ] After Jemimah redesign: check mobile + login flow
- [ ] After Gilbert expands products: re-run seed + reports
- [ ] Sign off: “Ready for demo” checklist (see bottom)

### Oral defence
- [ ] Backup presenter for any topic
- [ ] Explain full architecture in 3 minutes

---

## Gilbert — Database Architect

### Learn
- [ ] Read all files in `app/models/`
- [ ] Read `database/schema.sql` and `migrations/versions/`
- [ ] Run every file in `database/queries.sql` in Workbench
- [ ] Read `docs/normalization.md` and be able to teach it

### P0 — Data & catalog
- [ ] Expand **product catalog** (`equipment_type`) to **12+ sellable items** in `scripts/seed_database.py`  
      Categories: panels, inverters, batteries, charge controllers, mounting
- [ ] Document: *“Products for sale = Equipment Types; stock units = Equipment”* in technical report
- [ ] Add sample `rating` for every product (400W, 5 kW, 13.5 kWh)
- [ ] Verify 10+ rows in: customer, site, equipment, installation, invoice, service_request

### P0 — SQL & IT212
- [ ] Apply and test: `indexes.sql`, `views.sql`, `procedures.sql`
- [ ] Prepare live demo: 1 JOIN, 1 subquery, 1 view, 1 procedure
- [ ] Update ERD if schema changes (e.g. password reset tokens table — see Elijah)

### P1 — Forgot password (with Elijah)
- [ ] Design `password_reset_token` table (if email reset chosen):

```sql
-- Example — Elijah implements migration
password_reset_token (
  token_id PK, staff_id FK, token_hash, expires_at, used_at
)
```

- [ ] Or document **admin-only reset** as v1 policy if no email server

### P2 — Performance
- [ ] Run `EXPLAIN` on warranty expiry + outstanding balance queries
- [ ] Document index rationale in report (already in `indexes.sql`)

### Deliverables
- [ ] Updated `docs/erd.md` + `docs/ERD.png`
- [ ] `backup/solargrid_db_YYYYMMDD.sql` exists
- [ ] Can draw ERD and explain 3NF from memory

---

## Jemimah — Frontend Developer

### Learn
- [ ] Read `app/templates/base.html` — layout, sidebar, permissions in templates
- [ ] Read `app/templates/dashboard/index.html` — Chart.js setup
- [ ] Read `app/static/css/main.css` and `landing.css`
- [ ] Read `app/templates/landing/index.html` structure
- [ ] Jinja2: `{% extends %}`, `{% block %}`, `{{ variable }}`, `{% for %}`

### P0 — Navigation & labels
- [ ] Rename **Equipment Types** → **Products** (sidebar, page titles, breadcrumbs)
- [ ] Products page: clear price list columns (category, model, rating, ZMK price)
- [ ] Add **Sign in** visible on desktop navbar (done — verify)

### P0 — Staff change password UI (with Elijah)
- [ ] New page: **Account → Change password** (or profile dropdown in `base.html`)
- [ ] Form: current password, new password, confirm new password
- [ ] Show validation errors (match `validate_password_strength` messages)
- [ ] Success flash: “Password updated”

### P1 — Landing page redesign
- [ ] Hero: clearer value prop for SolarGrid Zambia
- [ ] Add **“Our products”** section (read-only cards from product types OR static showcase)
- [ ] Team section: real names, roles, student numbers, photos
- [ ] Mobile: test hamburger menu, button sizes, readable text
- [ ] Keep yellow SolarGrid brand; improve spacing and typography
- [ ] Files: `landing/index.html`, `static/css/landing.css`, `static/js/landing.js`

### P1 — Dashboard redesign
- [ ] KPI cards: clearer labels, icons, click-through to relevant module
- [ ] Improve layout grid (Bootstrap 5)
- [ ] Empty states when no data
- [ ] Role-aware dashboard (finance sees money KPIs, ops sees installs)
- [ ] Files: `templates/dashboard/index.html`, `routes/dashboard.py`, `static/css/main.css`

### P1 — Chart.js polish
- [ ] Consistent color palette (match brand yellow `#F4C430`)
- [ ] Chart titles, axis labels, tooltips with **ZMK** formatting
- [ ] Responsive charts (resize on mobile)
- [ ] Loading state when data is empty
- [ ] Consider: doughnut for equipment status, bar for revenue (already started — refine)
- [ ] File: `dashboard/index.html` + optional `static/js/dashboard.js` (extract JS from template)

### P2 — Forgot password UI (with Elijah)
- [ ] Login page: “Forgot password?” link
- [ ] Request reset page (email field)
- [ ] Reset password page (new password + token from URL)

### P2 — UX polish (all modules)
- [ ] Consistent page headers and breadcrumbs
- [ ] Confirm dialogs on delete/cancel installation
- [ ] Better empty tables (“No customers yet — Add one”)

### Deliverables
- [ ] 10+ screenshots for Linah’s report
- [ ] 5-minute UI demo path documented

---

## Elijah — Backend Developer

### Learn
- [ ] Read `app/routes/auth.py` — login, session, health check
- [ ] Read `app/security/decorators.py` — `@permission_required`
- [ ] Read `app/services/installation_service.py` — **the** transaction demo
- [ ] Read `app/services/payment_service.py`
- [ ] Trace: form POST → route → service → `db.session.commit()`

### P0 — Change own password
- [ ] New route: `GET/POST /account/change-password` (or `/auth/change-password`)
- [ ] Require: current password verified with `verify_password()`
- [ ] New password: `validate_password_strength()` + must match confirm field
- [ ] Update `staff.password_hash`, `log_audit("password_changed", ...)`
- [ ] Cannot reuse current password (optional nice rule)
- [ ] Register blueprint in `app/__init__.py`
- [ ] Only logged-in staff — no admin permission needed (every user)

### P1 — Forgot password (choose one approach)

**Option A — Admin reset only (simplest, no email):**
- [ ] Document that staff contact admin
- [ ] Admin uses existing Staff → Edit → new password
- [ ] Add audit log message

**Option B — Token-based reset (better for production):**
- [ ] Migration: `password_reset_token` table (Gilbert designs)
- [ ] `POST /auth/forgot-password` — create token, expiry 1 hour
- [ ] For dev: log reset link to console or flash token (no email server needed)
- [ ] `GET/POST /auth/reset-password/<token>` — set new password, mark token used
- [ ] Rate limit with Flask-Limiter

### P1 — Products backend support
- [ ] Ensure `equipment.types_index` returns all fields Jemimah needs
- [ ] Optional: public read-only API `/api/products` for landing page (JSON)
- [ ] Expand seed with Gilbert

### P1 — Dashboard data
- [ ] Review `app/routes/dashboard.py` — ensure chart data is accurate
- [ ] Add any missing KPIs for redesigned dashboard
- [ ] Optimize queries if dashboard is slow (with Gilbert)

### P2 — Missing CRUD
- [ ] Equipment **edit** route (`equipment/<id>/edit`)
- [ ] Warranty create (optional — auto-created on install completion)

### P0 — Business rules audit
- [ ] Complete installation: only In Progress, equipment Available/Reserved
- [ ] Payment: cannot exceed invoice balance
- [ ] Test each rule fails with clear flash message

### Deliverables
- [ ] Demo complete installation + rollback explanation
- [ ] Demo change-password flow
- [ ] All new routes have permission checks + audit log where appropriate

---

## Yves — Software Tester & DevOps

### Learn
- [ ] Read `tests/` — how pytest-flask works
- [ ] Read `docs/quick-start.md` and `database/backup-recovery.md`
- [ ] Read Railway config: `railway.json`, `Procfile`, `scripts/railway_bootstrap.py`
- [ ] Run app locally and on production URL

### P0 — Test plan (write in `docs/test-plan.md`)
- [ ] Login: valid, invalid, locked/rate-limited
- [ ] Each role: list what they can access (RBAC matrix test)
- [ ] CRUD: customer, site, equipment, installation, invoice, payment
- [ ] Transaction: complete installation success + failure
- [ ] Change password: new flow after Elijah builds it
- [ ] All 5 reports return data
- [ ] Search/filter on list pages

### P0 — Automated tests
- [ ] Run `pytest` — fix or document failures
- [ ] Add test: change password success
- [ ] Add test: change password wrong current password fails
- [ ] Add test: unauthorized role gets 403

### P0 — Security & production
- [ ] Apply `database/users.sql` — demo SHOW GRANTS
- [ ] Confirm no secrets in git (`grep` for passwords in code)
- [ ] Railway: `/health` returns ok, `staff_count > 0`
- [ ] Production admin password **not** `SolarGrid2026!`
- [ ] Create mysqldump backup in `backup/`
- [ ] Test restore once on local MySQL

### P1 — Regression after redesign
- [ ] Full regression pass after Jemimah’s landing + dashboard merge
- [ ] Mobile smoke test (phone or browser dev tools)
- [ ] Cross-browser: Chrome + Edge

### P1 — Performance smoke
- [ ] Dashboard loads under 3 seconds with seed data
- [ ] Report pages with 12+ records paginate correctly

### P2 — Launch checklist
- [ ] Railway env vars documented (not in repo)
- [ ] Pre-deploy bootstrap runs migrations
- [ ] Error pages 404/500 styled
- [ ] Optional: GitHub Action running pytest on push

### Deliverables
- [ ] `docs/test-plan.md` with pass/fail checklist
- [ ] Backup file in repo
- [ ] Security demo script for oral defence

---

## Linah — Technical Writer

### Learn
- [ ] Read entire `docs/technical-report.md`
- [ ] Run [beginner-setup.md](beginner-setup.md) yourself — note confusing steps
- [ ] Shadow each member’s demo once

### P0 — IT212 submission
- [ ] Finalize **technical report** (concise — design + implementation + screenshots)
- [ ] **Submission checklist** — every compulsory requirement ticked
- [ ] ERD, normalization, ACID section accurate after team changes
- [ ] GitHub repo clean: README, all SQL, backup, docs
- [ ] Tag release `v1.0-submission` by 5 Oct

### P0 — Demo materials
- [ ] **`docs/demo-script.md`** — 12 min, speaker per section
- [ ] One-page **login credentials** sheet for demo day
- [ ] **FAQ for oral defence** — 20 likely lecturer questions + answers

### P1 — User documentation
- [ ] **`docs/user-guide.md`** — one section per role (how to do their daily job)
- [ ] Update [beginner-setup.md](beginner-setup.md) if setup steps change
- [ ] **Change password** instructions for staff
- [ ] **Admin guide**: reset staff password, run seed, run backup

### P1 — “We built this” narrative
- [ ] Section: *What Cursor AI generated vs what the team added* (honest, academic integrity)
- [ ] List team contributions: redesign, change password, expanded products, tests, docs

### P2 — Launch docs
- [ ] **`docs/production-runbook.md`** — deploy, rollback, backup schedule
- [ ] Privacy note: customer data handling

### Deliverables
- [ ] Printed demo script for each member
- [ ] Final PDF/Markdown report ready for submission

---

## Suggested build order (3 weeks)

### Week 1 — Learn + P0 fixes
| Day | Focus |
|-----|--------|
| Mon–Tue | Phase 0 for everyone |
| Wed–Thu | Elijah: change password · Gilbert: expand products seed |
| Fri | Jemimah: Products UI + change password form |
| Sat | Yves: test plan + RBAC testing |
| Sun | Mercy: integration review |

### Week 2 — Redesign + P1
| Day | Focus |
|-----|--------|
| Mon–Wed | Jemimah: landing + dashboard + Chart.js |
| Wed–Thu | Elijah: dashboard data + forgot password (Option A or B) |
| Fri | Gilbert: SQL demo prep + ERD update |
| Sat | Yves: full regression + backup |
| Sun | Linah: mock demo #1 |

### Week 3 — Polish + submit
| Day | Focus |
|-----|--------|
| 2 Oct | Feature freeze |
| 5 Oct | Submission package on GitHub |
| 8 Oct | Dress rehearsal ×2 |
| 12 Oct | Live demo |

---

## Production launch checklist (whole team)

Before calling it “live to the world”:

- [ ] All P0 tasks complete
- [ ] Production passwords rotated
- [ ] HTTPS on Railway (default)
- [ ] Backup schedule defined
- [ ] At least 2 team members can deploy without Mercy
- [ ] User guide for SolarGrid staff
- [ ] Known limitations documented (no email = admin reset only, etc.)

---

## “Done” definition

**IT212 pass:** Demo runs twice, all 6 members pass mock oral, GitHub complete.  
**Production ready:** P0 + P1 complete, test plan green, backup tested, Railway stable.

---

## Quick reference — who touches which files

| Feature | Files |
|---------|--------|
| Change password | `routes/auth.py` or new `routes/account.py`, `templates/account/`, `security_utils.py` |
| Forgot password | `routes/auth.py`, new model/migration, `templates/auth/` |
| Products catalog | `seed_database.py`, `templates/equipment/types_index.html`, `base.html` nav |
| Landing redesign | `templates/landing/`, `static/css/landing.css`, `static/js/landing.js` |
| Dashboard + charts | `routes/dashboard.py`, `templates/dashboard/index.html`, `static/js/` |
| Products seed | `scripts/seed_database.py` |
| Tests | `tests/test_*.py` |
| Docs | `docs/*.md` |

---

*Mercy maintains this file — update checkboxes in GitHub Issues or here as tasks complete.*
