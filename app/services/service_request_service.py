from datetime import datetime

from app.extensions import db
from app.models.maintenance import MaintenanceRecord
from app.models.service_request import ServiceAssignment, ServiceRequest
from app.models.technician import Technician
from app.utils.audit import log_audit


class ServiceRequestServiceError(Exception):
    pass


SERVICE_TRANSITIONS = {
    "Open": {"In Progress", "Closed"},
    "In Progress": {"Resolved", "Closed"},
    "Resolved": {"Closed"},
    "Closed": set(),
}


class ServiceRequestService:
    @staticmethod
    def assign_technician(request_id: int, technician_id: int) -> ServiceAssignment:
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise ServiceRequestServiceError("Service request not found.")
        technician = Technician.query.get(technician_id)
        if not technician:
            raise ServiceRequestServiceError("Technician not found.")
        if not technician.is_active:
            raise ServiceRequestServiceError("Only active technicians can receive new assignments.")
        if ServiceAssignment.query.filter_by(request_id=request_id, technician_id=technician_id).first():
            raise ServiceRequestServiceError("Technician already assigned to this request.")

        assignment = ServiceAssignment(request_id=request_id, technician_id=technician_id)
        if request.status == "Open":
            request.status = "In Progress"
        db.session.add(assignment)
        db.session.commit()
        log_audit("technician_assigned", "ServiceRequest", request_id, f"Technician {technician_id}")
        return assignment

    @staticmethod
    def update_status(request_id: int, new_status: str) -> ServiceRequest:
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise ServiceRequestServiceError("Service request not found.")

        allowed = SERVICE_TRANSITIONS.get(request.status, set())
        if new_status not in allowed and new_status != request.status:
            raise ServiceRequestServiceError(f"Cannot transition from '{request.status}' to '{new_status}'.")

        if new_status == "Resolved":
            if MaintenanceRecord.query.filter_by(request_id=request_id).count() == 0:
                raise ServiceRequestServiceError("At least one maintenance record is required to resolve.")

        old_status = request.status
        request.status = new_status
        if new_status == "Resolved":
            request.date_resolved = datetime.utcnow()
        db.session.commit()
        log_audit("status_change", "ServiceRequest", request_id, f"{old_status} -> {new_status}")
        return request
