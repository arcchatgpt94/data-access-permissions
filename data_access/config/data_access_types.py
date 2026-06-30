from __future__ import annotations

import frappe


DEFAULT_DATA_ACCESS_TYPES = [
    {
        "name": "Branch",
        "label": "الفروع",
        "label_en": "Branch",
        "doctype": "Branch",
        "field_name": "branch",
        "allow_blank": False,
        "apply_to": [
            "Employee",
            "Sales Invoice",
            "Purchase Invoice",
            "Journal Entry",
            "Payment Entry",
            "Salary Slip",
            "Attendance",
            "Leave Application",
        ],
    },
    {
        "name": "Cost Center",
        "label": "مراكز التكلفة",
        "label_en": "Cost Center",
        "doctype": "Cost Center",
        "field_name": "cost_center",
        "allow_blank": False,
        "apply_to": [
            "Journal Entry",
            "Purchase Invoice",
            "Sales Invoice",
            "Payment Entry",
            "Budget",
        ],
    },
    {
        "name": "Account",
        "label": "الحسابات",
        "label_en": "Account",
        "doctype": "Account",
        "field_name": "account",
        "allow_blank": False,
        "apply_to": [
            "Journal Entry",
            "Payment Entry",
            "Bank Statement Transaction",
        ],
    },
    {
        "name": "Warehouse",
        "label": "المستودعات",
        "label_en": "Warehouse",
        "doctype": "Warehouse",
        "field_name": "warehouse",
        "allow_blank": False,
        "apply_to": [
            "Stock Entry",
            "Delivery Note",
            "Purchase Receipt",
            "Stock Ledger Entry",
            "Material Request",
        ],
    },
    {
        "name": "Notification Type",
        "label": "أنواع الإشعارات",
        "label_en": "Notification Type",
        "doctype": "Notification",
        "field_name": "notification_type",
        "allow_blank": False,
        "apply_to": [
            "Notification Log",
        ],
    },
    {
        "name": "Request Type",
        "label": "أنواع الطلبات",
        "label_en": "Request Type",
        "doctype": "Material Request Type",
        "field_name": "material_request_type",
        "allow_blank": False,
        "apply_to": [
            "Material Request",
        ],
    },
    {
        "name": "Journal Entry Type",
        "label": "أنواع القيود",
        "label_en": "Journal Entry Type",
        "doctype": "Journal Entry Template",
        "field_name": "voucher_type",
        "allow_blank": False,
        "apply_to": [
            "Journal Entry",
        ],
    },
]

# Hooks are loaded before the setup DocTypes may exist, so hook registration
# still needs a static list. Runtime behavior reads from Data Access Type.
DATA_ACCESS_TYPES = DEFAULT_DATA_ACCESS_TYPES


def get_configured_access_types(enabled_only: bool = True) -> list[dict]:
    if not _data_access_type_table_exists():
        return DEFAULT_DATA_ACCESS_TYPES

    filters = {"is_enabled": 1} if enabled_only else {}
    rows = frappe.get_all(
        "Data Access Type",
        filters=filters,
        fields=[
            "name",
            "access_type",
            "label",
            "label_en",
            "source_doctype",
            "field_name",
            "allow_blank",
        ],
        order_by="access_type asc",
    )

    if not rows and enabled_only:
        return []

    targets_by_parent = _get_targets_by_parent([row.name for row in rows])
    return [_row_to_config(row, targets_by_parent.get(row.name, [])) for row in rows]


def get_type_by_name(name: str) -> dict | None:
    return next(
        (item for item in get_configured_access_types(enabled_only=False) if item["name"] == name),
        None,
    )


def get_types_for_doctype(doctype: str) -> list[dict]:
    return [
        item
        for item in get_configured_access_types(enabled_only=True)
        if doctype in item.get("apply_to", [])
    ]


def get_all_names() -> list[str]:
    return [item["name"] for item in get_configured_access_types(enabled_only=True)]


def _data_access_type_table_exists() -> bool:
    try:
        return frappe.db.table_exists("Data Access Type")
    except Exception:
        return False


def _get_targets_by_parent(parents: list[str]) -> dict[str, list[str]]:
    if not parents:
        return {}

    target_rows = frappe.get_all(
        "Data Access Type Target",
        filters={"parent": ["in", parents]},
        fields=["parent", "target_doctype"],
        order_by="idx asc",
    )

    out: dict[str, list[str]] = {}
    for row in target_rows:
        if row.target_doctype:
            out.setdefault(row.parent, []).append(row.target_doctype)
    return out


def _row_to_config(row, apply_to: list[str]) -> dict:
    return {
        "name": row.access_type,
        "label": row.label or row.access_type,
        "label_en": row.label_en or row.access_type,
        "doctype": row.source_doctype,
        "field_name": row.field_name,
        "allow_blank": bool(row.allow_blank),
        "apply_to": apply_to,
    }
