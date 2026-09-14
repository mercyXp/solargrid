from datetime import datetime

from app.extensions import db


class Installation(db.Model):
    __tablename__ = "installation"

    installation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.site_id", name="fk_installation_site_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    planned_date = db.Column(db.Date, nullable=False)
    actual_start_date = db.Column(db.Date, nullable=True)
    completion_date = db.Column(db.Date, nullable=True)
    status = db.Column(
        db.Enum("Scheduled", "In Progress", "Completed", "Cancelled", name="installation_status_enum"),
        nullable=False,
        default="Scheduled",
    )
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("staff.staff_id", name="fk_installation_created_by", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    site = db.relationship("Site", back_populates="installations")
    creator = db.relationship("Staff", back_populates="installations_created")
    details = db.relationship("InstallationDetail", back_populates="installation", lazy="dynamic", cascade="all, delete-orphan")
    assignments = db.relationship(
        "InstallationAssignment", back_populates="installation", lazy="dynamic", cascade="all, delete-orphan"
    )
    invoices = db.relationship("Invoice", back_populates="installation", lazy="dynamic")

    def __repr__(self):
        return f"<Installation {self.installation_id}>"


class InstallationDetail(db.Model):
    __tablename__ = "installation_detail"
    __table_args__ = (
        db.UniqueConstraint("equipment_id", name="uk_installation_detail_equipment_id"),
        db.UniqueConstraint("installation_id", "equipment_id", name="uk_installation_detail_install_equip"),
        db.CheckConstraint("quantity >= 1", name="chk_installation_detail_quantity"),
        db.CheckConstraint("unit_price_at_install > 0", name="chk_installation_detail_price"),
    )

    install_detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "installation.installation_id",
            name="fk_installation_detail_installation_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    equipment_id = db.Column(
        db.Integer,
        db.ForeignKey("equipment.equipment_id", name="fk_installation_detail_equipment_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price_at_install = db.Column(db.Numeric(12, 2), nullable=False)

    installation = db.relationship("Installation", back_populates="details")
    equipment = db.relationship("Equipment", back_populates="installation_detail")


class InstallationAssignment(db.Model):
    __tablename__ = "installation_assignment"
    __table_args__ = (
        db.UniqueConstraint("installation_id", "technician_id", name="uk_installation_assignment"),
    )

    install_assign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "installation.installation_id",
            name="fk_installation_assignment_installation_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    technician_id = db.Column(
        db.Integer,
        db.ForeignKey("technician.technician_id", name="fk_installation_assignment_technician_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role_in_team = db.Column(
        db.Enum("Lead", "Assistant", name="role_in_team_enum"),
        nullable=False,
        default="Assistant",
    )

    installation = db.relationship("Installation", back_populates="assignments")
    technician = db.relationship("Technician", back_populates="installation_assignments")
