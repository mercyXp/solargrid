# SolarGrid Energy Solutions — Management System

Production-quality Flask web application for managing solar installation operations, inventory, service requests, warranties, invoicing, and reporting.

Based on **IT212 Database Design: Stages 1 & 2** reference specification.

## Authors

This project was developed by **Jemimah**, **Lina**, **Elijah**, **Gilbert**, **Yves**, and **Mercy**.

## Stack

- **Backend:** Python Flask (application factory, blueprints)
- **Frontend:** HTML5, Bootstrap 5, Vanilla JavaScript, Chart.js
- **Database:** MySQL 8.x via SQLAlchemy + Flask-Migrate
- **Security:** bcrypt, CSRF, RBAC, rate limiting, audit logging

## Quick Start

**New to programming?** Start here: [docs/beginner-setup.md](docs/beginner-setup.md)  
**Already have Python/MySQL?** [docs/quick-start.md](docs/quick-start.md)

```powershell
net start MYSQL80                                    # Start MySQL (Admin PowerShell)
cd solargrid
python -m venv venv && .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env                               # Edit SECRET_KEY if you like

$env:MYSQL_ROOT_PASSWORD="your-root-password"
python scripts/setup_database.py                     # Create DB + user

$env:FLASK_APP="run.py"
flask db upgrade
python scripts/seed_database.py
python run.py
```

Open http://localhost:5000 → **Sign in** with `admin` / `SolarGrid2026!`

See [docs/quick-start.md](docs/quick-start.md) for Mac/Linux, troubleshooting, SQL scripts, and all demo login accounts.

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

- [Beginner Setup (from zero)](docs/beginner-setup.md)
- [Local Quick Start](docs/quick-start.md)
- [Team Task Checklists (by role)](docs/team-tasks.md)
- [Technical Report (IT212 submission)](docs/technical-report.md)
- [Submission Checklist](docs/submission-checklist.md)
- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Database Design](docs/database-design.md)
- [Normalization (1NF/2NF/3NF)](docs/normalization.md)
- [ACID Transactions](docs/acid-transactions.md)
- [ERD](docs/erd.md)
- [Security](docs/security.md)
- [Traceability Matrix](docs/traceability-matrix.md)

## Key Business Operations

- **Complete Installation:** Atomic transaction — updates installation, equipment, creates warranties
- **Confirm Payment:** Atomic transaction — records payment, updates invoice amount_paid and status
- **RBAC:** Eight roles with centralized permission checks on every route

## License

Academic / internal use — SolarGrid Energy Solutions IT212 project.
