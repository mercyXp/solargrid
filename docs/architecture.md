# SolarGrid — Architecture

## Overview

Modular Flask monolith using application factory pattern, server-rendered Jinja2 UI, and a service layer designed for future REST API extraction.

## Layers

```
Routes (Blueprints) → Forms/Validation → Services → SQLAlchemy Models → MySQL
                              ↓
                         Audit / Security
```

## Application Factory

`create_app()` in `app/__init__.py` configures extensions, blueprints, error handlers, security headers, and session user loading.

## Modules

| Module | Blueprint | Service |
|--------|-----------|---------|
| Auth | auth | security_utils |
| Dashboard | dashboard | reporting_service |
| Customers | customers | — |
| Sites | sites | — |
| Equipment | equipment | — |
| Installations | installations | installation_service |
| Technicians | technicians | — |
| Service Requests | services | service_request_service |
| Maintenance | maintenance | — |
| Warranties | warranties | warranty_service |
| Invoices | invoices | invoice_service |
| Payments | payments | payment_service |
| Reports | reports | reporting_service |
| Staff | staff | security_utils |
| Audit | audit | audit utils |

## Authorization

Centralized in `app/security/permissions.py`. Routes use `@permission_required(Permission.X)` and `@write_required` (blocks Auditor writes).

## Transaction Boundaries

### Complete Installation (FR-08, FR-20)

Single transaction in `InstallationService.complete_installation()`:
1. Lock installation row (FOR UPDATE)
2. Validate status, equipment, technicians
3. Update installation → Completed
4. Update equipment → Installed + site_id
5. Create warranty records
6. Commit or full rollback

### Confirm Payment (FR-18, APP-10)

Single transaction in `PaymentService.confirm_payment()`:
1. Lock invoice row
2. Validate status and amount
3. Insert payment
4. Update amount_paid and status
5. Commit or rollback

## Controlled Denormalization

`Invoice.amount_paid` is maintained transactionally by PaymentService (documented deliberate denormalization for report performance).

## Scalability Strategy

- Indexed FK and status columns
- Server-side pagination (25/50/100)
- Service layer reusable by future API blueprints
- No premature microservices

## Configuration

Environment-based via `.env`: `SECRET_KEY`, `DATABASE_URL`, session timeout, bcrypt rounds.

## Security Headers

CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, HSTS (production).
