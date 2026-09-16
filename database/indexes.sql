-- SolarGrid Energy Solutions — Performance Indexes (MySQL 8.x)
-- Apply after tables exist (flask db upgrade or schema import).

USE solargrid_db;

-- Frequently filtered/joined columns for reports and list views
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_site_id ON equipment(site_id);
CREATE INDEX IF NOT EXISTS idx_installation_status ON installation(status);
CREATE INDEX IF NOT EXISTS idx_installation_planned_date ON installation(planned_date);
CREATE INDEX IF NOT EXISTS idx_service_request_status_priority ON service_request(status, priority, date_raised);
CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoice(status);
CREATE INDEX IF NOT EXISTS idx_invoice_due_date ON invoice(due_date);
CREATE INDEX IF NOT EXISTS idx_warranty_end_date ON warranty(end_date);
CREATE INDEX IF NOT EXISTS idx_warranty_status ON warranty(status);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_equipment_type_rating ON equipment_type(rating);
CREATE INDEX IF NOT EXISTS idx_customer_type ON customer(customer_type);
CREATE INDEX IF NOT EXISTS idx_site_customer_id ON site(customer_id);

-- Index rationale (IT212):
-- idx_equipment_status      → equipment list filter by Available/Installed
-- idx_installation_status   → dashboard KPIs and installation reports
-- idx_service_request_*     → unresolved service request report
-- idx_invoice_*             → outstanding balances and overdue alerts
-- idx_warranty_end_date     → warranty expiry report (Report 1)
-- idx_audit_created_at      → audit log chronological search
