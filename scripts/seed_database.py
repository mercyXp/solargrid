"""Seed SolarGrid database with realistic Zambian sample data."""
import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db
from app.models.customer import Customer
from app.models.equipment import Equipment, EquipmentType
from app.models.installation import Installation, InstallationAssignment, InstallationDetail
from app.models.invoice import Invoice
from app.models.maintenance import MaintenanceRecord
from app.models.payment import Payment
from app.models.service_request import ServiceAssignment, ServiceRequest
from app.models.site import Site
from app.models.staff import Staff
from app.models.technician import Technician
from app.models.warranty import Warranty
from app.security.security_utils import hash_password


def seed(reset=False):
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        if reset:
            db.drop_all()
            db.create_all()
        elif Staff.query.count() > 0:
            print("Database already has data — skipping seed (use reset=True to wipe).")
            return

        staff_users = [
            ("admin", "Administrator", "Admin", "Mwanza", "admin@solargrid.co.zm"),
            ("salesrep", "Sales Rep", "Chanda", "Bwalya", "sales@solargrid.co.zm"),
            ("opsmgr", "Operations Manager", "Mutale", "Zulu", "ops@solargrid.co.zm"),
            ("techstaff", "Technician", "Emmanuel", "Phiri", "tech@solargrid.co.zm"),
            ("warehouse", "Warehouse Clerk", "Linda", "Nyirenda", "warehouse@solargrid.co.zm"),
            ("customersvc", "Customer Service", "Nomsa", "Sakala", "service@solargrid.co.zm"),
            ("finance", "Finance Officer", "Peter", "Tembo", "finance@solargrid.co.zm"),
            ("auditor", "Auditor", "Grace", "Lungu", "audit@solargrid.co.zm"),
        ]
        staff_map = {}
        for username, role, fn, ln, email in staff_users:
            s = Staff(
                username=username,
                password_hash=hash_password("SolarGrid2026!"),
                first_name=fn,
                last_name=ln,
                email=email,
                role=role,
            )
            db.session.add(s)
            staff_map[username] = s
        db.session.flush()

        customers_data = [
            ("Joseph", "Banda", None, "joseph.banda@email.co.zm", "0977123456", "Plot 234, Kabulonga, Lusaka", "Individual"),
            ("Mwamba", "Farms", "Mwamba Farms Ltd", "info@mwambafarms.co.zm", "0966789012", "Farm Block 12, Chisamba", "Business"),
            ("Eastern", "Province School", "Eastern Province Education Board", "admin@epeducation.gov.zm", "0976543210", "Chipata Central, Eastern Province", "Government"),
        ]
        customers = []
        for fn, ln, co, em, ph, ad, ct in customers_data:
            c = Customer(first_name=fn, last_name=ln, company_name=co, email=em, phone=ph, address=ad, customer_type=ct)
            db.session.add(c)
            customers.append(c)
        db.session.flush()

        sites = []
        site_data = [
            (customers[0], "Kabulonga Home", "Plot 234, Kabulonga", "Lusaka", "Lusaka", "10101", "Household"),
            (customers[1], "Chisamba Main Farm", "Farm Block 12", "Chisamba", "Central", "10102", "Farm"),
            (customers[2], "Chipata School Campus", "School Road, Chipata", "Chipata", "Eastern", "10103", "School"),
        ]
        for cust, name, addr, city, prov, pc, st in site_data:
            s = Site(customer_id=cust.customer_id, site_name=name, address=addr, city=city, province=prov, postal_code=pc, site_type=st)
            db.session.add(s)
            sites.append(s)
        db.session.flush()

        types = []
        type_data = [
            ("Solar Panel", "SunPower", "Maxeon 3 400W", "SP-400", Decimal("4500.00"), 120),
            ("Inverter", "SMA", "Sunny Boy 5.0", "SB-5.0", Decimal("18500.00"), 60),
            ("Battery", "Tesla", "Powerwall 2", "PW2", Decimal("95000.00"), 120),
        ]
        for cat, mfr, model, mn, price, months in type_data:
            et = EquipmentType(category=cat, manufacturer=mfr, model_name=model, model_number=mn, unit_price=price, default_warranty_months=months)
            db.session.add(et)
            types.append(et)
        db.session.flush()

        equipment_items = []
        for i in range(1, 16):
            et = types[i % 3]
            eq = Equipment(
                equipment_type_id=et.equipment_type_id,
                serial_number=f"SG-ZM-2026-{i:04d}",
                status="Available" if i > 5 else ("Installed" if i <= 2 else "Reserved"),
                site_id=sites[0].site_id if i <= 2 else None,
                date_received=date.today() - timedelta(days=30 + i),
            )
            db.session.add(eq)
            equipment_items.append(eq)
        db.session.flush()

        technicians = []
        for fn, ln, em, spec in [
            ("Patrick", "Mbewe", "patrick.m@solargrid.co.zm", "Solar Panels"),
            ("Beatrice", "Mukuka", "beatrice.m@solargrid.co.zm", "Inverter Systems"),
            ("John", "Chilufya", "john.c@solargrid.co.zm", "Battery Storage"),
        ]:
            t = Technician(first_name=fn, last_name=ln, email=em, phone="0977000001", specialisation=spec, hire_date=date(2024, 1, 15))
            db.session.add(t)
            technicians.append(t)
        db.session.flush()

        inst1 = Installation(
            site_id=sites[0].site_id,
            planned_date=date.today() + timedelta(days=7),
            status="Scheduled",
            created_by=staff_map["opsmgr"].staff_id,
        )
        inst2 = Installation(
            site_id=sites[1].site_id,
            planned_date=date.today() - timedelta(days=14),
            actual_start_date=date.today() - timedelta(days=10),
            status="In Progress",
            created_by=staff_map["opsmgr"].staff_id,
        )
        inst3 = Installation(
            site_id=sites[0].site_id,
            planned_date=date.today() - timedelta(days=60),
            actual_start_date=date.today() - timedelta(days=58),
            completion_date=date.today() - timedelta(days=55),
            status="Completed",
            created_by=staff_map["opsmgr"].staff_id,
        )
        db.session.add_all([inst1, inst2, inst3])
        db.session.flush()

        db.session.add(InstallationDetail(installation_id=inst2.installation_id, equipment_id=equipment_items[2].equipment_id, unit_price_at_install=types[0].unit_price))
        db.session.add(InstallationDetail(installation_id=inst3.installation_id, equipment_id=equipment_items[0].equipment_id, unit_price_at_install=types[0].unit_price))
        db.session.add(InstallationAssignment(installation_id=inst2.installation_id, technician_id=technicians[0].technician_id, role_in_team="Lead"))
        db.session.add(InstallationAssignment(installation_id=inst3.installation_id, technician_id=technicians[0].technician_id, role_in_team="Lead"))
        equipment_items[2].status = "Reserved"

        sr1 = ServiceRequest(site_id=sites[0].site_id, equipment_id=equipment_items[0].equipment_id, reported_by=staff_map["customersvc"].staff_id, description="Inverter showing error code E04", priority="High", status="Open")
        sr2 = ServiceRequest(site_id=sites[1].site_id, reported_by=staff_map["customersvc"].staff_id, description="Annual maintenance check", priority="Low", status="In Progress")
        db.session.add_all([sr1, sr2])
        db.session.flush()
        db.session.add(ServiceAssignment(request_id=sr2.request_id, technician_id=technicians[1].technician_id))
        db.session.add(MaintenanceRecord(request_id=sr2.request_id, technician_id=technicians[1].technician_id, maintenance_date=datetime.utcnow() - timedelta(days=1), work_description="Inspected all connections", hours_worked=Decimal("2.5")))

        w = Warranty(equipment_id=equipment_items[0].equipment_id, start_date=date.today() - timedelta(days=55), end_date=date.today() + timedelta(days=3650), warranty_type="Manufacturer", status="Active")
        db.session.add(w)

        inv1 = Invoice(invoice_number="INV-2026-0001", customer_id=customers[0].customer_id, installation_id=inst3.installation_id, date_issued=date.today() - timedelta(days=50), due_date=date.today() - timedelta(days=20), total_amount=Decimal("45000.00"), amount_paid=Decimal("30000.00"), status="Partially Paid", created_by=staff_map["finance"].staff_id)
        inv2 = Invoice(invoice_number="INV-2026-0002", customer_id=customers[1].customer_id, date_issued=date.today() - timedelta(days=10), due_date=date.today() + timedelta(days=20), total_amount=Decimal("125000.00"), amount_paid=Decimal("0"), status="Issued", created_by=staff_map["finance"].staff_id)
        db.session.add_all([inv1, inv2])
        db.session.flush()
        db.session.add(Payment(invoice_id=inv1.invoice_id, payment_date=datetime.utcnow() - timedelta(days=30), amount=Decimal("30000.00"), payment_method="EFT", reference_number="ZANACO-001", status="Confirmed", recorded_by=staff_map["finance"].staff_id))

        db.session.commit()
        print("Database seeded successfully with Zambian sample data.")
        print("\nDevelopment credentials (all roles):")
        print("  Password: SolarGrid2026!")
        for username, role, *_ in staff_users:
            print(f"  {username} ({role})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before seeding")
    args = parser.parse_args()
    seed(reset=args.reset)
