-- SolarGrid — Master database install script (MySQL Workbench / CLI)
-- Order: schema → indexes → views → procedures → users
--
-- Prerequisites: MySQL 8.x, root access
--
-- Option A (recommended with Flask app):
--   python scripts/setup_database.py
--   flask db upgrade
--   python scripts/seed_database.py
--   mysql -u root -p solargrid_db < database/indexes.sql
--   mysql -u root -p solargrid_db < database/views.sql
--   mysql -u root -p solargrid_db < database/procedures.sql
--
-- Option B (SQL-only layers after flask db upgrade):
--   SOURCE database/indexes.sql;
--   SOURCE database/views.sql;
--   SOURCE database/procedures.sql;
--   SOURCE database/users.sql;

SOURCE indexes.sql;
SOURCE views.sql;
SOURCE procedures.sql;
