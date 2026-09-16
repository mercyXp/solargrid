# IT212 Group 1 — Submission Checklist

**Project:** SolarGrid Energy Service Management System  
**Repository:** [mercyXp/solargrid](https://github.com/mercyXp/solargrid)  
**Deadline:** 12/10/2026

Use this checklist before submission and live demonstration.

## Documentation

| Item | Location | Status |
|------|----------|--------|
| Concise technical report | `docs/technical-report.md` | ✅ |
| Requirements analysis & business rules | `docs/requirements.md` | ✅ |
| ERD (entities, relationships, cardinalities) | `docs/erd.md`, `docs/ERD.png`, `docs/er.svg` | ✅ |
| Relational schema (PK, FK, constraints) | `docs/database-design.md`, `database/schema.sql` | ✅ |
| Normalization evidence (1NF, 2NF, 3NF) | `docs/normalization.md` | ✅ |
| ACID / transaction explanation | `docs/acid-transactions.md` | ✅ |
| Security (users, roles, least privilege) | `docs/security.md`, `database/users.sql` | ✅ |
| Backup & recovery | `database/backup-recovery.md`, `backup/` | ✅ |
| Traceability matrix | `docs/traceability-matrix.md` | ✅ |

## Database (MySQL 8.x)

| Item | Location | Status |
|------|----------|--------|
| DDL — CREATE TABLE scripts | `database/schema.sql`, `migrations/versions/b000f2425625_initial_schema.py` | ✅ |
| DML — sample data (10+ per major table) | `scripts/seed_database.py`, `database/seed.sql` | ✅ |
| SELECT, filtering, sorting, aggregates | `database/queries.sql` | ✅ |
| INNER JOIN + other JOIN type | `database/queries.sql` (INNER, LEFT) | ✅ |
| Meaningful subquery | `database/queries.sql` | ✅ |
| At least 2 views | `database/views.sql` (3 views) | ✅ |
| At least 2 stored procedures | `database/procedures.sql` (4 procedures) | ✅ |
| Transaction / ACID demo | `app/services/installation_service.py`, `sp_demo_transaction_rollback` | ✅ |
| Indexes + rationale | `database/indexes.sql` | ✅ |
| Database users / roles | `database/users.sql` | ✅ |
| Master install script | `database/install.sql` | ✅ |

## Application (Flask + MySQL)

| Item | Location | Status |
|------|----------|--------|
| Login / user identification | `app/routes/auth.py` | ✅ |
| Data-entry forms (major entities) | `app/templates/*/` | ✅ |
| CRUD (Create, Read, Update, Delete) | Routes per module | ✅ |
| Business rule validation | Services + model constraints | ✅ |
| Search / filter | List views (customers, equipment, etc.) | ✅ |
| At least 2 reports | `app/routes/reports.py` (5 reports) | ✅ |
| Multi-table business transaction | `InstallationService.complete_installation()` | ✅ |
| Error handling | Flash messages, try/except in services | ✅ |
| Direct DB connection (not hard-coded data) | SQLAlchemy via `config.py` | ✅ |

## Required Reports (Assignment §4)

| Report | App route | SQL support |
|--------|-----------|-------------|
| 1. Warranties approaching expiry | `/reports/warranty-expiry` | `vw_expiring_warranties` |
| 2. Unresolved service requests | `/reports/unresolved-services` | `sp_unresolved_service_requests` |
| 3. Technician workload | `/reports/technician-workload` | `vw_technician_workload` |
| 4. Outstanding customer balances | `/reports/outstanding-balances` | `vw_outstanding_invoices`, `sp_outstanding_balances_by_customer` |
| 5. Revenue by period | `/reports/revenue` | `sp_revenue_by_month` |

## Business Transaction (Assignment §5)

**Complete Installation** — atomic steps:

1. Validate installation is *In Progress*
2. Verify equipment is *Available* or *Reserved*
3. Mark installation *Completed*
4. Record installed equipment on site
5. Update equipment status to *Installed*
6. Create warranty records

**Implementation:** `app/services/installation_service.py` → `complete_installation()`  
**Rollback demo:** `database/procedures.sql` → `sp_demo_transaction_rollback`

## Live Demo Script (prepare each member)

1. **Login** as different roles (admin, opsmgr, finance, technician)
2. **CRUD** — register customer, add site, schedule installation
3. **Transaction** — complete installation; show DB before/after; demo rollback
4. **Reports** — run all 5 from `/reports`
5. **SQL** — run JOIN, subquery, view, stored procedure in MySQL Workbench
6. **Security** — `SHOW GRANTS` for `solargrid` vs `solargrid_auditor`
7. **Backup** — show mysqldump file and restore steps
8. **NoSQL** — explain where document/KV store could complement (e.g. equipment spec sheets, photos)

## Quick Setup Commands

```powershell
cd C:\solargrid
.\venv\Scripts\Activate.ps1
flask db upgrade
python scripts/seed_database.py --reset
mysql -u root -p solargrid_db < database/indexes.sql
mysql -u root -p solargrid_db < database/views.sql
mysql -u root -p solargrid_db < database/procedures.sql
python run.py
```

**Demo login:** `admin` / `SolarGrid2026!` (after seed) or `ADMIN_PASSWORD` in production.
