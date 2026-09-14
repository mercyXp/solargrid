import logging
import os
from datetime import timedelta

from flask import Flask, g, session

from app.extensions import csrf, db, limiter, migrate
from config import config_by_name


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    if config_name not in config_by_name:
        config_name = "development"
    config_class = config_by_name[config_name]

    app = Flask(__name__)
    app.config.from_object(config_class)
    if hasattr(config_class, "init_app"):
        config_class.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    _configure_logging(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context_processors(app)
    _register_security_headers(app)

    @app.before_request
    def load_current_user():
        from app.models.staff import Staff

        g.current_user = None
        staff_id = session.get("staff_id")
        if staff_id:
            g.current_user = Staff.query.get(staff_id)

    return app


def _configure_logging(app):
    logging.basicConfig(
        level=logging.DEBUG if app.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _register_blueprints(app):
    from app.routes.audit import audit_bp
    from app.routes.auth import auth_bp
    from app.routes.customers import customers_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.equipment import equipment_bp
    from app.routes.installations import installations_bp
    from app.routes.invoices import invoices_bp
    from app.routes.maintenance import maintenance_bp
    from app.routes.payments import payments_bp
    from app.routes.reports import reports_bp
    from app.routes.services import services_bp
    from app.routes.sites import sites_bp
    from app.routes.staff import staff_bp
    from app.routes.technicians import technicians_bp
    from app.routes.warranties import warranties_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(sites_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(installations_bp)
    app.register_blueprint(technicians_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(warranties_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(audit_bp)


def _register_error_handlers(app):
    from flask import render_template

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def rate_limited(e):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _register_context_processors(app):
    from app.security.permissions import Permission, ROLE_PERMISSIONS, has_permission

    @app.context_processor
    def inject_globals():
        user = getattr(g, "current_user", None)
        role = user.role if user else None
        return {
            "current_user": user,
            "has_permission": lambda perm: has_permission(role, perm) if role else False,
            "Permission": Permission,
            "ROLE_PERMISSIONS": ROLE_PERMISSIONS,
        }


def _register_security_headers(app):
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com; "
            "font-src 'self' fonts.gstatic.com cdn.jsdelivr.net; "
            "img-src 'self' data:;"
        )
        if not app.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
