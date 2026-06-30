from __future__ import annotations

import frappe


DEFAULT_DATA_PERMISSION_DIMENSIONS = [
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
        "name": "Department",
        "label": "الإدارات",
        "label_en": "Department",
        "doctype": "Department",
        "field_name": "department",
        "allow_blank": False,
        "apply_to": [
            "Employee",
            "Job Applicant",
        ],
    },
    {
        "name": "Designation",
        "label": "المسميات الوظيفية",
        "label_en": "Designation",
        "doctype": "Designation",
        "field_name": "designation",
        "allow_blank": False,
        "apply_to": [
            "Employee",
            "Job Applicant",
        ],
    },
    {
        "name": "Company",
        "label": "الشركات",
        "label_en": "Company",
        "doctype": "Company",
        "field_name": "company",
        "allow_blank": False,
        "apply_to": [
            "Sales Invoice",
            "Purchase Invoice",
            "Journal Entry",
            "Payment Entry",
            "Stock Entry",
            "Employee",
        ],
    },
]

# Hooks are loaded before setup DocTypes may exist. Runtime behavior reads from
# Data Permission Dimension after the app is installed.
DATA_PERMISSION_DIMENSIONS = DEFAULT_DATA_PERMISSION_DIMENSIONS


def get_configured_dimensions(enabled_only: bool = True) -> list[dict]:
    if not _dimension_table_exists():
        return DEFAULT_DATA_PERMISSION_DIMENSIONS

    filters = {"is_enabled": 1} if enabled_only else {}
    rows = frappe.get_all(
        "Data Permission Dimension",
        filters=filters,
        fields=[
            "name",
            "dimension",
            "label",
            "label_en",
            "source_doctype",
            "field_name",
            "allow_blank",
        ],
        order_by="dimension asc",
    )

    targets_by_parent = get_targets_by_parent([row.name for row in rows])
    return [_row_to_config(row, targets_by_parent.get(row.name, [])) for row in rows]


def get_type_by_name(name: str) -> dict | None:
    return next(
        (item for item in get_configured_dimensions(enabled_only=False) if item["name"] == name),
        None,
    )


def get_types_for_doctype(doctype: str) -> list[dict]:
    out = []
    for item in get_configured_dimensions(enabled_only=True):
        for target in item.get("targets", []):
            if target["doctype"] == doctype:
                row = item.copy()
                row["field_name"] = target["field_name"]
                out.append(row)
    return out


def get_all_names() -> list[str]:
    return [item["name"] for item in get_configured_dimensions(enabled_only=True)]


def _dimension_table_exists() -> bool:
    try:
        return frappe.db.table_exists("Data Permission Dimension")
    except Exception:
        return False


def get_targets_by_parent(parents: list[str]) -> dict[str, list[dict]]:
    if not parents:
        return {}

    target_rows = frappe.get_all(
        "Data Permission Dimension Target",
        filters={"parent": ["in", parents]},
        fields=["parent", "target_doctype", "field_name"],
        order_by="idx asc",
    )

    out: dict[str, list[dict]] = {}
    for row in target_rows:
        if row.target_doctype and row.field_name:
            out.setdefault(row.parent, []).append(
                {"doctype": row.target_doctype, "field_name": row.field_name}
            )
    return out


def discover_dimension_targets(source_doctype: str) -> list[dict]:
    """Find non-child DocTypes that have Link fields pointing to source_doctype."""
    targets: dict[tuple[str, str], dict] = {}

    for row in frappe.get_all(
        "DocField",
        filters={"fieldtype": "Link", "options": source_doctype},
        fields=["parent", "fieldname"],
    ):
        if not _is_child_table(row.parent):
            targets[(row.parent, row.fieldname)] = {
                "target_doctype": row.parent,
                "field_name": row.fieldname,
            }

    for row in frappe.get_all(
        "Custom Field",
        filters={"fieldtype": "Link", "options": source_doctype},
        fields=["dt", "fieldname"],
    ):
        if not _is_child_table(row.dt):
            targets[(row.dt, row.fieldname)] = {
                "target_doctype": row.dt,
                "field_name": row.fieldname,
            }

    return sorted(targets.values(), key=lambda item: (item["target_doctype"], item["field_name"]))


def _is_child_table(doctype: str) -> bool:
    try:
        return bool(frappe.db.get_value("DocType", doctype, "istable"))
    except Exception:
        return False


def _row_to_config(row, targets: list[dict]) -> dict:
    return {
        "name": row.dimension,
        "label": row.label or row.dimension,
        "label_en": row.label_en or row.dimension,
        "doctype": row.source_doctype,
        "field_name": row.field_name,
        "allow_blank": bool(row.allow_blank),
        "targets": targets,
        "apply_to": sorted({target["doctype"] for target in targets}),
    }
