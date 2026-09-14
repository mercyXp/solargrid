from flask import Blueprint, render_template, request

from app.models.warranty import Warranty
from app.security.decorators import permission_required
from app.security.permissions import Permission
from app.services.warranty_service import WarrantyService
from app.utils.pagination import get_page, get_per_page, pagination_context

warranties_bp = Blueprint("warranties", __name__, url_prefix="/warranties")


@warranties_bp.route("/")
@permission_required(Permission.VIEW_WARRANTIES)
def index():
    page = get_page()
    per_page = get_per_page()
    status = request.args.get("status", "")
    query = Warranty.query
    if status:
        query = query.filter(Warranty.status == status)
    view = request.args.get("view", "")
    if view == "expiring":
        items = WarrantyService.get_expiring(30)
        return render_template("warranties/index.html", warranties=items, view=view, pagination=None)
    if view == "expired":
        items = WarrantyService.get_expired()
        return render_template("warranties/index.html", warranties=items, view=view, pagination=None)
    pagination = query.order_by(Warranty.end_date.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "warranties/index.html",
        **pagination_context(pagination, "warranties.index"),
        status=status,
        view=view,
    )


@warranties_bp.route("/<int:warranty_id>")
@permission_required(Permission.VIEW_WARRANTIES)
def detail(warranty_id):
    warranty = Warranty.query.get_or_404(warranty_id)
    return render_template("warranties/detail.html", warranty=warranty)
