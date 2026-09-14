-- SolarGrid Energy Solutions — Schema (MySQL 8.x)
-- Corresponds to SQLAlchemy models; use Flask-Migrate for application deployments.

CREATE DATABASE IF NOT EXISTS solargrid_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE solargrid_db;

-- Tables created via Flask-Migrate/Alembic in application.
-- Run: flask db upgrade
-- Or import constraints.sql and indexes.sql after migration.
