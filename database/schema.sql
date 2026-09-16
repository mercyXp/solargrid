-- SolarGrid Energy Solutions — Full DDL (MySQL 8.x)
-- IT212 Group 1: tables, PKs, FKs, CHECK and UNIQUE constraints
--
-- Alternative: flask db upgrade (Alembic migration is authoritative twin)
--   migrations/versions/b000f2425625_initial_schema.py

CREATE DATABASE IF NOT EXISTS solargrid_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS solargrid_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE solargrid_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS service_assignment;
DROP TABLE IF EXISTS maintenance_record;
DROP TABLE IF EXISTS invoice;
DROP TABLE IF EXISTS warranty;
DROP TABLE IF EXISTS service_request;
DROP TABLE IF EXISTS installation_detail;
DROP TABLE IF EXISTS installation_assignment;
DROP TABLE IF EXISTS installation;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS site;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS technician;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS equipment_type;
DROP TABLE IF EXISTS customer;

SET FOREIGN_KEY_CHECKS = 1;

-- ── Master entities ──

CREATE TABLE customer (
    customer_id     INT AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    company_name    VARCHAR(100) NULL,
    email           VARCHAR(100) NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    address         VARCHAR(255) NOT NULL,
    customer_type   ENUM('Individual','Business','Government','NGO') NOT NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_customer_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE equipment_type (
    equipment_type_id       INT AUTO_INCREMENT PRIMARY KEY,
    category                ENUM('Solar Panel','Battery','Inverter','Charge Controller','Mounting','Accessory') NOT NULL,
    manufacturer            VARCHAR(100) NOT NULL,
    model_name              VARCHAR(100) NOT NULL,
    rating                  VARCHAR(50)  NULL COMMENT 'Power/capacity e.g. 400W, 5 kW, 13.5 kWh',
    model_number            VARCHAR(50)  NULL,
    specifications          TEXT         NULL,
    unit_price              DECIMAL(12,2) NOT NULL,
    default_warranty_months INT          NOT NULL,
    is_active               TINYINT(1)   NOT NULL DEFAULT 1,
    CONSTRAINT uk_equipment_type_model_number UNIQUE (model_number),
    CONSTRAINT chk_equipment_type_warranty_months CHECK (default_warranty_months > 0),
    CONSTRAINT chk_equipment_type_unit_price CHECK (unit_price > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE staff (
    staff_id        INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    email           VARCHAR(100) NOT NULL,
    role            ENUM('Administrator','Sales Rep','Operations Manager','Technician','Warehouse Clerk','Customer Service','Finance Officer','Auditor') NOT NULL,
    is_active       TINYINT(1)   NOT NULL DEFAULT 1,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_staff_username UNIQUE (username),
    CONSTRAINT uk_staff_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE technician (
    technician_id   INT AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    email           VARCHAR(100) NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    specialisation  VARCHAR(100) NULL,
    hire_date       DATE         NOT NULL,
    is_active       TINYINT(1)   NOT NULL DEFAULT 1,
    CONSTRAINT uk_technician_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE audit_log (
    audit_id        INT AUTO_INCREMENT PRIMARY KEY,
    staff_id        INT          NULL,
    action          VARCHAR(50)  NOT NULL,
    entity_type     VARCHAR(50)  NOT NULL,
    entity_id       INT          NULL,
    details         TEXT         NULL,
    ip_address      VARCHAR(45)  NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_staff_id FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Customer sites & equipment ──

CREATE TABLE site (
    site_id         INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT          NOT NULL,
    site_name       VARCHAR(100) NOT NULL,
    address         VARCHAR(255) NOT NULL,
    city            VARCHAR(50)  NOT NULL,
    province        VARCHAR(50)  NOT NULL,
    postal_code     VARCHAR(10)  NULL,
    latitude        DECIMAL(10,7) NULL,
    longitude       DECIMAL(10,7) NULL,
    site_type       ENUM('Household','School','Farm','Business','Government') NOT NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_site_customer_id FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE equipment (
    equipment_id        INT AUTO_INCREMENT PRIMARY KEY,
    equipment_type_id   INT          NOT NULL,
    serial_number       VARCHAR(50)  NOT NULL,
    site_id             INT          NULL,
    status              ENUM('Available','Reserved','Installed','Faulty','Decommissioned') NOT NULL DEFAULT 'Available',
    date_received       DATE         NOT NULL,
    notes               TEXT         NULL,
    CONSTRAINT uk_equipment_serial_number UNIQUE (serial_number),
    CONSTRAINT fk_equipment_equipment_type_id FOREIGN KEY (equipment_type_id) REFERENCES equipment_type(equipment_type_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_equipment_site_id FOREIGN KEY (site_id) REFERENCES site(site_id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Installations ──

CREATE TABLE installation (
    installation_id     INT AUTO_INCREMENT PRIMARY KEY,
    site_id             INT          NOT NULL,
    planned_date        DATE         NOT NULL,
    actual_start_date   DATE         NULL,
    completion_date     DATE         NULL,
    status              ENUM('Scheduled','In Progress','Completed','Cancelled') NOT NULL DEFAULT 'Scheduled',
    notes               TEXT         NULL,
    created_by          INT          NOT NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_installation_site_id FOREIGN KEY (site_id) REFERENCES site(site_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_installation_created_by FOREIGN KEY (created_by) REFERENCES staff(staff_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE installation_assignment (
    install_assign_id   INT AUTO_INCREMENT PRIMARY KEY,
    installation_id     INT          NOT NULL,
    technician_id       INT          NOT NULL,
    assigned_date       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role_in_team        ENUM('Lead','Assistant') NOT NULL DEFAULT 'Lead',
    CONSTRAINT uk_installation_assignment UNIQUE (installation_id, technician_id),
    CONSTRAINT fk_installation_assignment_installation_id FOREIGN KEY (installation_id) REFERENCES installation(installation_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_installation_assignment_technician_id FOREIGN KEY (technician_id) REFERENCES technician(technician_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE installation_detail (
    install_detail_id       INT AUTO_INCREMENT PRIMARY KEY,
    installation_id         INT          NOT NULL,
    equipment_id            INT          NOT NULL,
    quantity                INT          NOT NULL DEFAULT 1,
    unit_price_at_install   DECIMAL(12,2) NOT NULL,
    CONSTRAINT uk_installation_detail_equipment_id UNIQUE (equipment_id),
    CONSTRAINT uk_installation_detail_install_equip UNIQUE (installation_id, equipment_id),
    CONSTRAINT chk_installation_detail_quantity CHECK (quantity >= 1),
    CONSTRAINT chk_installation_detail_price CHECK (unit_price_at_install > 0),
    CONSTRAINT fk_installation_detail_installation_id FOREIGN KEY (installation_id) REFERENCES installation(installation_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_installation_detail_equipment_id FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Service & maintenance ──

CREATE TABLE service_request (
    request_id      INT AUTO_INCREMENT PRIMARY KEY,
    site_id         INT          NOT NULL,
    equipment_id    INT          NULL,
    reported_by     INT          NOT NULL,
    date_raised     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description     TEXT         NOT NULL,
    priority        ENUM('Low','Medium','High','Critical') NOT NULL DEFAULT 'Medium',
    status          ENUM('Open','In Progress','Resolved','Closed') NOT NULL DEFAULT 'Open',
    date_resolved   DATETIME     NULL,
    CONSTRAINT fk_service_request_site_id FOREIGN KEY (site_id) REFERENCES site(site_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_service_request_equipment_id FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_service_request_reported_by FOREIGN KEY (reported_by) REFERENCES staff(staff_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE service_assignment (
    service_assign_id   INT AUTO_INCREMENT PRIMARY KEY,
    request_id          INT          NOT NULL,
    technician_id       INT          NOT NULL,
    assigned_date       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_service_assignment UNIQUE (request_id, technician_id),
    CONSTRAINT fk_service_assignment_request_id FOREIGN KEY (request_id) REFERENCES service_request(request_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_service_assignment_technician_id FOREIGN KEY (technician_id) REFERENCES technician(technician_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE maintenance_record (
    maintenance_id      INT AUTO_INCREMENT PRIMARY KEY,
    request_id          INT          NOT NULL,
    technician_id       INT          NOT NULL,
    maintenance_date    DATETIME     NOT NULL,
    work_description    TEXT         NOT NULL,
    hours_worked        DECIMAL(5,2) NOT NULL,
    parts_used          TEXT         NULL,
    resolution_notes    TEXT         NULL,
    CONSTRAINT chk_maintenance_hours_worked CHECK (hours_worked > 0),
    CONSTRAINT fk_maintenance_request_id FOREIGN KEY (request_id) REFERENCES service_request(request_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_maintenance_technician_id FOREIGN KEY (technician_id) REFERENCES technician(technician_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Warranties & finance ──

CREATE TABLE warranty (
    warranty_id     INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id    INT          NOT NULL,
    start_date      DATE         NOT NULL,
    end_date        DATE         NOT NULL,
    warranty_type   ENUM('Manufacturer','Extended','SolarGrid') NOT NULL DEFAULT 'Manufacturer',
    terms           TEXT         NULL,
    status          ENUM('Active','Expired','Claimed','Voided') NOT NULL DEFAULT 'Active',
    CONSTRAINT chk_warranty_dates CHECK (end_date > start_date),
    CONSTRAINT fk_warranty_equipment_id FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE invoice (
    invoice_id      INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number  VARCHAR(20)  NOT NULL,
    customer_id     INT          NOT NULL,
    installation_id INT          NULL,
    request_id      INT          NULL,
    date_issued     DATE         NOT NULL,
    due_date        DATE         NOT NULL,
    total_amount    DECIMAL(12,2) NOT NULL,
    amount_paid     DECIMAL(12,2) NOT NULL DEFAULT 0,
    status          ENUM('Draft','Issued','Partially Paid','Paid','Overdue','Cancelled') NOT NULL DEFAULT 'Draft',
    created_by      INT          NOT NULL,
    CONSTRAINT uk_invoice_number UNIQUE (invoice_number),
    CONSTRAINT chk_invoice_amount_paid CHECK (amount_paid >= 0),
    CONSTRAINT chk_invoice_due_date CHECK (due_date >= date_issued),
    CONSTRAINT chk_invoice_total_amount CHECK (total_amount > 0),
    CONSTRAINT fk_invoice_customer_id FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_invoice_installation_id FOREIGN KEY (installation_id) REFERENCES installation(installation_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_invoice_request_id FOREIGN KEY (request_id) REFERENCES service_request(request_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_invoice_created_by FOREIGN KEY (created_by) REFERENCES staff(staff_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE payment (
    payment_id          INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id          INT          NOT NULL,
    payment_date        DATETIME     NOT NULL,
    amount              DECIMAL(12,2) NOT NULL,
    payment_method      ENUM('Cash','EFT','Credit Card','Debit Order','Cheque') NOT NULL,
    reference_number    VARCHAR(50)  NULL,
    status              ENUM('Pending','Confirmed','Reversed') NOT NULL DEFAULT 'Pending',
    recorded_by         INT          NOT NULL,
    CONSTRAINT chk_payment_amount CHECK (amount > 0),
    CONSTRAINT fk_payment_invoice_id FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_payment_recorded_by FOREIGN KEY (recorded_by) REFERENCES staff(staff_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- After schema, apply:
--   SOURCE database/indexes.sql;
--   SOURCE database/views.sql;
--   SOURCE database/procedures.sql;
--   SOURCE database/users.sql;
--   python scripts/seed_database.py
