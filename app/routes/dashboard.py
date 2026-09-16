from datetime import date, timedelta

from flask import Blueprint, render_template

from app.models.installation import Installation
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.service_request import ServiceRequest
from app.security.decorators import login_required, permission_required
from app.security.permissions import Permission
from app.services.reporting_service import ReportingService
from app.services.warranty_service import WarrantyService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
@permission_required(Permission.VIEW_DASHBOARD)
def index():
    kpis = ReportingService.dashboard_kpis()
    charts = ReportingService.chart_data()
    recent_installations = Installation.query.order_by(Installation.created_at.desc()).limit(5).all()
    recent_services = ServiceRequest.query.order_by(ServiceRequest.date_raised.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    expiring_warranties = WarrantyService.get_expiring(30)[:5]
    overdue_invoices = (
        Invoice.query.filter(
            Invoice.status.in_(["Issued", "Partially Paid", "Overdue"]),
            Invoice.due_date < date.today(),
        )
        .order_by(Invoice.due_date.asc())
        .limit(5)
        .all()
    )
    critical_requests = (
        ServiceRequest.query.filter(
            ServiceRequest.priority == "Critical",
            ServiceRequest.status.in_(["Open", "In Progress"]),
        )
        .limit(5)
        .all()
    )
    unassigned_requests = [
        sr
        for sr in ServiceRequest.query.filter(ServiceRequest.status.in_(["Open", "In Progress"])).all()
        if sr.assignments.count() == 0
    ][:5]
    attention_installations = (
        Installation.query.filter(
            Installation.status.in_(["Scheduled", "In Progress"]),
            Installation.planned_date <= date.today() + timedelta(days=7),
        )
        .order_by(Installation.planned_date.asc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        kpis=kpis,
        charts=charts,
        recent_installations=recent_installations,
        recent_services=recent_services,
        recent_payments=recent_payments,
        expiring_warranties=expiring_warranties,
        overdue_invoices=overdue_invoices,
        critical_requests=critical_requests,
        unassigned_requests=unassigned_requests,
        attention_installations=attention_installations,
    )
