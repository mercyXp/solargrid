from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import case, func

from app.extensions import db
from app.models.customer import Customer
from app.models.equipment import Equipment
from app.models.installation import Installation, InstallationAssignment, InstallationDetail
from app.models.invoice import Invoice
from app.models.maintenance import MaintenanceRecord
from app.models.service_request import ServiceAssignment, ServiceRequest
from app.models.technician import Technician
from app.models.warranty import Warranty


class ReportingService:
    @staticmethod
    def warranty_expiry_report(status=None, equipment_id=None, customer_id=None, site_id=None, date_from=None, date_to=None):
        from app.services.warranty_service import WarrantyService

        return WarrantyService.search(status, equipment_id, customer_id, site_id, date_from, date_to).all()

    @staticmethod
    def unresolved_service_requests():
        priority_order = case(
            (ServiceRequest.priority == "Critical", 1),
            (ServiceRequest.priority == "High", 2),
            (ServiceRequest.priority == "Medium", 3),
            else_=4,
        )
        return (
            ServiceRequest.query.filter(ServiceRequest.status.in_(["Open", "In Progress"]))
            .order_by(priority_order, ServiceRequest.date_raised.asc())
            .all()
        )

    @staticmethod
    def technician_workload():
        technicians = Technician.query.filter_by(is_active=True).all()
        results = []
        for tech in technicians:
            active_installations = (
                InstallationAssignment.query.join(Installation)
                .filter(
                    InstallationAssignment.technician_id == tech.technician_id,
                    Installation.status.in_(["Scheduled", "In Progress"]),
                )
                .count()
            )
            active_services = (
                ServiceAssignment.query.join(ServiceRequest)
                .filter(
                    ServiceAssignment.technician_id == tech.technician_id,
                    ServiceRequest.status.in_(["Open", "In Progress"]),
                )
                .count()
            )
            maintenance_visits = MaintenanceRecord.query.filter_by(technician_id=tech.technician_id).count()
            results.append(
                {
                    "technician": tech,
                    "active_installations": active_installations,
                    "active_services": active_services,
                    "maintenance_visits": maintenance_visits,
                    "total_workload": active_installations + active_services,
                }
            )
        return sorted(results, key=lambda x: x["total_workload"], reverse=True)

    @staticmethod
    def outstanding_balances():
        invoices = (
            Invoice.query.filter(
                Invoice.status.in_(["Issued", "Partially Paid", "Overdue"]),
                Invoice.amount_paid < Invoice.total_amount,
            )
            .order_by(Invoice.due_date.asc())
            .all()
        )
        today = date.today()
        results = []
        for inv in invoices:
            outstanding = Decimal(str(inv.total_amount)) - Decimal(str(inv.amount_paid))
            days_overdue = (today - inv.due_date).days
            if days_overdue <= 0:
                ageing = "Current"
            elif days_overdue <= 30:
                ageing = "1-30 days"
            elif days_overdue <= 60:
                ageing = "31-60 days"
            elif days_overdue <= 90:
                ageing = "61-90 days"
            else:
                ageing = "90+ days"
            results.append({"invoice": inv, "outstanding": outstanding, "ageing": ageing, "days_overdue": days_overdue})
        return results

    @staticmethod
    def revenue_report(period: str = "monthly", year: int = None):
        year = year or date.today().year
        invoices = Invoice.query.filter(
            Invoice.status.notin_(["Draft", "Cancelled"]),
            func.year(Invoice.date_issued) == year,
        ).all()

        buckets = {}
        for inv in invoices:
            if period == "monthly":
                key = inv.date_issued.strftime("%Y-%m")
            elif period == "quarterly":
                q = (inv.date_issued.month - 1) // 3 + 1
                key = f"{inv.date_issued.year}-Q{q}"
            else:
                key = str(inv.date_issued.year)

            if key not in buckets:
                buckets[key] = {"invoiced": Decimal("0"), "paid": Decimal("0")}
            buckets[key]["invoiced"] += Decimal(str(inv.total_amount))
            buckets[key]["paid"] += Decimal(str(inv.amount_paid))

        return [
            {
                "period": k,
                "total_invoiced": v["invoiced"],
                "total_paid": v["paid"],
                "outstanding": v["invoiced"] - v["paid"],
            }
            for k, v in sorted(buckets.items())
        ]

    @staticmethod
    def dashboard_kpis():
        return {
            "total_customers": Customer.query.count(),
            "active_sites": db.session.query(func.count()).select_from(
                db.session.query(Installation.site_id).distinct().subquery()
            ).scalar() or 0,
            "available_equipment": Equipment.query.filter_by(status="Available").count(),
            "installed_equipment": Equipment.query.filter_by(status="Installed").count(),
            "scheduled_installations": Installation.query.filter_by(status="Scheduled").count(),
            "open_service_requests": ServiceRequest.query.filter(
                ServiceRequest.status.in_(["Open", "In Progress"])
            ).count(),
            "active_warranties": Warranty.query.filter_by(status="Active").count(),
            "outstanding_invoices": Invoice.query.filter(
                Invoice.status.in_(["Issued", "Partially Paid", "Overdue"])
            ).count(),
            "total_revenue": db.session.query(func.coalesce(func.sum(Invoice.amount_paid), 0)).scalar(),
        }

    @staticmethod
    def chart_data():
        year = date.today().year
        revenue = ReportingService.revenue_report("monthly", year)
        installation_status = (
            db.session.query(Installation.status, func.count(Installation.installation_id))
            .group_by(Installation.status)
            .all()
        )
        service_priority = (
            db.session.query(ServiceRequest.priority, func.count(ServiceRequest.request_id))
            .filter(ServiceRequest.status.in_(["Open", "In Progress"]))
            .group_by(ServiceRequest.priority)
            .all()
        )
        equipment_status = (
            db.session.query(Equipment.status, func.count(Equipment.equipment_id))
            .group_by(Equipment.status)
            .all()
        )
        workload = ReportingService.technician_workload()[:10]
        return {
            "monthly_revenue": revenue,
            "installation_status": installation_status,
            "service_priority": service_priority,
            "equipment_status": equipment_status,
            "technician_workload": workload,
        }
