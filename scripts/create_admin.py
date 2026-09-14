"""Create an administrator account."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db
from app.models.staff import Staff
from app.security.security_utils import hash_password, validate_password_strength


def create_admin(username, email, password, first_name="System", last_name="Administrator"):
    valid, msg = validate_password_strength(password)
    if not valid:
        raise ValueError(msg)
    app = create_app()
    with app.app_context():
        if Staff.query.filter_by(username=username).first():
            print(f"User {username} already exists.")
            return
        staff = Staff(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role="Administrator",
            password_hash=hash_password(password),
        )
        db.session.add(staff)
        db.session.commit()
        print(f"Administrator '{username}' created.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="admin")
    parser.add_argument("--email", default="admin@solargrid.co.za")
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    create_admin(args.username, args.email, args.password)
