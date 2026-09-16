from datetime import date

from app.extensions import db


class EquipmentType(db.Model):
    __tablename__ = "equipment_type"
    __table_args__ = (
        db.UniqueConstraint("model_number", name="uk_equipment_type_model_number"),
        db.CheckConstraint("unit_price > 0", name="chk_equipment_type_unit_price"),
        db.CheckConstraint("default_warranty_months > 0", name="chk_equipment_type_warranty_months"),
    )

    equipment_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(
        db.Enum(
            "Solar Panel",
            "Battery",
            "Inverter",
            "Charge Controller",
            "Mounting",
            "Accessory",
            name="equipment_category_enum",
        ),
        nullable=False,
    )
    manufacturer = db.Column(db.String(100), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.String(50), nullable=True)
    model_number = db.Column(db.String(50), nullable=True)
    specifications = db.Column(db.Text, nullable=True)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    default_warranty_months = db.Column(db.Integer, nullable=False, default=12)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    equipment_items = db.relationship("Equipment", back_populates="equipment_type", lazy="dynamic")

    @property
    def type_label(self) -> str:
        """Manufacturer, model name, and power/capacity rating for lists and dropdowns."""
        base = f"{self.manufacturer} {self.model_name}"
        return f"{base} ({self.rating})" if self.rating else base

    def __repr__(self):
        return f"<EquipmentType {self.model_name}>"


class Equipment(db.Model):
    __tablename__ = "equipment"
    __table_args__ = (db.UniqueConstraint("serial_number", name="uk_equipment_serial_number"),)

    equipment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_type_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "equipment_type.equipment_type_id",
            name="fk_equipment_equipment_type_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    serial_number = db.Column(db.String(50), nullable=False)
    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.site_id", name="fk_equipment_site_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    status = db.Column(
        db.Enum(
            "Available",
            "Reserved",
            "Installed",
            "Faulty",
            "Decommissioned",
            name="equipment_status_enum",
        ),
        nullable=False,
        default="Available",
    )
    date_received = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)

    equipment_type = db.relationship("EquipmentType", back_populates="equipment_items")
    site = db.relationship("Site", back_populates="equipment_items")
    installation_detail = db.relationship("InstallationDetail", back_populates="equipment", uselist=False)
    warranties = db.relationship("Warranty", back_populates="equipment", lazy="dynamic")
    service_requests = db.relationship("ServiceRequest", back_populates="equipment", lazy="dynamic")

    def __repr__(self):
        return f"<Equipment {self.serial_number}>"
