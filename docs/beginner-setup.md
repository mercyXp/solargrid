# SolarGrid — Complete Beginner Setup Guide

**For:** Teammates with little or no programming experience  
**Goal:** Run SolarGrid on your Windows laptop from zero  
**Time:** About 45–90 minutes the first time  
**Repo:** https://github.com/mercyXp/solargrid

Read each section in order. Do not skip steps.

---

## Before you start — what you are installing

| Tool | What it is (simple) |
|------|---------------------|
| **Git** | Downloads the project code from GitHub |
| **Python** | Runs the web application |
| **MySQL** | Stores all data (customers, equipment, invoices, etc.) |
| **VS Code** (recommended) | Edits files and opens the built-in terminal |

The app is **not** a normal `.exe` file. You start it from a **terminal** (a text window where you type commands).

---

## Part 1 — Install Git

1. Open: https://git-scm.com/download/win  
2. Download and run the installer.  
3. Click **Next** on every screen (defaults are fine).  
4. When finished, open **PowerShell**:
   - Press the **Windows key**
   - Type `PowerShell`
   - Click **Windows PowerShell**

5. Check Git works:

```powershell
git --version
```

You should see something like `git version 2.x.x`.  
If you see *“not recognized”*, close PowerShell, reopen it, and try again.

---

## Part 2 — Install Python

1. Open: https://www.python.org/downloads/  
2. Click **Download Python 3.11** or **3.12** (3.11+ is required).  
3. Run the installer.  
4. **IMPORTANT:** On the first screen, tick ✅ **“Add python.exe to PATH”**  
5. Click **Install Now** and wait until it finishes.

6. Close and reopen PowerShell, then check:

```powershell
python --version
```

You should see `Python 3.11.x` or newer.

If `python` does not work, try:

```powershell
py --version
```

For the rest of this guide, if `python` fails, use `py` instead (e.g. `py -m venv venv`).

---

## Part 3 — Install MySQL

1. Open: https://dev.mysql.com/downloads/installer/  
2. Download **MySQL Installer for Windows** (the larger “Full” or “Web” installer).  
3. Run the installer. Choose **Custom** or **Developer Default**.  
4. Make sure these are selected:
   - **MySQL Server 8.x**
   - **MySQL Workbench** (optional but helpful for IT212 demo)
5. When asked for a **root password**, choose one and **write it down**.  
   Example: `MyRootPass2026!`  
   You will need this password several times below.
6. Finish the installer. MySQL usually runs as a Windows service named **MYSQL80**.

### Check MySQL is running

Open **PowerShell as Administrator**:

- Press Windows key → type `PowerShell`
- Right-click **Windows PowerShell** → **Run as administrator**

```powershell
net start MYSQL80
```

If it says *“service is already started”*, that is fine.

---

## Part 4 — Choose a folder for the project

Pick a simple location, for example:

```
C:\Projects
```

Create it if it does not exist:

```powershell
mkdir C:\Projects
cd C:\Projects
```

---

## Part 5 — Clone the GitHub repository

**Clone** means “download a copy of the project from GitHub.”

In PowerShell (normal window is OK now):

```powershell
cd C:\Projects
git clone https://github.com/mercyXp/solargrid.git
cd solargrid
```

You should now have a folder: `C:\Projects\solargrid`

### If Git asks for login

- Use your **GitHub username** and a **Personal Access Token** (not your GitHub password).  
- Create a token: GitHub → Settings → Developer settings → Personal access tokens.

### Alternative: GitHub Desktop (no commands)

1. Install https://desktop.github.com/  
2. Sign in to GitHub  
3. File → Clone repository → URL: `https://github.com/mercyXp/solargrid.git`  
4. Choose `C:\Projects\solargrid`  
5. Use GitHub Desktop’s **Open in terminal** or open PowerShell and `cd` to that folder

---

## Part 6 — Create a Python virtual environment

A **virtual environment** keeps this project’s Python packages separate from the rest of your computer.

In PowerShell, inside the project folder:

```powershell
cd C:\Projects\solargrid
python -m venv venv
```

Wait until it finishes (no errors).

### Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

When it works, your prompt shows `(venv)` at the start:

```
(venv) PS C:\Projects\solargrid>
```

**You must activate `venv` every time** you open a new terminal to work on this project.

### If you get “running scripts is disabled”

Run this **once** in PowerShell (normal user is OK):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Type `Y` and press Enter. Then try `Activate.ps1` again.

---

## Part 7 — Install Python packages

With `(venv)` active:

```powershell
pip install -r requirements.txt
```

This takes a few minutes. Wait until it completes without red **ERROR** lines.

If `pip` is slow or fails, try:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Part 8 — Create the configuration file (`.env`)

The app reads secret settings from a file named `.env`.

```powershell
copy .env.example .env
```

### Edit `.env` (choose one method)

**Method A — Notepad**

```powershell
notepad .env
```

**Method B — VS Code**

```powershell
code .env
```

Make sure these lines exist (defaults from `.env.example` are usually fine):

```env
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=my-local-dev-secret-key-change-this

DATABASE_URL=mysql+pymysql://solargrid:solargrid_pass@127.0.0.1:3306/solargrid_db
TEST_DATABASE_URL=mysql+pymysql://solargrid:solargrid_pass@127.0.0.1:3306/solargrid_test_db
```

