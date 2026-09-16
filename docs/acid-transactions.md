# SolarGrid — Transactions & ACID

## Required business transaction: Complete Installation

**Flow:** Complete installation → Record installed equipment → Update equipment availability → Create warranties

**Implementation:** `app/services/installation_service.py` → `complete_installation()`

```text
BEGIN (implicit SQLAlchemy session)
  SELECT installation FOR UPDATE
  FOR EACH equipment in installation_detail:
    validate status IN (Available, Reserved)
    UPDATE equipment SET status='Installed', site_id=...
    INSERT warranty
  UPDATE installation SET status='Completed', completion_date=...
COMMIT — or ROLLBACK on any error
```

### ACID properties

| Property | How SolarGrid demonstrates it |
|----------|-------------------------------|
| **Atomicity** | All equipment updates, warranty inserts, and installation status change commit together or roll back |
| **Consistency** | CHECK constraints, FK rules, and service validation prevent invalid states (e.g. duplicate equipment on installs) |
| **Isolation** | `with_for_update()` row lock on installation during completion |
| **Durability** | InnoDB commits persist to disk after successful commit |

### Demo: failure → rollback

1. Open an **In Progress** installation with linked equipment.
2. Manually set one linked equipment row to `Faulty` in MySQL Workbench.
3. Attempt **Complete** in the app → error message; installation remains **In Progress**, equipment unchanged, no new warranty.
4. Optional SQL demo: `CALL sp_demo_transaction_rollback(installation_id, @result);`

## Second transaction: Confirm Payment

**Implementation:** `app/services/payment_service.py` → `confirm_payment()`

- Locks invoice row (`FOR UPDATE`)
- Inserts payment
- Updates `amount_paid` and invoice status atomically
- Rolls back if amount exceeds balance or invoice is cancelled

## SQL-layer demonstration

See `database/procedures.sql` → `sp_demo_transaction_rollback` for stored-procedure rollback demo.
