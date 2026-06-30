import frappe

from data_access.config.data_permission_dimensions import (
    DEFAULT_DATA_PERMISSION_DIMENSIONS,
    discover_dimension_targets,
)


def sync_data_permission_dimensions():
    if not frappe.db.table_exists("Data Permission Dimension"):
        return

    for dimension in DEFAULT_DATA_PERMISSION_DIMENSIONS:
        doc = _get_or_create_dimension(dimension)
        discovered_targets = discover_dimension_targets(dimension["doctype"])
        _ensure_targets(doc, discovered_targets or _fallback_targets(dimension))
        doc.flags.ignore_permissions = True
        doc.save()


def _get_or_create_dimension(dimension: dict):
    name = dimension["name"]
    if frappe.db.exists("Data Permission Dimension", name):
        doc = frappe.get_doc("Data Permission Dimension", name)
    else:
        doc = frappe.new_doc("Data Permission Dimension")
        doc.dimension = name
        doc.is_enabled = 1

    doc.label = dimension["label"]
    doc.label_en = dimension["label_en"]
    doc.source_doctype = dimension["doctype"]
    doc.field_name = dimension["field_name"]
    doc.allow_blank = int(bool(dimension.get("allow_blank")))
    return doc


def _ensure_targets(doc, targets: list[dict]):
    existing = {(row.target_doctype, row.field_name) for row in doc.target_doctypes}
    for target in targets:
        key = (target["target_doctype"], target["field_name"])
        if key not in existing:
            doc.append("target_doctypes", target)


def _fallback_targets(dimension: dict) -> list[dict]:
    return [
        {"target_doctype": doctype, "field_name": dimension["field_name"]}
        for doctype in dimension.get("apply_to", [])
    ]
