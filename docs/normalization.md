# SolarGrid — Normalization Evidence (1NF → 3NF)

## 1NF (First Normal Form)

All attributes are **atomic** (no repeating groups):

- Customer address is one field per site (sites are separate rows, not repeated columns).
- Equipment items are individual rows, not embedded lists on Installation.
- Technician assignments use bridge tables (`installation_assignment`, `service_assignment`).

## 2NF (Second Normal Form)

All non-key attributes depend on the **whole primary key**:

- `installation_detail`: composite uniqueness on `(installation_id, equipment_id)`; `unit_price_at_install` depends on the full install-equipment link.
- Bridge tables remove partial dependencies on multi-column keys.

**Removed dependency example:** Storing technician name on `installation_assignment` would depend only on `technician_id` → moved to `technician` table.

## 3NF (Third Normal Form)

No transitive dependencies (non-key → non-key):

- Customer name/email live on `customer`, not duplicated on `site` or `invoice`.
- Equipment type catalogue (`equipment_type`) separated from serial-tracked `equipment` units.
- Staff login credentials on `staff`; field operative profiles on `technician` (separate entities per business rule).

**Removed dependency example:** Storing `manufacturer` on `equipment` would transitively depend on `equipment_type_id` → manufacturer stays on `equipment_type`.

## Controlled denormalization

| Field | Reason |
|-------|--------|
| `Invoice.amount_paid` | Updated atomically with payments for fast balance queries; source of truth remains `payment` rows |

## Functional dependencies (examples)

- `customer_id` → `{first_name, last_name, email, ...}`
- `equipment_type_id` → `{category, manufacturer, unit_price, default_warranty_months}`
- `installation_id` → `{site_id, status, planned_date, ...}`

See ERD: `docs/erd.md`, relational schema: `docs/database-design.md`.
