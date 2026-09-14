"""Create SolarGrid MySQL databases and application user.

Usage (PowerShell):
    $env:MYSQL_ROOT_PASSWORD="your-root-password"
    python scripts/setup_database.py

Or:
    python scripts/setup_database.py --root-password "your-root-password"
"""
import argparse
import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pymysql

APP_USER = os.environ.get("MYSQL_APP_USER", "solargrid")
APP_PASSWORD = os.environ.get("MYSQL_APP_PASSWORD", "solargrid_pass")
DATABASES = ("solargrid_db", "solargrid_test_db")


def setup(root_password: str, host: str = "127.0.0.1", port: int = 3306):
    conn = pymysql.connect(
        host=host,
        user="root",
        password=root_password,
        port=port,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE USER IF NOT EXISTS '{APP_USER}'@'localhost' IDENTIFIED BY %s",
                (APP_PASSWORD,),
            )
            cur.execute(
                f"CREATE USER IF NOT EXISTS '{APP_USER}'@'127.0.0.1' IDENTIFIED BY %s",
                (APP_PASSWORD,),
            )
            for db in DATABASES:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                cur.execute(f"GRANT ALL PRIVILEGES ON `{db}`.* TO '{APP_USER}'@'localhost'")
                cur.execute(f"GRANT ALL PRIVILEGES ON `{db}`.* TO '{APP_USER}'@'127.0.0.1'")
            cur.execute("FLUSH PRIVILEGES")
    finally:
        conn.close()

    encoded = quote_plus(APP_PASSWORD)
    db_url = f"mysql+pymysql://{APP_USER}:{encoded}@{host}:{port}/solargrid_db"
    test_url = f"mysql+pymysql://{APP_USER}:{encoded}@{host}:{port}/solargrid_test_db"

    print("Database setup complete.")
    print("\nAdd these lines to your .env file:")
    print(f"DATABASE_URL={db_url}")
    print(f"TEST_DATABASE_URL={test_url}")
    print(f"\nApp user: {APP_USER}")
    print(f"App password: {APP_PASSWORD}")
    print("\nNext steps:")
    print("  flask db migrate -m \"Initial schema\"")
    print("  flask db upgrade")
    print("  python scripts/seed_database.py")


def verify_app_connection(host: str = "127.0.0.1", port: int = 3306):
    conn = pymysql.connect(
        host=host,
        user=APP_USER,
        password=APP_PASSWORD,
        port=port,
        database="solargrid_db",
    )
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
    conn.close()
    print("Verified: application user can connect to solargrid_db.")


def main():
    parser = argparse.ArgumentParser(description="Create SolarGrid MySQL databases")
    parser.add_argument("--root-password", default=os.environ.get("MYSQL_ROOT_PASSWORD", ""))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    if args.verify_only:
        verify_app_connection(args.host, args.port)
        return

    if not args.root_password:
        print("Error: MySQL root password required.")
        print("Set MYSQL_ROOT_PASSWORD or pass --root-password")
        sys.exit(1)

    try:
        setup(args.root_password, args.host, args.port)
        verify_app_connection(args.host, args.port)
    except pymysql.err.OperationalError as exc:
        print(f"Connection failed: {exc}")
        print("\nCheck that:")
        print("  - MySQL80 service is running")
        print("  - Root password is correct (same as MySQL Workbench)")
        sys.exit(1)


if __name__ == "__main__":
    main()
