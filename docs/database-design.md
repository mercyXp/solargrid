# SolarGrid — Database Design

## Database

- **Name:** `solargrid_db`
- **Engine:** MySQL 8.x
- **ORM:** SQLAlchemy with Flask-Migrate/Alembic

## Entities (15)

| # | Entity | PK | Type |
|---|--------|-----|------|
| 1 | Staff | staff_id | Master |
| 2 | Customer | customer_id | Master |
| 3 | Site | site_id | Master |
| 4 | EquipmentType | equipment_type_id | Master |
| 5 | Equipment | equipment_id | Operational (pivot) |
| 6 | Installation | installation_id | Operational |
| 7 | InstallationDetail | install_detail_id | Bridge M:N |
| 8 | Technician | technician_id | Master |
| 9 | InstallationAssignment | install_assign_id | Bridge M:N |
| 10 | ServiceRequest | request_id | Operational |
| 11 | ServiceAssignment | service_assign_id | Bridge M:N |
| 12 | MaintenanceRecord | maintenance_id | Operational |
| 13 | Warranty | warranty_id | Operational |
| 14 | Invoice | invoice_id | Financial |
| 15 | Payment | payment_id | Financial |

Additional: **AuditLog** (application audit trail, not in Stage 2 ERD).

## Key Relationships

- Customer 1:N Site, Invoice
- Site 1:N Installation, ServiceRequest; 1:N Equipment (nullable FK)
- EquipmentType 1:N Equipment
- Installation M:N Equipment via InstallationDetail (UNIQUE equipment_id)
- Installation M:N Technician via InstallationAssignment (UNIQUE installation_id+technician_id)
- ServiceRequest M:N Technician via ServiceAssignment
- Equipment 1:N Warranty, ServiceRequest
- Invoice 1:N Payment; optional FK to Installation, ServiceRequest
- Staff audit FKs: Installation.created_by, ServiceRequest.reported_by, Invoice.created_by, Payment.recorded_by

## Normalization

Schema at 3NF/BCNF. Deliberate controlled denormalization: `Invoice.amount_paid` maintained transactionally.

## Constraint Naming

- `pk_tablename`
- `fk_tablename_column`
- `uk_tablename_column`
- `chk_tablename_column`

## Indexes

See `database/indexes.sql` — FK columns, email, serial_number, invoice_number, status fields, date filters.

## DDL Dependency Order

Staff → Customer → Site → EquipmentType → Equipment → Technician → Installation → InstallationDetail → InstallationAssignment → ServiceRequest → ServiceAssignment → MaintenanceRecord → Warranty → Invoice → Payment → AuditLog
