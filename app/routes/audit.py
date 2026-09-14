from flask import Blueprint, render_template, request

from app.models.audit import AuditLog
from app.security.decorators import permission_required
from app.security.permissions import Permission
from app.utils.pagination import get_page, get_per_page, pagination_context

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")


@audit_bp.route("/")
@permission_required(Permission.VIEW_AUDIT)
def index():
    page = get_page()
    per_page = get_per_page()
    query = AuditLog.query
    action = request.args.get("action", "")
    entity_type = request.args.get("entity_type", "")
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    pagination = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "audit/index.html",
        **pagination_context(pagination, "audit.index"),
        action=action,
        entity_type=entity_type,
    )
