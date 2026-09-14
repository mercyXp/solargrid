# SolarGrid Energy Solutions — Management System

Production-quality Flask web application for managing solar installation operations, inventory, service requests, warranties, invoicing, and reporting.

Based on **IT212 Database Design: Stages 1 & 2** reference specification.

## Stack

- **Backend:** Python Flask (application factory, blueprints)
- **Frontend:** HTML5, Bootstrap 5, Vanilla JavaScript, Chart.js
- **Database:** MySQL 8.x via SQLAlchemy + Flask-Migrate
- **Security:** bcrypt, CSRF, RBAC, rate limiting, audit logging

## Quick Start

### 1. Prerequisites

- Python 3.11+
- MySQL 8.x
- MySQL Workbench (optional, for SQL scripts)

### 2. Create Database

```sql
CREATE DATABASE solargrid_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE solargrid_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Install & Configure

```bash
cd solargrid
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # Edit DATABASE_URL and SECRET_KEY
```

### 4. Initialize Database

```bash
set FLASK_APP=run.py
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
python scripts/seed_database.py
```

### 5. Run

```bash
python run.py
```

Open http://localhost:5000

### Development Credentials (after seeding)

| Username | Role | Password |
|----------|------|----------|
| admin | Administrator | SolarGrid2026! |
| salesrep | Sales Rep | SolarGrid2026! |
| opsmgr | Operations Manager | SolarGrid2026! |
| finance | Finance Officer | SolarGrid2026! |
| auditor | Auditor | SolarGrid2026! |

**Do not use these passwords in production.**

## Project Structure

```
solargrid/
├── app/                  # Application package
│   ├── models/           # 15 SQLAlchemy entities + AuditLog
│   ├── routes/           # Flask blueprints
│   ├── services/         # Business logic layer
│   ├── security/         # RBAC, auth utilities
│   ├── templates/        # Jinja2 templates
│   └── static/           # CSS, JS
├── database/             # MySQL Workbench SQL scripts
├── docs/                 # Requirements, architecture, ERD
├── scripts/              # Seed and admin creation
├── tests/                # pytest suite
└── migrations/           # Alembic migrations
```

## Testing

```bash
pytest
```

Requires `solargrid_test_db` MySQL database (see `.env.example` TEST_DATABASE_URL).

## Documentation

- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Database Design](docs/database-design.md)
- [ERD](docs/erd.md)
- [Security](docs/security.md)
- [Traceability Matrix](docs/traceability-matrix.md)

## Key Business Operations

- **Complete Installation:** Atomic transaction — updates installation, equipment, creates warranties
- **Confirm Payment:** Atomic transaction — records payment, updates invoice amount_paid and status
- **RBAC:** Eight roles with centralized permission checks on every route

## License

Academic / internal use — SolarGrid Energy Solutions IT212 project.
