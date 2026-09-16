-- SolarGrid Energy Solutions — Stored Procedures (MySQL 8.x)
-- Demonstrates multi-step business logic at the database layer.
-- Application equivalent: app/services/installation_service.py, payment_service.py

USE solargrid_db;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_outstanding_balances_by_customer$$
CREATE PROCEDURE sp_outstanding_balances_by_customer()
BEGIN
    /*
     * Report: customers with unpaid invoice balances.
     * Uses INNER JOIN + aggregate (GROUP BY).
     */
    SELECT
        c.customer_id,
        CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        c.company_name,
        COUNT(i.invoice_id) AS open_invoice_count,
        SUM(i.total_amount - i.amount_paid) AS total_outstanding
    FROM customer c
    INNER JOIN invoice i ON i.customer_id = c.customer_id
    WHERE i.status IN ('Issued', 'Partially Paid', 'Overdue')
      AND (i.total_amount - i.amount_paid) > 0
    GROUP BY c.customer_id, c.first_name, c.last_name, c.company_name
    ORDER BY total_outstanding DESC;
END$$

DROP PROCEDURE IF EXISTS sp_revenue_by_month$$
CREATE PROCEDURE sp_revenue_by_month(IN p_year INT)
BEGIN
    /*
     * Report: revenue by month for a calendar year.
     * Uses confirmed payments joined to invoices.
     */
    SELECT
        MONTH(p.payment_date) AS month_num,
        DATE_FORMAT(p.payment_date, '%M') AS month_name,
        SUM(p.amount) AS revenue_zmw,
        COUNT(p.payment_id) AS payment_count
    FROM payment p
    INNER JOIN invoice i ON i.invoice_id = p.invoice_id
    WHERE p.status = 'Confirmed'
      AND YEAR(p.payment_date) = p_year
    GROUP BY MONTH(p.payment_date), DATE_FORMAT(p.payment_date, '%M')
    ORDER BY month_num;
END$$

DROP PROCEDURE IF EXISTS sp_unresolved_service_requests$$
CREATE PROCEDURE sp_unresolved_service_requests()
BEGIN
    /*
     * Report: open/in-progress service requests with site and reporter.
     * Uses LEFT JOIN for optional equipment link.
     */
    SELECT
        sr.request_id,
        sr.priority,
        sr.status,
        sr.date_raised,
        s.site_name,
        CONCAT(st.first_name, ' ', st.last_name) AS reported_by_name,
        e.serial_number AS equipment_serial
    FROM service_request sr
    INNER JOIN site s ON s.site_id = sr.site_id
    INNER JOIN staff st ON st.staff_id = sr.reported_by
    LEFT JOIN equipment e ON e.equipment_id = sr.equipment_id
    WHERE sr.status IN ('Open', 'In Progress')
    ORDER BY
        FIELD(sr.priority, 'Critical', 'High', 'Medium', 'Low'),
        sr.date_raised;
END$$

DROP PROCEDURE IF EXISTS sp_demo_transaction_rollback$$
CREATE PROCEDURE sp_demo_transaction_rollback(
    IN p_installation_id INT,
    OUT p_result VARCHAR(255)
)
BEGIN
    /*
     * ACID demonstration: attempts to complete installation when equipment
     * is not in Reserved/Available state — entire transaction rolls back.
     * For live demo of ROLLBACK behaviour (does not replace app transaction).
     */
    DECLARE v_invalid_count INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result = 'ROLLBACK: transaction failed — no partial updates committed';
    END;

    START TRANSACTION;

    SELECT COUNT(*) INTO v_invalid_count
    FROM installation_detail id
    INNER JOIN equipment e ON e.equipment_id = id.equipment_id
    WHERE id.installation_id = p_installation_id
      AND e.status NOT IN ('Available', 'Reserved');

    IF v_invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Equipment not eligible for completion';
    END IF;

    UPDATE installation
    SET status = 'Completed', completion_date = CURDATE()
    WHERE installation_id = p_installation_id
      AND status = 'In Progress';

    UPDATE equipment e
    INNER JOIN installation_detail id ON id.equipment_id = e.equipment_id
    SET e.status = 'Installed',
        e.site_id = (SELECT site_id FROM installation WHERE installation_id = p_installation_id)
    WHERE id.installation_id = p_installation_id;

    COMMIT;
    SET p_result = 'COMMIT: installation completed successfully';
END$$

DELIMITER ;
