from datetime import date
from decimal import Decimal

import pytest

from app.extensions import db
from app.models.customer import Customer
from app.models.equipment import Equipment, EquipmentType
from app.models.installation import Installation
from app.models.site import Site
from app.models.staff import Staff
from app.models.technician import Technician
from app.services.installation_service import InstallationService, InstallationServiceError


def _setup_installation(app):
    with app.app_context():
        c = Customer(first_name="T", last_name="C", email="tc@test.com", phone="1", address="a", customer_type="Individual")
        db.session.add(c)
        db.session.flush()
        s = Site(customer_id=c.customer_id, site_name="S", address="a", city="c", province="p", site_type="Household")
        db.session.add(s)
        et = EquipmentType(category="Solar Panel", manufacturer="X", model_name="Y", unit_price=Decimal("1000"), default_warranty_months=12)
        db.session.add(et)
        db.session.flush()
        eq = Equipment(equipment_type_id=et.equipment_type_id, serial_number="SN-TEST-001", status="Available", date_received=date.today())
        db.session.add(eq)
        staff = Staff.query.filter_by(username="testadmin").first()
        inst = Installation(site_id=s.site_id, planned_date=date.today(), created_by=staff.staff_id)
        db.session.add(inst)
        db.session.commit()
        return inst, eq, staff


def test_unavailable_equipment_rejected(app):
    inst, eq, staff = _setup_installation(app)
    with app.app_context():
        eq.status = "Installed"
        db.session.commit()
        with pytest.raises(InstallationServiceError):
            InstallationService.add_equipment(inst.installation_id, eq.equipment_id, 1000.0)


def test_cancelled_cannot_reactivate(app):
    inst, _, staff = _setup_installation(app)
    with app.app_context():
        inst = Installation.query.get(inst.installation_id)
        inst.status = "Cancelled"
        db.session.commit()
        with pytest.raises(InstallationServiceError):
            InstallationService.update_status(inst.installation_id, "Scheduled", staff)
