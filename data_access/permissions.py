from __future__ import annotations

from typing import Literal

import frappe
from frappe import _

from data_access.config.data_access_types import get_types_for_doctype


PermissionAction = Literal["view", "add", "edit", "delete"]

ACTION_FIELD = {
    "view": "can_view",
    "add": "can_add",
    "edit": "can_edit",
    "delete": "can_delete",
}


def user_is_system_manager(user: str | None = None) -> bool:
    user = user or frappe.session.user
    return "System Manager" in frappe.get_roles(user)


def _cache_key(user: str, access_type: str, action: PermissionAction) -> str:
    return f"data_access::{user}::{access_type}::{action}"


def _get_applicable_permission_records(user: str, access_type: str) -> list[str]:
    user_records = frappe.get_all(
        "Data Access Permission",
        filters={"user": user, "access_type": access_type, "is_active": 1},
        pluck="name",
    )

    user_groups = frappe.get_all(
        "User Group Member",
        filters={"user": user},
        pluck="parent",
    )

    group_records: list[str] = []
    if user_groups:
        group_records = frappe.get_all(
            "Data Access Permission",
            filters={
                "user_group": ["in", user_groups],
                "access_type": access_type,
                "is_active": 1,
            },
            pluck="name",
        )

    return sorted(set(user_records + group_records))


def get_user_allowed_values(
    user: str,
    access_type: str,
    action: PermissionAction = "view",
) -> list[str] | None:
    """Return None for unrestricted users, or a list of allowed values.

    An empty list means the user is restricted but has no allowed values for
    this action, so access must be denied.
    """
    cache_key = _cache_key(user, access_type, action)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None:
        return cached

    permission_records = _get_applicable_permission_records(user, access_type)
    if not permission_records:
        frappe.cache().set_value(cache_key, None, expires_in_sec=300)
        return None

    allowed = frappe.get_all(
        "Data Access Permission Detail",
        filters={
            "parent": ["in", permission_records],
            ACTION_FIELD[action]: 1,
        },
        pluck="reference_value",
    )

    allowed = sorted(set(filter(None, allowed)))
    frappe.cache().set_value(cache_key, allowed, expires_in_sec=300)
    return allowed


def clear_user_cache(user: str | None = None):
    if user:
        frappe.cache().delete_keys(f"data_access::{user}::*")
    else:
        frappe.cache().delete_keys("data_access::*")


def _field_condition(doctype: str, field: str, values: list[str], allow_blank: bool) -> str:
    field_sql = f"`tab{doctype}`.`{field}`"
    escaped_values = ", ".join(frappe.db.escape(value) for value in values)
    value_condition = f"{field_sql} IN ({escaped_values})" if values else "1 = 0"

    if allow_blank:
        return f"(IFNULL({field_sql}, '') = '' OR {value_condition})"

    return f"({value_condition})"


def get_permission_query_condition(doctype: str, user: str | None = None) -> str:
    user = user or frappe.session.user
    if user_is_system_manager(user):
        return ""

    conditions = []
    for access_type in get_types_for_doctype(doctype):
        allowed = get_user_allowed_values(user, access_type["name"], "view")
        if allowed is None:
            continue

        conditions.append(
            _field_condition(
                doctype=doctype,
                field=access_type["field_name"],
                values=allowed,
                allow_blank=bool(access_type.get("allow_blank", False)),
            )
        )

    return " AND ".join(conditions)


def validate_document_access(doc, method: str | None = None):
    user = frappe.session.user
    if user_is_system_manager(user):
        return

    action = _action_from_method(doc, method)
    for access_type in get_types_for_doctype(doc.doctype):
        allowed = get_user_allowed_values(user, access_type["name"], action)
        if allowed is None:
            continue

        field_value = doc.get(access_type["field_name"])
        if not field_value and access_type.get("allow_blank", False):
            continue

        if not field_value or field_value not in allowed:
            frappe.throw(
                _("You are not allowed to {0} this document for {1}: {2}").format(
                    _(action),
                    _(access_type.get("label_en") or access_type["label"]),
                    field_value or _("empty value"),
                ),
                frappe.PermissionError,
                title=_("Access denied"),
            )


def _action_from_method(doc, method: str | None) -> PermissionAction:
    if method == "before_insert":
        return "add"
    if method == "on_trash":
        return "delete"
    if getattr(doc, "is_new", None) and doc.is_new():
        return "add"
    return "edit"


@frappe.whitelist()
def get_allowed_values_for_user(user: str, access_type: str) -> list[str]:
    if not frappe.has_permission("Data Access Permission", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    return get_user_allowed_values(user, access_type, "view") or []


@frappe.whitelist()
def get_data_access_types() -> list[dict]:
    from data_access.config.data_access_types import DATA_ACCESS_TYPES

    return [
        {
            "name": item["name"],
            "label": item["label"],
            "doctype": item["doctype"],
        }
        for item in DATA_ACCESS_TYPES
    ]
