"""Run on Railway: migrate DB and seed sample data if empty."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("FLASK_APP", "run.py")


def bootstrap():
    from flask_migrate import upgrade

    from app import create_app
    from app.models.staff import Staff

    app = create_app("production")
    with app.app_context():
        print("Running database migrations...")
        upgrade()
        if Staff.query.count() == 0:
            print("No staff found — seeding database...")
            from scripts.seed_database import seed

            seed(reset=False)
        else:
            print(f"Database ready ({Staff.query.count()} staff users).")


if __name__ == "__main__":
    bootstrap()
