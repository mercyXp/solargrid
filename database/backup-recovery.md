# SolarGrid — Backup & Recovery

## Backup strategy

SolarGrid uses **MySQL logical backups** (mysqldump) for the `solargrid_db` database.

### Create a backup

```powershell
mysqldump -u root -p --single-transaction --routines --triggers --databases solargrid_db > backup/solargrid_db_YYYYMMDD.sql
```

Include views and procedures:

```powershell
mysqldump -u root -p --single-transaction --routines --triggers solargrid_db > backup/solargrid_full_YYYYMMDD.sql
```

### Restore from backup

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS solargrid_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p solargrid_db < backup/solargrid_db_YYYYMMDD.sql
```

Then verify:

```sql
USE solargrid_db;
SHOW TABLES;
SELECT COUNT(*) FROM customer;
SELECT COUNT(*) FROM staff;
```

## What could be lost

| Strategy | RPO (data loss window) | Notes |
|----------|------------------------|-------|
| Daily mysqldump | Up to 24 hours | Transactions after last backup are lost |
| Hourly dump (production) | Up to 1 hour | Recommended for live deployments |
| `--single-transaction` (InnoDB) | Point-in-time of dump start | Consistent snapshot, no table locks |

**Not included in a standard mysqldump:** MySQL server configuration, OS-level files, application `.env` secrets (store separately in Railway Variables / secure vault).

## Railway production

Use Railway MySQL **Backups** in the dashboard or schedule:

```bash
railway run mysqldump ...   # when CLI connected to MySQL service
```

Document the restore procedure in your live demo: restore → `flask db upgrade` (if needed) → verify `/health`.

## Application-level audit

`audit_log` table records staff actions but is **not** a substitute for full database backup — restore requires mysqldump or provider snapshot.
