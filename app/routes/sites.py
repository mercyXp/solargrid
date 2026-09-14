from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms.site import SiteForm
from app.models.customer import Customer
from app.models.site import Site
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


def _populate_customers(form):
    form.customer_id.choices = [(c.customer_id, c.full_name) for c in Customer.query.order_by(Customer.first_name).all()]


@sites_bp.route("/")
@permission_required(Permission.VIEW_SITES)
def index():
    page = get_page()
    per_page = get_per_page()
    query = Site.query.join(Customer)
    search = request.args.get("q", "").strip()
    customer_id = request.args.get("customer_id", type=int)
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Site.site_name.ilike(like), Site.city.ilike(like), Site.address.ilike(like)))
    if customer_id:
        query = query.filter(Site.customer_id == customer_id)
    pagination = query.order_by(Site.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    customers = Customer.query.order_by(Customer.first_name).all()
    return render_template(
        "sites/index.html",
        **pagination_context(pagination, "sites.index"),
        search=search,
        customer_id=customer_id,
        customers=customers,
    )


@sites_bp.route("/<int:site_id>")
@permission_required(Permission.VIEW_SITES)
def detail(site_id):
    site = Site.query.get_or_404(site_id)
    return render_template("sites/detail.html", site=site)


@sites_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_SITES)
def create():
    form = SiteForm()
    _populate_customers(form)
    if form.validate_on_submit():
        site = Site(
            customer_id=form.customer_id.data,
            site_name=form.site_name.data,
            address=form.address.data,
            city=form.city.data,
            province=form.province.data,
            postal_code=form.postal_code.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            site_type=form.site_type.data,
        )
        db.session.add(site)
        db.session.commit()
        log_audit("site_created", "Site", site.site_id)
        flash("Site created successfully.", "success")
        return redirect(url_for("sites.detail", site_id=site.site_id))
    return render_template("sites/form.html", form=form, title="Create Site")


@sites_bp.route("/<int:site_id>/edit", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_SITES)
def edit(site_id):
    site = Site.query.get_or_404(site_id)
    form = SiteForm(obj=site)
    _populate_customers(form)
    if form.validate_on_submit():
        site.customer_id = form.customer_id.data
        site.site_name = form.site_name.data
        site.address = form.address.data
        site.city = form.city.data
        site.province = form.province.data
        site.postal_code = form.postal_code.data
        site.latitude = form.latitude.data
        site.longitude = form.longitude.data
        site.site_type = form.site_type.data
        db.session.commit()
        log_audit("site_updated", "Site", site.site_id)
        flash("Site updated.", "success")
        return redirect(url_for("sites.detail", site_id=site.site_id))
    return render_template("sites/form.html", form=form, title="Edit Site", site=site)
