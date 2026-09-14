from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms.customer import CustomerForm
from app.models.customer import Customer
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


@customers_bp.route("/")
@permission_required(Permission.VIEW_CUSTOMERS)
def index():
    page = get_page()
    per_page = get_per_page()
    query = Customer.query
    search = request.args.get("q", "").strip()
    customer_type = request.args.get("customer_type", "")
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Customer.first_name.ilike(like),
                Customer.last_name.ilike(like),
                Customer.email.ilike(like),
                Customer.phone.ilike(like),
                Customer.company_name.ilike(like),
            )
        )
    if customer_type:
        query = query.filter_by(customer_type=customer_type)
    pagination = query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "customers/index.html",
        **pagination_context(pagination, "customers.index"),
        search=search,
        customer_type=customer_type,
    )


@customers_bp.route("/<int:customer_id>")
@permission_required(Permission.VIEW_CUSTOMERS)
def detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template("customers/detail.html", customer=customer)


@customers_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_CUSTOMERS)
def create():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            company_name=form.company_name.data or None,
            email=form.email.data.lower(),
            phone=form.phone.data,
            address=form.address.data,
            customer_type=form.customer_type.data,
        )
        try:
            db.session.add(customer)
            db.session.commit()
            log_audit("customer_created", "Customer", customer.customer_id)
            flash("Customer created successfully.", "success")
            return redirect(url_for("customers.detail", customer_id=customer.customer_id))
        except IntegrityError:
            db.session.rollback()
            flash("Email address already exists.", "danger")
    return render_template("customers/form.html", form=form, title="Create Customer")


@customers_bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_CUSTOMERS)
def edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.first_name = form.first_name.data
        customer.last_name = form.last_name.data
        customer.company_name = form.company_name.data or None
        customer.email = form.email.data.lower()
        customer.phone = form.phone.data
        customer.address = form.address.data
        customer.customer_type = form.customer_type.data
        try:
            db.session.commit()
            log_audit("customer_updated", "Customer", customer.customer_id)
            flash("Customer updated successfully.", "success")
            return redirect(url_for("customers.detail", customer_id=customer.customer_id))
        except IntegrityError:
            db.session.rollback()
            flash("Email address already exists.", "danger")
    return render_template("customers/form.html", form=form, title="Edit Customer", customer=customer)


@customers_bp.route("/<int:customer_id>/delete", methods=["POST"])
@write_required
@permission_required(Permission.MANAGE_CUSTOMERS)
def delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.sites.count() > 0:
        flash("Cannot delete customer with existing sites.", "danger")
        return redirect(url_for("customers.detail", customer_id=customer_id))
    db.session.delete(customer)
    db.session.commit()
    log_audit("customer_deleted", "Customer", customer_id)
    flash("Customer deleted.", "success")
    return redirect(url_for("customers.index"))
