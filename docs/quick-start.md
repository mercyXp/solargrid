# SolarGrid — Local Quick Start

Get the app running on your machine in about **10 minutes** (Windows-focused; Mac/Linux notes included).

---

## What you need

| Tool | Version |
|------|---------|
| Python | 3.11 or newer |
| MySQL | 8.x |
| Git | Any recent version |

Optional: **MySQL Workbench** (to run SQL scripts for views/procedures).

---

## 1. Clone the project

```powershell
git clone https://github.com/mercyXp/solargrid.git
cd solargrid
```

---

## 2. Start MySQL

**Windows** — open PowerShell **as Administrator**:

```powershell
net start MYSQL80
```

**Mac** (Homebrew):

```bash
brew services start mysql
```

**Linux**:

```bash
sudo systemctl start mysql
```

If this step is skipped, login will fail with *“Can't connect to MySQL server”*.

---

## 3. Create the database & app user

### Option A — automated script (recommended)

```powershell
cd C:\solargrid
$env:MYSQL_ROOT_PASSWORD="your-mysql-root-password"
python scripts/setup_database.py
```

This creates:

- Databases: `solargrid_db`, `solargrid_test_db`
- App user: `solargrid` / `solargrid_pass`

### Option B — MySQL Workbench / CLI

Run as root:

```sql
CREATE DATABASE solargrid_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE solargrid_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'solargrid'@'localhost' IDENTIFIED BY 'solargrid_pass';
CREATE USER IF NOT EXISTS 'solargrid'@'127.0.0.1' IDENTIFIED BY 'solargrid_pass';
GRANT ALL PRIVILEGES ON solargrid_db.* TO 'solargrid'@'localhost';
GRANT ALL PRIVILEGES ON solargrid_db.* TO 'solargrid'@'127.0.0.1';
GRANT ALL PRIVILEGES ON solargrid_test_db.* TO 'solargrid'@'localhost';
GRANT ALL PRIVILEGES ON solargrid_test_db.* TO 'solargrid'@'127.0.0.1';
FLUSH PRIVILEGES;
```

---

## 4. Python environment

```powershell
cd C:\solargrid
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Configure environment variables

```powershell
copy .env.example .env
```

Edit `.env` — minimum required settings:

```env
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=pick-any-long-random-string-for-local-dev

DATABASE_URL=mysql+pymysql://solargrid:solargrid_pass@127.0.0.1:3306/solargrid_db
TEST_DATABASE_URL=mysql+pymysql://solargrid:solargrid_pass@127.0.0.1:3306/solargrid_test_db
```

Use your own values if you changed the MySQL user or password in step 3.

---

## 6. Create tables & sample data

The repo already includes migrations — **do not run** `flask db init`.

```powershell
$env:FLASK_APP="run.py"
flask db upgrade
python scripts/seed_database.py
```

`seed_database.py` loads demo customers, equipment, installations, invoices, and staff accounts.

To wipe and re-seed:

```powershell
python scripts/seed_database.py --reset
```

---

## 7. Apply SQL extras (optional but recommended for IT212 demo)

Views, stored procedures, and indexes:

```powershell
mysql -u root -p solargrid_db < database\indexes.sql
mysql -u root -p solargrid_db < database\views.sql
mysql -u root -p solargrid_db < database\procedures.sql
```

**Mac/Linux** — use forward slashes:

```bash
mysql -u root -p solargrid_db < database/indexes.sql
mysql -u root -p solargrid_db < database/views.sql
mysql -u root -p solargrid_db < database/procedures.sql
```

---

## 8. Run the app

```powershell
python run.py
```

Open in your browser:

| URL | Purpose |
|-----|---------|
| http://localhost:5000 | Landing page |
| http://localhost:5000/login | Staff sign-in |
| http://localhost:5000/health | DB connection check (JSON) |

---

## 9. Log in

After seeding, use any of these accounts:

| Username | Role | Password |
|----------|------|----------|
| `admin` | Administrator | `SolarGrid2026!` |
| `salesrep` | Sales Rep | `SolarGrid2026!` |
| `opsmgr` | Operations Manager | `SolarGrid2026!` |
| `finance` | Finance Officer | `SolarGrid2026!` |
| `warehouse` | Warehouse Clerk | `SolarGrid2026!` |
| `customersvc` | Customer Service | `SolarGrid2026!` |
| `techstaff` | Technician | `SolarGrid2026!` |
| `auditor` | Auditor (read-only) | `SolarGrid2026!` |

---

## Troubleshooting

### `Can't connect to MySQL server on 127.0.0.1`

- MySQL service is not running → run `net start MYSQL80` (Windows)
- Wrong host/port in `DATABASE_URL`

### `Access denied for user 'solargrid'`

- Re-run `python scripts/setup_database.py` with the correct root password
- Confirm `.env` `DATABASE_URL` matches the user/password you created

### `ModuleNotFoundError: No module named 'flask'`

- Virtual environment not activated → `.\venv\Scripts\Activate.ps1`
- Then: `pip install -r requirements.txt`

### Login says database may not be set up

- Run `flask db upgrade` then `python scripts/seed_database.py`
- Check http://localhost:5000/health — `staff_count` should be greater than 0

### `Table 'solargrid_db.staff' doesn't exist`

- Migrations not applied → `flask db upgrade`

### Port 5000 already in use

```powershell
$env:PORT="5001"
python run.py
```

Then open http://localhost:5001

---

## Run tests (optional)

```powershell
pytest
```

Requires `solargrid_test_db` to exist (created in step 3) and `TEST_DATABASE_URL` in `.env`.

---

## Daily workflow (after first setup)

```powershell
net start MYSQL80
cd C:\solargrid
.\venv\Scripts\Activate.ps1
python run.py
```

That's it — no need to re-seed unless you want fresh demo data.

---

## Next steps

- [Technical report](technical-report.md) — full IT212 documentation
- [Submission checklist](submission-checklist.md) — demo preparation
- [Backup & recovery](../database/backup-recovery.md) — mysqldump guide
