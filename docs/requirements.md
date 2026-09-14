# SolarGrid Energy Solutions — Requirements (Stage 1)

## Business Scenario

SolarGrid Energy Solutions installs and maintains solar power systems for households, schools, farms, and businesses in Zambia (ZMK). The system tracks customers, sites, equipment inventory, installations, warranties, technicians, service requests, maintenance, invoices, and payments.

## Actors / Roles

| Role | Primary Responsibility |
|------|------------------------|
| Administrator | Full system administration |
| Sales Rep | Customer and site acquisition |
| Operations Manager | Installations and service delivery |
| Technician (Staff role) | Field work via assigned jobs |
| Warehouse Clerk | Equipment inventory |
| Customer Service | Service request logging |
| Finance Officer | Invoicing and payments |
| Auditor | Read-only compliance review |

**Note:** Staff (authenticated users) is distinct from Technician (field operative profiles).

## Functional Requirements (FR-01 to FR-20)

| ID | Summary | Actor | Priority |
|----|---------|-------|----------|
| FR-01 | Register customers with type | Sales Rep / Admin | P0 |
| FR-02 | Register sites per customer | Sales Rep / Admin | P0 |
| FR-03 | Maintain equipment type catalogue | Warehouse Clerk / Admin | P0 |
| FR-04 | Register individual equipment items | Warehouse Clerk | P0 |
| FR-05 | Schedule installations | Operations Manager | P0 |
| FR-06 | Link equipment to installations | Operations Manager / Warehouse Clerk | P0 |
| FR-07 | Assign technicians to installations | Operations Manager | P0 |
| FR-08 | Atomically complete installations | Operations Manager | P0 |
| FR-09 | Prevent duplicate equipment assignments | System | P0 |
| FR-10 | Track warranty coverage per equipment | Admin / Warehouse Clerk | P0 |
| FR-11 | Log service requests | Customer Service | P0 |
| FR-12 | Assign technicians to service requests | Operations Manager | P0 |
| FR-13 | Record maintenance visits | Technician | P0 |
| FR-14 | Update service request status | Operations Manager / Technician | P0 |
| FR-15 | Searchable maintenance history | Customer Service / Auditor | P1 |
| FR-16 | Raise invoices | Finance Officer | P0 |
| FR-17 | Record payments | Finance Officer | P0 |
| FR-18 | Auto-update invoice amount_paid/status | System | P0 |
| FR-19 | Five management reports | Finance / Ops / Auditor | P1 |
| FR-20 | Atomic multi-table transactions | System | P0 |

## Non-Functional Requirements

- **Performance:** Indexed lookups < 500ms; reports < 5s
- **Security:** bcrypt passwords, RBAC on every write
- **Integrity:** FK constraints, CHECK constraints, UNIQUE on candidate keys
- **Auditability:** Financial and status changes traceable to Staff
- **Concurrency:** SELECT FOR UPDATE on critical transactions

## Database Rules (DB-01 to DB-15)

See `database-design.md` and `traceability-matrix.md`.

## Application Rules (APP-01 to APP-10)

See `architecture.md` service layer documentation.

## Assumptions

- MySQL 8.x target RDBMS
- Single-tenant deployment
- Zambian geography and ZMK (Zambian Kwacha) currency
- Staff and Technician remain separate entities
