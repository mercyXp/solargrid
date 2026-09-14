# SolarGrid — API Readiness

The primary interface is server-rendered HTML. Business logic lives in the service layer for future REST extraction.

## Planned API Structure (Future)

| Resource | Service Layer |
|----------|---------------|
| POST /api/installations/{id}/complete | `InstallationService.complete_installation` |
| POST /api/payments | `PaymentService.confirm_payment` |
| POST /api/service-requests/{id}/assign | `ServiceRequestService.assign_technician` |
| GET /api/reports/revenue | `ReportingService.revenue_report` |

## Current Web Routes

All routes require authentication except `/login`. See route blueprints in `app/routes/`.

## Response Conventions (Future API)

- JSON responses with `{ "data": ..., "error": null }`
- HTTP 403 for authorization failures
- HTTP 409 for business rule violations
- HTTP 422 for validation errors
