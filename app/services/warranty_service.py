from datetime import date, timedelta

from app.models.warranty import Warranty


class WarrantyService:
    @staticmethod
    def get_expiring(days: int = 30):
        threshold = date.today() + timedelta(days=days)
        return (
            Warranty.query.filter(
                Warranty.status == "Active",
                Warranty.end_date <= threshold,
                Warranty.end_date >= date.today(),
            )
            .order_by(Warranty.end_date.asc())
            .all()
        )

    @staticmethod
    def get_expired():
        return (
            Warranty.query.filter(
                Warranty.end_date < date.today(),
                Warranty.status == "Active",
            )
            .order_by(Warranty.end_date.desc())
            .all()
        )

    @staticmethod
    def search(status=None, equipment_id=None, customer_id=None, site_id=None, date_from=None, date_to=None):
        from app.models.equipment import Equipment

        query = Warranty.query.join(Equipment)
        if status:
            query = query.filter(Warranty.status == status)
        if equipment_id:
            query = query.filter(Warranty.equipment_id == equipment_id)
        if site_id:
            query = query.filter(Equipment.site_id == site_id)
        if customer_id:
            from app.models.site import Site

            query = query.join(Site, Equipment.site_id == Site.site_id).filter(Site.customer_id == customer_id)
        if date_from:
            query = query.filter(Warranty.end_date >= date_from)
        if date_to:
            query = query.filter(Warranty.end_date <= date_to)
        return query.order_by(Warranty.end_date.asc())
