# Requirements Traceability Matrix

## Functional Requirements

| Req | Module | Route | Service | Model | Test |
|-----|--------|-------|---------|-------|------|
| FR-01 | customers | customers.create | — | Customer | test_customers |
| FR-02 | sites | sites.create | — | Site | test_sites |
| FR-03 | equipment | equipment.type_create | — | EquipmentType | test_equipment |
| FR-04 | equipment | equipment.create | — | Equipment | test_equipment |
| FR-05 | installations | installations.create | — | Installation | test_installations |
| FR-06 | installations | installations.assign_equipment | InstallationService.add_equipment | InstallationDetail | test_installations |
| FR-07 | installations | installations.assign_technician | InstallationService.assign_technician | InstallationAssignment | test_installations |
| FR-08 | installations | installations.complete | InstallationService.complete_installation | Installation, Equipment, Warranty | test_installations |
| FR-09 | installations | installations.assign_equipment | InstallationService | InstallationDetail (UK) | test_installations |
| FR-10 | warranties | warranties.index | WarrantyService | Warranty | test_warranties |
| FR-11 | services | services.create | — | ServiceRequest | test_service_requests |
| FR-12 | services | services.assign | ServiceRequestService | ServiceAssignment | test_service_requests |
| FR-13 | maintenance | maintenance.create | — | MaintenanceRecord | test_service_requests |
| FR-14 | services | services.update_status | ServiceRequestService | ServiceRequest | test_service_requests |
| FR-15 | maintenance | maintenance.index | — | MaintenanceRecord | test_service_requests |
| FR-16 | invoices | invoices.create | InvoiceService | Invoice | test_invoices |
| FR-17 | payments | payments.create | PaymentService | Payment | test_payments |
| FR-18 | payments | payments.create | PaymentService.recalculate_invoice_status | Invoice | test_payments |
| FR-19 | reports | reports.* | ReportingService | All | test_reports |
| FR-20 | installations | installations.complete | InstallationService (atomic) | Multi-table | test_installations |

## Database Rules

| Rule | Implementation | Test |
|------|----------------|------|
| DB-01 | uk_customer_email | test_customers |
| DB-02 | chk_equipment_type_unit_price | test_equipment |
| DB-03 | chk_equipment_type_warranty_months | test_equipment |
| DB-04 | uk_equipment_serial_number | test_equipment |
| DB-05 | uk_installation_detail_equipment_id | test_installations |
| DB-06 | uk_installation_assignment | test_installations |
| DB-07 | uk_service_assignment | test_service_requests |
| DB-08 | chk_warranty_dates | test_warranties |
| DB-09 | chk_invoice_total_amount | test_invoices |
| DB-10 | chk_invoice_amount_paid | test_invoices |
| DB-11 | chk_invoice_due_date | test_invoices |
| DB-12 | chk_payment_amount | test_payments |
| DB-13 | chk_maintenance_hours_worked | test_service_requests |
| DB-14 | ON DELETE RESTRICT Site/Equipment | test_customers |
| DB-15 | ON DELETE RESTRICT Staff FKs | test_staff |

## Application Rules

| Rule | Service | Test |
|------|---------|------|
| APP-01 | InstallationService.add_equipment | test_installations |
| APP-02 | InstallationService.update_status | test_installations |
| APP-03 | ServiceRequestService.update_status | test_service_requests |
| APP-04 | InvoiceService.validate_installation_amount | test_invoices |
| APP-05 | PaymentService.confirm_payment | test_payments |
| APP-06 | Installation/Service assignment services | test_installations |
| APP-07 | InstallationService.validate_status_transition | test_installations |
| APP-08 | PaymentService.confirm_payment | test_payments |
| APP-09 | security_utils hash/validate | test_auth |
| APP-10 | PaymentService.recalculate_invoice_status | test_payments |
