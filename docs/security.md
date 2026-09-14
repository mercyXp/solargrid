# SolarGrid — Security

## Authentication

- Session-based login with server-side Flask sessions
- Passwords hashed with bcrypt (cost factor 12+)
- Minimum 8 characters, letter + number required
- Inactive accounts cannot login
- Login rate limited (5 per minute)
- Session timeout via `PERMANENT_SESSION_LIFETIME`

## Authorization

- RBAC via `Permission` enum and `ROLE_PERMISSIONS` map
- `@permission_required` on every protected route
- `@write_required` blocks Auditor POST/PUT/DELETE
- UI hides unauthorized menu items; server always re-validates

## CSRF

- Flask-WTF CSRF on all WTForms
- Manual forms include `csrf_token()`

## SQL Injection

- SQLAlchemy parameterized queries exclusively
- No string-concatenated SQL

## XSS

- Jinja2 auto-escaping for user content
- No `|safe` on user-generated data

## Session Security

- HttpOnly cookies
- SameSite=Lax
- Secure cookies in production

## Security Headers

- Content-Security-Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- Referrer-Policy
- Strict-Transport-Security (production)

## Audit Logging

- Login, logout, failed login
- CRUD on customers, equipment, installations, invoices, payments
- Status changes and assignments
- Passwords never logged

## Secrets

- `.env` for SECRET_KEY, DATABASE_URL
- `.env.example` provided; `.env` gitignored

## Error Handling

- Custom error pages; no stack traces to users in production
- DB errors trigger rollback