Save and close the file.

---

## Part 9 — Create the MySQL databases

MySQL must be running (Part 3). With `(venv)` active:

```powershell
$env:MYSQL_ROOT_PASSWORD="YOUR-MYSQL-ROOT-PASSWORD-HERE"
python scripts/setup_database.py
```

Replace `YOUR-MYSQL-ROOT-PASSWORD-HERE` with the root password you set when installing MySQL.

**Success looks like:**

```
Database setup complete.
Verified: application user can connect to solargrid_db.
```

This creates:

- Database `solargrid_db` (main app data)
- Database `solargrid_test_db` (for tests)
- User `solargrid` / password `solargrid_pass`

---

## Part 10 — Create tables in the database

Still with `(venv)` active:

```powershell
$env:FLASK_APP="run.py"
flask db upgrade
```

**Success:** No red errors; you may see “Running upgrade …”.

**Do not run** `flask db init` — the project already has migrations.

---

## Part 11 — Load sample data (demo users & customers)

```powershell
python scripts/seed_database.py
```

**Success:**

```
Database seeded successfully with Zambian sample data.
Development credentials (all roles):
  Password: SolarGrid2026!
  admin (Administrator)
  ...
```

If it says *“already has data — skipping”*, run:

```powershell
python scripts/seed_database.py --reset
```

---

## Part 12 — Run the application

```powershell
python run.py
```

**Success looks like:**

```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

**Leave this window open** while using the app. Closing it stops the server.

---

## Part 13 — Open the app in your browser

Open **Chrome** or **Edge** and go to:

| Address | What you see |
|---------|----------------|
| http://localhost:5000 | Landing page |
| http://localhost:5000/login | Staff login |
| http://localhost:5000/health | JSON status (proves DB works) |

### Log in

| Field | Value |
|-------|--------|
| Username | `admin` |
| Password | `SolarGrid2026!` |

After login you should see the **Dashboard**.

---

## Part 14 — Optional: SQL extras (for IT212 demo)

Only needed if your role covers views/procedures (Gilbert, Yves, or demo prep).

Add MySQL to your PATH, or use the full path to `mysql.exe` (often `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe`).

```powershell
mysql -u root -p solargrid_db < database\indexes.sql
mysql -u root -p solargrid_db < database\views.sql
mysql -u root -p solargrid_db < database\procedures.sql
```

Enter your **MySQL root password** when prompted.

---

## Every day after the first setup

You only repeat these steps:

1. **Start MySQL** (Admin PowerShell):

```powershell
net start MYSQL80
```

2. **Open project terminal:**

```powershell
cd C:\Projects\solargrid
.\venv\Scripts\Activate.ps1
python run.py
```

3. Open http://localhost:5000 in your browser.

You do **not** need to re-clone, re-install pip packages, or re-seed every day.

---

## Troubleshooting (common beginner problems)

### “python is not recognized”

- Reinstall Python and tick **Add to PATH**, or use `py` instead of `python`.

### “Can't connect to MySQL server”

- MySQL is not running → Admin PowerShell: `net start MYSQL80`
- Wrong password in `.env` → check `DATABASE_URL`

### “Access denied for user 'solargrid'”

- Re-run Part 9 with the correct root password.

### “ModuleNotFoundError: No module named 'flask'”

- You forgot to activate venv → `.\venv\Scripts\Activate.ps1`
- Then: `pip install -r requirements.txt`

### “running scripts is disabled”

- See Part 6 — `Set-ExecutionPolicy RemoteSigned`

### Login page says database not set up

```powershell
$env:FLASK_APP="run.py"
flask db upgrade
python scripts/seed_database.py --reset
```

### Port 5000 already in use

```powershell
$env:PORT="5001"
python run.py
```

Then open http://localhost:5001

### Browser shows “This site can’t be reached”

- Is `python run.py` still running in the terminal?
- Did you use `http://localhost:5000` (not https)?

### `git clone` fails — repository not found

- Check internet connection
- Confirm URL: `https://github.com/mercyXp/solargrid.git`
- Ask team lead if repo is private (you need GitHub access)

---

## Quick checklist (print this)

```
[ ] Git installed          git --version
[ ] Python 3.11+ installed python --version
[ ] MySQL 8 installed      net start MYSQL80
[ ] Repo cloned            cd C:\Projects\solargrid
[ ] venv created           python -m venv venv
[ ] venv activated         (venv) in prompt
[ ] Packages installed     pip install -r requirements.txt
[ ] .env file created      copy .env.example .env
[ ] Database setup         python scripts/setup_database.py
[ ] Tables created         flask db upgrade
[ ] Sample data loaded     python scripts/seed_database.py
[ ] App running            python run.py
[ ] Login works            admin / SolarGrid2026!
```

---

## Get help from your team

| Problem type | Ask |
|--------------|-----|
| App won’t start, code errors | **Mercy** or **Elijah** |
| Database / SQL / MySQL | **Gilbert** or **Yves** |
| Page looks wrong | **Jemimah** |
| Which step to run / demo | **Linah** |

---

## Shorter guide (after you’ve done this once)

See [quick-start.md](quick-start.md) for a condensed version.
