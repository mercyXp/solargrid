-- SolarGrid Energy Solutions — Demonstration SQL Queries
-- IT212: DDL/DML, SELECT, filtering, sorting, aggregates, JOINs, subqueries

USE solargrid_db;

-- ── Filtering & sorting ──
SELECT customer_id, first_name, last_name, customer_type, email
FROM customer
WHERE customer_type = 'Business'
ORDER BY last_name, first_name;

-- ── Aggregate + GROUP BY ──
SELECT status, COUNT(*) AS equipment_count
FROM equipment
GROUP BY status
ORDER BY equipment_count DESC;

-- ── INNER JOIN: installations with customer and site ──
SELECT
    i.installation_id,
    i.status,
    i.planned_date,
    s.site_name,
    c.first_name,
    c.last_name
FROM installation i
INNER JOIN site s ON s.site_id = i.site_id
INNER JOIN customer c ON c.customer_id = s.customer_id
ORDER BY i.planned_date DESC;

-- ── LEFT JOIN: all technicians and their installation assignments ──
SELECT
    t.technician_id,
    CONCAT(t.first_name, ' ', t.last_name) AS technician_name,
    ia.installation_id,
    ia.role_in_team
FROM technician t
LEFT JOIN installation_assignment ia ON ia.technician_id = t.technician_id
ORDER BY technician_name;

-- ── Subquery: customers with more than one site ──
SELECT c.customer_id, c.first_name, c.last_name, c.email
FROM customer c
WHERE c.customer_id IN (
    SELECT s.customer_id
    FROM site s
    GROUP BY s.customer_id
    HAVING COUNT(*) > 1
);

-- ── Subquery: equipment never installed (correlated-style via NOT IN) ──
SELECT e.serial_number, et.category, e.status
FROM equipment e
INNER JOIN equipment_type et ON et.equipment_type_id = e.equipment_type_id
WHERE e.equipment_id NOT IN (
    SELECT id.equipment_id FROM installation_detail id
);

-- ── Report queries (also available as views/procedures) ──
SELECT * FROM vw_outstanding_invoices ORDER BY balance_due DESC;
SELECT * FROM vw_expiring_warranties ORDER BY end_date;
SELECT * FROM vw_technician_workload ORDER BY active_installations DESC;

CALL sp_outstanding_balances_by_customer();
CALL sp_revenue_by_month(2026);
CALL sp_unresolved_service_requests();
