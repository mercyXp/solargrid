from app.extensions import db


class Warranty(db.Model):
    __tablename__ = "warranty"
    __table_args__ = (db.CheckConstraint("end_date > start_date", name="chk_warranty_dates"),)

    warranty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(
        db.Integer,
        db.ForeignKey("equipment.equipment_id", name="fk_warranty_equipment_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    warranty_type = db.Column(
        db.Enum("Manufacturer", "Extended", "SolarGrid", name="warranty_type_enum"),
        nullable=False,
        default="Manufacturer",
    )
    terms = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum("Active", "Expired", "Claimed", "Voided", name="warranty_status_enum"),
        nullable=False,
        default="Active",
    )

    equipment = db.relationship("Equipment", back_populates="warranties")
