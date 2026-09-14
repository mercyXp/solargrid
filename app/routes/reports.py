from flask import Blueprint, render_template, request

from app.security.decorators import permission_required
from app.security.permissions import Permission
from app.services.reporting_service import ReportingService

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@permission_required(Permission.VIEW_REPORTS)
def index():
    return render_template("reports/index.html")


@reports_bp.route("/warranty-expiry")
@permission_required(Permission.VIEW_REPORTS)
def warranty_expiry():
    status = request.args.get("status", "")
    results = ReportingService.warranty_expiry_report(status=status or None)
    return render_template("reports/warranty_expiry.html", results=results, status=status)


@reports_bp.route("/unresolved-services")
@permission_required(Permission.VIEW_REPORTS)
def unresolved_services():
    results = ReportingService.unresolved_service_requests()
    return render_template("reports/unresolved_services.html", results=results)


@reports_bp.route("/technician-workload")
@permission_required(Permission.VIEW_REPORTS)
def technician_workload():
    results = ReportingService.technician_workload()
    return render_template("reports/technician_workload.html", results=results)


@reports_bp.route("/outstanding-balances")
@permission_required(Permission.VIEW_REPORTS)
def outstanding_balances():
    results = ReportingService.outstanding_balances()
    return render_template("reports/outstanding_balances.html", results=results)


@reports_bp.route("/revenue")
@permission_required(Permission.VIEW_REPORTS)
def revenue():
    period = request.args.get("period", "monthly")
    year = request.args.get("year", type=int)
    results = ReportingService.revenue_report(period, year)
    return render_template("reports/revenue.html", results=results, period=period, year=year)
