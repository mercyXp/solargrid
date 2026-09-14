# SolarGrid — Entity Relationship Diagram

Canonical Mermaid ERD from IT212 Stage 2 reference document.

```mermaid
erDiagram
    Staff {
        int staff_id PK
        varchar username UK
        varchar password_hash
        varchar first_name
        varchar last_name
        varchar email UK
        enum role
        boolean is_active
        datetime created_at
    }
    Customer {
        int customer_id PK
        varchar first_name
        varchar last_name
        varchar company_name
        varchar email UK
        varchar phone
        varchar address
        enum customer_type
        datetime created_at
        datetime updated_at
    }
    Site {
        int site_id PK
        int customer_id FK
        varchar site_name
        varchar address
        varchar city
        varchar province
        varchar postal_code
        decimal latitude
        decimal longitude
        enum site_type
        datetime created_at
    }
    EquipmentType {
        int equipment_type_id PK
        enum category
        varchar manufacturer
        varchar model_name
        varchar model_number UK
        text specifications
        decimal unit_price
        int default_warranty_months
        boolean is_active
    }
    Equipment {
        int equipment_id PK
        int equipment_type_id FK
        varchar serial_number UK
        int site_id FK
        enum status
        date date_received
        text notes
    }
    Installation {
        int installation_id PK
        int site_id FK
        date planned_date
        date actual_start_date
        date completion_date
        enum status
        text notes
        int created_by FK
        datetime created_at
    }
    InstallationDetail {
        int install_detail_id PK
        int installation_id FK
        int equipment_id FK UK
        int quantity
        decimal unit_price_at_install
    }
    Technician {
        int technician_id PK
        varchar first_name
        varchar last_name
        varchar email UK
        varchar phone
        varchar specialisation
        date hire_date
        boolean is_active
    }
    InstallationAssignment {
        int install_assign_id PK
        int installation_id FK
        int technician_id FK
        datetime assigned_date
        enum role_in_team
    }
    ServiceRequest {
        int request_id PK
        int site_id FK
        int equipment_id FK
        int reported_by FK
        datetime date_raised
        text description
        enum priority
        enum status
        datetime date_resolved
    }
    ServiceAssignment {
        int service_assign_id PK
        int request_id FK
        int technician_id FK
        datetime assigned_date
    }
    MaintenanceRecord {
        int maintenance_id PK
        int request_id FK
        int technician_id FK
        datetime maintenance_date
        text work_description
        decimal hours_worked
        text parts_used
        text resolution_notes
    }
    Warranty {
        int warranty_id PK
        int equipment_id FK
        date start_date
        date end_date
        enum warranty_type
        text terms
        enum status
    }
    Invoice {
        int invoice_id PK
        varchar invoice_number UK
        int customer_id FK
        int installation_id FK
        int request_id FK
        date date_issued
        date due_date
        decimal total_amount
        decimal amount_paid
        enum status
        int created_by FK
    }
    Payment {
        int payment_id PK
        int invoice_id FK
        datetime payment_date
        decimal amount
        enum payment_method
        varchar reference_number
        enum status
        int recorded_by FK
    }
    Customer ||--o{ Site : owns
    Customer ||--o{ Invoice : receives
    Site ||--o{ Installation : has
    Site ||--o{ ServiceRequest : generates
    Site ||--o{ Equipment : holds
    EquipmentType ||--|{ Equipment : classifies
    Installation ||--o{ InstallationDetail : contains
    Equipment ||--o{ InstallationDetail : included-in
    Installation ||--o{ InstallationAssignment : assigns
    Technician ||--o{ InstallationAssignment : assigned-to
    ServiceRequest ||--o{ ServiceAssignment : assigned-via
    Technician ||--o{ ServiceAssignment : handles
    ServiceRequest ||--o{ MaintenanceRecord : records
    Technician ||--o{ MaintenanceRecord : performs
    Equipment ||--o{ Warranty : covered-by
    Equipment ||--o{ ServiceRequest : subject-of
    Invoice ||--o{ Payment : settled-by
    Installation ||--o{ Invoice : billed-via
    ServiceRequest ||--o{ Invoice : billed-via
    Staff ||--o{ Installation : created-by
    Staff ||--o{ ServiceRequest : reported-by
    Staff ||--o{ Invoice : created-by
    Staff ||--o{ Payment : recorded-by
```

## Design Notes

- **Staff vs Technician:** Intentionally separate; a person may exist in both tables.
- **InstallationDetail UNIQUE on equipment_id:** Enforces DB-05 (one equipment, one installation).
- **Bridge entities** carry relationship attributes (price snapshot, role_in_team, assigned_date).
