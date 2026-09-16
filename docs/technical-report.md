# SolarGrid Energy Service Management System
## IT212 Group 1 — Technical Report

**Course:** Database Management Systems (IT212)  
**Group:** SolarGrid — Group 1  
**Authors:** Jemimah, Lina, Elijah, Gilbert, Yves, Mercy  
**Technology:** Python 3.11 · Flask · SQLAlchemy · MySQL 8.x  
**Repository:** [github.com/mercyXp/solargrid](https://github.com/mercyXp/solargrid)

---

## 1. Introduction

SolarGrid Energy Solutions installs solar systems for households, schools, farms, and businesses across Zambia. Previously, customer records, equipment, installations, and billing were tracked in spreadsheets. This project delivers a **database-backed web application** that centralises operations for staff and supports reporting, audit trails, and transactional integrity.

---

## 2. Requirements Analysis

### 2.1 Main Users

| Role | Responsibilities |
|------|------------------|
| Administrator | User management, full system access |
| Sales Rep | Register customers and sites |
| Operations Manager | Schedule installations, assign technicians |
| Technician | View assigned jobs, record maintenance |
| Warehouse Clerk | Register equipment, manage stock status |
| Customer Service | Raise and track service requests |
| Finance Officer | Invoices and payments |
| Auditor | Read-only access to reports and audit log |

### 2.2 System Requirements

The system manages ten business domains: **Customers, Sites, Equipment, Installations, Technicians, Service Requests, Maintenance History, Warranties, Invoices, Payments**.

Required functions: register customers/equipment, schedule installations, assign technicians, record completed work, raise invoices, record payments, and search installation histories.

### 2.3 Business Rules

| Rule | Enforced by |
|------|-------------|
| Customer email must be unique | DB (`uk_customer_email`) |
| Equipment serial number unique | DB (`uk_equipment_serial_number`) |
| One equipment item on one installation only | DB (`uk_installation_detail_equipment_id`) |
| Invoice due date ≥ issue date | DB (`chk_invoice_due_date`) |
| Only *In Progress* installations can be completed | Application (`InstallationService`) |
| Equipment must be *Available* or *Reserved* before install | Application + transaction |
| Role-based access to modules | Application (RBAC decorators) |
| Payment cannot exceed invoice balance | Application (`PaymentService`) |

**Database vs application:** Structural integrity (PK, FK, CHECK, UNIQUE) lives in MySQL. Workflow rules (status transitions, role permissions, multi-step transactions) live in the Flask service layer.

Full analysis: `docs/requirements.md`.

---

## 3. Conceptual Design (ERD)

**Entities:** Customer, Site, EquipmentType, Equipment, Installation, InstallationDetail, InstallationAssignment, Technician, ServiceRequest, ServiceAssignment, MaintenanceRecord, Warranty, Invoice, Payment, Staff, AuditLog.

**Key relationships:**

- Customer **1:N** Site  
- Site **1:N** Installation  
- Installation **M:N** Technician (via InstallationAssignment)  
- Installation **1:N** InstallationDetail **N:1** Equipment  
- Customer **1:N** Invoice **1:N** Payment  
- Equipment **1:1** Warranty (active lifecycle)  
- ServiceRequest **1:N** MaintenanceRecord  

ER diagram: `docs/ERD.png`, `docs/erd.md`.

---

## 4. Relational Schema

Sixteen InnoDB tables in `solargrid_db`. Primary keys are surrogate integer IDs (`customer_id`, `installation_id`, etc.). Foreign keys use `ON UPDATE CASCADE` and appropriate `ON DELETE` actions (RESTRICT for financial records, CASCADE for assignment junction rows).

Complete DDL: `database/schema.sql`  
Constraint reference: `database/constraints.sql`, `docs/database-design.md`.

---

## 5. Normalization

| Stage | Issue removed | Example |
|-------|---------------|---------|
| **1NF** | Repeating equipment groups on installation rows | Moved to `installation_detail` |
| **2NF** | Partial dependencies on composite keys | Junction tables use single-column PKs |
| **3NF** | Transitive dependencies | Equipment type attributes in `equipment_type`, not duplicated on each `equipment` row |

Detail: `docs/normalization.md`.

---

## 6. Database Implementation

- **DBMS:** MySQL 8.x (Workbench / CLI)  
- **Sample data:** `scripts/seed_database.py` — 12 customers, 12 sites, 15 equipment items, 5 technicians, 11+ installations, 12+ service requests, 12+ invoices  
- **Views (3):** `vw_outstanding_invoices`, `vw_expiring_warranties`, `vw_technician_workload`  
- **Stored procedures (4):** outstanding balances, revenue by month, unresolved services, transaction rollback demo  
- **Indexes:** 11 indexes on frequently filtered/joined columns — `database/indexes.sql`  
- **Users:** `solargrid` (app DML), `solargrid_auditor` (SELECT only), `solargrid_admin` (DDL) — `database/users.sql`

Demonstration queries: `database/queries.sql`.

---

## 7. Transactions & ACID

### Business operation: Complete Installation

When an operations manager completes an installation, the application executes one atomic transaction:

1. Validate status and equipment eligibility  
2. Set installation → *Completed*  
3. Link equipment to site, status → *Installed*  
4. Create warranty records  

**ACID properties:**

| Property | How demonstrated |
|----------|------------------|
| **Atomicity** | All steps commit together or `db.session.rollback()` on any failure |
| **Consistency** | FK and CHECK constraints remain satisfied after commit |
| **Isolation** | SQLAlchemy session / InnoDB row locks during transaction |
| **Durability** | Committed rows persist after server restart |

Implementation: `app/services/installation_service.py`.  
Rollback demo: `CALL sp_demo_transaction_rollback(...)` in `database/procedures.sql`.  
Explanation: `docs/acid-transactions.md`.

Secondary transaction: **Confirm Payment** (`PaymentService.confirm_payment`) updates payment and invoice balance atomically.

---

## 8. Indexing & Query Optimisation

Indexes target report and list-view columns: `equipment.status`, `installation.status`, `service_request(status, priority)`, `invoice.due_date`, `warranty.end_date`. These support warranty expiry, outstanding balance, and unresolved service reports without full table scans.

---

## 9. Security

- Passwords hashed with Werkzeug (never stored plain text)  
- Credentials from environment variables (`DATABASE_URL`, `SECRET_KEY`, `ADMIN_PASSWORD`) — not hard-coded in source  
- Eight application roles with permission matrix (`app/security/permissions.py`)  
- MySQL users follow least privilege (`database/users.sql`)  
- Audit log records create/update/delete actions  

Detail: `docs/security.md`.

---

## 10. Backup & Recovery

Logical backup via `mysqldump --single-transaction --routines`. Restoration documented in `database/backup-recovery.md`. **RPO:** up to 24 hours with daily dumps; transactions after last backup are lost.

---

## 11. Application Architecture

```
Browser → Flask routes → Service layer → SQLAlchemy ORM → MySQL
                ↓
         RBAC decorators + audit logging
```

- **Entry point:** `run.py`  
- **Modules:** customers, sites, equipment, installations, technicians, services, warranties, invoices, payments, reports  
- **UI:** Jinja2 templates, responsive CSS, role-aware navigation  
- **Deployment:** Railway (Gunicorn + MySQL plugin)

Architecture detail: `docs/architecture.md`.

---

## 12. Application Functionality

| Requirement | Implementation |
|-------------|----------------|
| Login | `/auth/login` — session-based staff authentication |
| CRUD | Full CRUD on customers, sites, staff; create/read/update on installations, services, invoices |
| Validation | Form + service-layer checks (status, amounts, dates) |
| Search/filter | Query params on list pages (name, status, date range) |
| Reports (5) | `/reports/*` — all assignment reports implemented |
| Transaction | Complete installation + confirm payment |
| Error handling | Flash messages, HTTP error pages, service exceptions |

---

## 13. NoSQL Complement (Oral Defence)

A relational database fits transactional billing and referential integrity. **NoSQL could complement** SolarGrid for:

- **Document store (MongoDB):** Equipment specification PDFs, installation photos, signed contracts  
- **Time-series DB:** Live inverter telemetry and performance monitoring  
- **Search engine (Elasticsearch):** Full-text search across service request notes  

These are read-heavy, schema-flexible workloads that sit alongside — not replace — the core MySQL OLTP database.

---

## 14. Conclusion

SolarGrid meets IT212 Group 1 requirements: normalised MySQL schema, comprehensive SQL artefacts (views, procedures, indexes, users, backup docs), atomic business transactions, and a working Flask application with login, CRUD, search, five reports, and direct database connectivity. The repository contains all scripts, documentation, and sample data needed for submission and live demonstration.

**Setup:** See `README.md` and `docs/submission-checklist.md`.
