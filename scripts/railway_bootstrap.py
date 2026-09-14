"""Run on Railway before deploy: migrate DB and create admin if needed."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("FLASK_APP", "run.py")


def _ensure_admin():
    """Create a single admin account when the database is empty."""
    from app.models.staff import Staff
    from app.security.security_utils import hash_password, validate_password_strength

    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password:
        print("No staff users found. Set ADMIN_PASSWORD in Railway Variables to create the first admin.")
        return

    valid, message = validate_password_strength(admin_password)
    if not valid:
        raise ValueError(f"ADMIN_PASSWORD is not strong enough: {message}")

    username = os.environ.get("ADMIN_USERNAME", "admin")
    email = os.environ.get("ADMIN_EMAIL", "admin@solargrid.co.zm")

    if Staff.query.filter_by(username=username).first():
        print(f"Admin user '{username}' already exists.")
        return

    staff = Staff(
        username=username,
        email=email,
        first_name=os.environ.get("ADMIN_FIRST_NAME", "System"),
        last_name=os.environ.get("ADMIN_LAST_NAME", "Administrator"),
        role="Administrator",
        password_hash=hash_password(admin_password),
    )
    from app.extensions import db

    db.session.add(staff)
    db.session.commit()
    print(f"Created production admin user '{username}'.")


def bootstrap():
    from flask_migrate import upgrade

    from app import create_app
    from config import database_connection_label
    from app.models.staff import Staff

    print(f"Connecting to database: {database_connection_label()}")

    try:
        app = create_app("production")
        with app.app_context():
            print("Running database migrations...")
            upgrade()

            staff_count = Staff.query.count()
            if staff_count == 0:
                _ensure_admin()
            else:
                print(f"Database ready ({staff_count} staff users).")
    except Exception:
        print(
            f"Bootstrap failed for database target {database_connection_label()}. "
            "Check Railway MySQL service connectivity and variables."
        )
        raise


if __name__ == "__main__":
    bootstrap()
