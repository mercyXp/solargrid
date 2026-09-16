-- SolarGrid Energy Solutions — Database Users & Privileges (MySQL 8.x)
-- Principle of least privilege: separate app, read-only, and admin roles.
-- Run as MySQL root: mysql -u root -p < database/users.sql

-- Application user (used by Flask app — see .env.example)
CREATE USER IF NOT EXISTS 'solargrid'@'localhost' IDENTIFIED BY 'solargrid_pass';
CREATE USER IF NOT EXISTS 'solargrid'@'127.0.0.1' IDENTIFIED BY 'solargrid_pass';

GRANT SELECT, INSERT, UPDATE, DELETE ON solargrid_db.* TO 'solargrid'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON solargrid_db.* TO 'solargrid'@'127.0.0.1';

-- Read-only auditor role (reports and SELECT only)
CREATE USER IF NOT EXISTS 'solargrid_auditor'@'localhost' IDENTIFIED BY 'ChangeMe_Auditor_2026!';
CREATE USER IF NOT EXISTS 'solargrid_auditor'@'127.0.0.1' IDENTIFIED BY 'ChangeMe_Auditor_2026!';

GRANT SELECT ON solargrid_db.* TO 'solargrid_auditor'@'localhost';
GRANT SELECT ON solargrid_db.* TO 'solargrid_auditor'@'127.0.0.1';

-- DBA / migration user (schema changes — not used by running app)
CREATE USER IF NOT EXISTS 'solargrid_admin'@'localhost' IDENTIFIED BY 'ChangeMe_Admin_2026!';
GRANT ALL PRIVILEGES ON solargrid_db.* TO 'solargrid_admin'@'localhost';

FLUSH PRIVILEGES;

-- Verify (run manually):
-- SHOW GRANTS FOR 'solargrid'@'localhost';
-- SHOW GRANTS FOR 'solargrid_auditor'@'localhost';
