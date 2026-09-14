-- SolarGrid sample data reference
-- Prefer: python scripts/seed_database.py (handles bcrypt hashing)
-- Use this file for MySQL Workbench reference after schema is created.

USE solargrid_db;

-- After running seed_database.py, verify with:
-- SELECT role, username FROM staff;
-- SELECT COUNT(*) FROM customer;
-- SELECT COUNT(*) FROM equipment;
-- SELECT COUNT(*) FROM installation;
