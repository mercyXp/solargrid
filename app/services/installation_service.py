from datetime import date
from dateutil.relativedelta import relativedelta

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.equipment import Equipment
from app.models.installation import Installation, InstallationAssignment, InstallationDetail
from app.models.warranty import Warranty
from app.security.permissions import Permission, has_permission
from app.utils.audit import log_audit


class InstallationServiceError(Exception):
    pass


ALLOWED_TRANSITIONS = {
    "Scheduled": {"In Progress", "Cancelled"},
    "In Progress": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}


class InstallationService:
    @staticmethod
    def validate_status_transition(current: str, new: str) -> None:
        if current == "Cancelled":
            raise InstallationServiceError("Cancelled installations cannot be reactivated.")
        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if new not in allowed:
            raise InstallationServiceError(f"Cannot transition from '{current}' to '{new}'.")

    @staticmethod
    def can_start(installation: Installation) -> None:
        if installation.details.count() == 0:
            raise InstallationServiceError("At least one equipment item must be linked.")
        if installation.assignments.count() == 0:
            raise InstallationServiceError("At least one technician must be assigned.")

    @staticmethod
    def add_equipment(installation_id: int, equipment_id: int, unit_price: float) -> InstallationDetail:
        installation = Installation.query.get(installation_id)
        if not installation:
            raise InstallationServiceError("Installation not found.")
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            raise InstallationServiceError("Equipment not found.")
        if equipment.status != "Available":
            raise InstallationServiceError(f"Equipment status '{equipment.status}' is not eligible for installation.")
        if InstallationDetail.query.filter_by(equipment_id=equipment_id).first():
            raise InstallationServiceError("Equipment is already assigned to an installation.")

        detail = InstallationDetail(
            installation_id=installation_id,
            equipment_id=equipment_id,
            unit_price_at_install=unit_price,
        )
        equipment.status = "Reserved"
        db.session.add(detail)
        db.session.commit()
        log_audit("equipment_assigned", "Installation", installation_id, f"Equipment {equipment_id} assigned")
        return detail

    @staticmethod
    def assign_technician(installation_id: int, technician_id: int, role_in_team: str = "Assistant"):
        from app.models.technician import Technician

        installation = Installation.query.get(installation_id)
        if not installation:
            raise InstallationServiceError("Installation not found.")
        technician = Technician.query.get(technician_id)
        if not technician:
            raise InstallationServiceError("Technician not found.")
        if not technician.is_active:
            raise InstallationServiceError("Only active technicians can receive new assignments.")
        if InstallationAssignment.query.filter_by(installation_id=installation_id, technician_id=technician_id).first():
            raise InstallationServiceError("Technician is already assigned to this installation.")

        assignment = InstallationAssignment(
            installation_id=installation_id,
            technician_id=technician_id,
            role_in_team=role_in_team,
        )
        db.session.add(assignment)
        db.session.commit()
        log_audit("technician_assigned", "Installation", installation_id, f"Technician {technician_id} assigned")
        return assignment

    @staticmethod
    def update_status(installation_id: int, new_status: str, current_user) -> Installation:
        installation = (
            db.session.query(Installation)
            .filter_by(installation_id=installation_id)
            .with_for_update()
            .first()
        )
        if not installation:
            raise InstallationServiceError("Installation not found.")

        InstallationService.validate_status_transition(installation.status, new_status)

        if new_status == "In Progress":
            InstallationService.can_start(installation)
            if not installation.actual_start_date:
                installation.actual_start_date = date.today()

        old_status = installation.status
        installation.status = new_status
        db.session.commit()
        log_audit(
            "status_change",
            "Installation",
            installation_id,
            f"{old_status} -> {new_status} by staff {current_user.staff_id}",
        )
        return installation

    @staticmethod
    def complete_installation(installation_id: int, current_user) -> Installation:
        if not has_permission(current_user.role, Permission.COMPLETE_INSTALLATIONS):
            raise InstallationServiceError("Permission denied.")

        try:
            installation = (
                db.session.query(Installation)
                .filter_by(installation_id=installation_id)
                .with_for_update()
                .first()
            )
            if not installation:
                raise InstallationServiceError("Installation not found.")
            if installation.status != "In Progress":
                raise InstallationServiceError("Installation must be In Progress to complete.")

            details = list(installation.details.all())
            assignments = list(installation.assignments.all())
            if not details:
                raise InstallationServiceError("At least one equipment item must be linked.")
            if not assignments:
                raise InstallationServiceError("At least one technician must be assigned.")

            completion_date = date.today()
            for detail in details:
                equipment = detail.equipment
                if equipment.status not in ("Available", "Reserved"):
                    raise InstallationServiceError(
                        f"Equipment {equipment.serial_number} is not eligible (status: {equipment.status})."
                    )
                equipment.status = "Installed"
                equipment.site_id = installation.site_id

                warranty_months = equipment.equipment_type.default_warranty_months
                warranty = Warranty(
                    equipment_id=equipment.equipment_id,
                    start_date=completion_date,
                    end_date=completion_date + relativedelta(months=int(warranty_months)),
                    warranty_type="Manufacturer",
                    status="Active",
                )
                db.session.add(warranty)

            installation.status = "Completed"
            installation.completion_date = completion_date
            db.session.commit()
            log_audit("installation_completed", "Installation", installation_id, "Atomic completion transaction")
            return installation
        except InstallationServiceError:
            db.session.rollback()
            raise
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise InstallationServiceError(f"Transaction failed: {exc}") from exc
