-- Report query references (implemented in ReportingService)

-- Report 1: Warranty Expiry
-- SELECT w.*, e.serial_number FROM warranty w JOIN equipment e ON w.equipment_id = e.equipment_id
-- WHERE w.end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) AND w.status = 'Active';

-- Report 2: Unresolved Service Requests
-- SELECT * FROM service_request WHERE status IN ('Open','In Progress') ORDER BY FIELD(priority,'Critical','High','Medium','Low'), date_raised;

-- Report 3: Technician Workload — see ReportingService.technician_workload()

-- Report 4: Outstanding Balances
-- SELECT * FROM invoice WHERE status IN ('Issued','Partially Paid','Overdue') AND amount_paid < total_amount;

-- Report 5: Revenue by period — see ReportingService.revenue_report()
