-- SolarGrid Energy Solutions — Database Views (MySQL 8.x)
-- Run after schema/migrations: mysql -u solargrid -p solargrid_db < database/views.sql

USE solargrid_db;

DROP VIEW IF EXISTS vw_outstanding_invoices;
DROP VIEW IF EXISTS vw_expiring_warranties;
DROP VIEW IF EXISTS vw_technician_workload;

-- View 1: Outstanding customer balances (supports Report 4)
CREATE VIEW vw_outstanding_invoices AS
SELECT
    i.invoice_id,
    i.invoice_number,
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.company_name,
    i.date_issued,
    i.due_date,
    i.total_amount,
    i.amount_paid,
    (i.total_amount - i.amount_paid) AS balance_due,
    i.status
FROM invoice i
INNER JOIN customer c ON c.customer_id = i.customer_id
WHERE i.status IN ('Issued', 'Partially Paid', 'Overdue')
  AND (i.total_amount - i.amount_paid) > 0;

-- View 2: Warranties approaching expiry (supports Report 1)
CREATE VIEW vw_expiring_warranties AS
SELECT
    w.warranty_id,
    e.serial_number,
    et.category,
    et.manufacturer,
    et.model_name,
    s.site_name,
    w.start_date,
    w.end_date,
    w.status,
    DATEDIFF(w.end_date, CURDATE()) AS days_until_expiry
FROM warranty w
INNER JOIN equipment e ON e.equipment_id = w.equipment_id
INNER JOIN equipment_type et ON et.equipment_type_id = e.equipment_type_id
LEFT JOIN site s ON s.site_id = e.site_id
WHERE w.status = 'Active'
  AND w.end_date <= DATE_ADD(CURDATE(), INTERVAL 90 DAY);

-- View 3 (bonus): Technician workload summary (supports Report 3)
CREATE VIEW vw_technician_workload AS
SELECT
    t.technician_id,
    CONCAT(t.first_name, ' ', t.last_name) AS technician_name,
    t.specialisation,
    (
        SELECT COUNT(*)
        FROM installation_assignment ia
        INNER JOIN installation inst ON inst.installation_id = ia.installation_id
        WHERE ia.technician_id = t.technician_id
          AND inst.status IN ('Scheduled', 'In Progress')
    ) AS active_installations,
    (
        SELECT COUNT(*)
        FROM service_assignment sa
        INNER JOIN service_request sr ON sr.request_id = sa.request_id
        WHERE sa.technician_id = t.technician_id
          AND sr.status IN ('Open', 'In Progress')
    ) AS open_service_requests
FROM technician t
WHERE t.is_active = 1;
