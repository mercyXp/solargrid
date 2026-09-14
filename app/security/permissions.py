"""Centralized RBAC permission definitions."""

from enum import Enum


class Permission(str, Enum):
    VIEW_DASHBOARD = "view_dashboard"
    MANAGE_STAFF = "manage_staff"
    VIEW_STAFF = "view_staff"
    MANAGE_CUSTOMERS = "manage_customers"
    VIEW_CUSTOMERS = "view_customers"
    MANAGE_SITES = "manage_sites"
    VIEW_SITES = "view_sites"
    MANAGE_EQUIPMENT_TYPES = "manage_equipment_types"
    VIEW_EQUIPMENT_TYPES = "view_equipment_types"
    MANAGE_EQUIPMENT = "manage_equipment"
    VIEW_EQUIPMENT = "view_equipment"
    MANAGE_TECHNICIANS = "manage_technicians"
    VIEW_TECHNICIANS = "view_technicians"
    MANAGE_INSTALLATIONS = "manage_installations"
    VIEW_INSTALLATIONS = "view_installations"
    COMPLETE_INSTALLATIONS = "complete_installations"
    MANAGE_SERVICE_REQUESTS = "manage_service_requests"
    VIEW_SERVICE_REQUESTS = "view_service_requests"
    CREATE_SERVICE_REQUESTS = "create_service_requests"
    MANAGE_MAINTENANCE = "manage_maintenance"
    VIEW_MAINTENANCE = "view_maintenance"
    MANAGE_WARRANTIES = "manage_warranties"
    VIEW_WARRANTIES = "view_warranties"
    MANAGE_INVOICES = "manage_invoices"
    VIEW_INVOICES = "view_invoices"
    MANAGE_PAYMENTS = "manage_payments"
    VIEW_PAYMENTS = "view_payments"
    VIEW_REPORTS = "view_reports"
    VIEW_AUDIT = "view_audit"
    VIEW_SETTINGS = "view_settings"


ROLE_PERMISSIONS = {
    "Administrator": {p for p in Permission},
    "Sales Rep": {
        Permission.VIEW_DASHBOARD,
        Permission.MANAGE_CUSTOMERS,
        Permission.VIEW_CUSTOMERS,
        Permission.MANAGE_SITES,
        Permission.VIEW_SITES,
        Permission.VIEW_EQUIPMENT_TYPES,
        Permission.VIEW_INSTALLATIONS,
        Permission.MANAGE_INVOICES,
        Permission.VIEW_INVOICES,
    },
    "Operations Manager": {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CUSTOMERS,
        Permission.VIEW_SITES,
        Permission.VIEW_EQUIPMENT,
        Permission.VIEW_EQUIPMENT_TYPES,
        Permission.MANAGE_INSTALLATIONS,
        Permission.VIEW_INSTALLATIONS,
        Permission.COMPLETE_INSTALLATIONS,
        Permission.MANAGE_TECHNICIANS,
        Permission.VIEW_TECHNICIANS,
        Permission.MANAGE_SERVICE_REQUESTS,
        Permission.VIEW_SERVICE_REQUESTS,
        Permission.VIEW_MAINTENANCE,
        Permission.VIEW_WARRANTIES,
        Permission.VIEW_REPORTS,
    },
    "Technician": {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_INSTALLATIONS,
        Permission.VIEW_SERVICE_REQUESTS,
        Permission.MANAGE_MAINTENANCE,
        Permission.VIEW_MAINTENANCE,
        Permission.VIEW_EQUIPMENT,
        Permission.VIEW_SITES,
        Permission.VIEW_WARRANTIES,
    },
    "Warehouse Clerk": {
        Permission.VIEW_DASHBOARD,
        Permission.MANAGE_EQUIPMENT_TYPES,
        Permission.VIEW_EQUIPMENT_TYPES,
        Permission.MANAGE_EQUIPMENT,
        Permission.VIEW_EQUIPMENT,
        Permission.MANAGE_WARRANTIES,
        Permission.VIEW_WARRANTIES,
        Permission.VIEW_INSTALLATIONS,
    },
    "Customer Service": {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CUSTOMERS,
        Permission.VIEW_SITES,
        Permission.CREATE_SERVICE_REQUESTS,
        Permission.VIEW_SERVICE_REQUESTS,
        Permission.VIEW_MAINTENANCE,
        Permission.VIEW_EQUIPMENT,
    },
    "Finance Officer": {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CUSTOMERS,
        Permission.MANAGE_INVOICES,
        Permission.VIEW_INVOICES,
        Permission.MANAGE_PAYMENTS,
        Permission.VIEW_PAYMENTS,
        Permission.VIEW_REPORTS,
    },
    "Auditor": {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CUSTOMERS,
        Permission.VIEW_SITES,
        Permission.VIEW_EQUIPMENT,
        Permission.VIEW_EQUIPMENT_TYPES,
        Permission.VIEW_INSTALLATIONS,
        Permission.VIEW_TECHNICIANS,
        Permission.VIEW_SERVICE_REQUESTS,
        Permission.VIEW_MAINTENANCE,
        Permission.VIEW_WARRANTIES,
        Permission.VIEW_INVOICES,
        Permission.VIEW_PAYMENTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_AUDIT,
        Permission.VIEW_STAFF,
    },
}


def has_permission(role: str, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def is_read_only_role(role: str) -> bool:
    return role == "Auditor"


def can_write(role: str) -> bool:
    return not is_read_only_role(role)
