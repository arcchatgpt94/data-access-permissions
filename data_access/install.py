import frappe

from data_access.config.data_access_types import DEFAULT_DATA_ACCESS_TYPES


def sync_data_access_types():
    if not frappe.db.table_exists("Data Access Type"):
        return

    for access_type in DEFAULT_DATA_ACCESS_TYPES:
        doc = _get_or_create_type(access_type)
        _ensure_targets(doc, access_type["apply_to"])
        doc.flags.ignore_permissions = True
        doc.save()


def _get_or_create_type(access_type: dict):
    name = access_type["name"]
    if frappe.db.exists("Data Access Type", name):
        doc = frappe.get_doc("Data Access Type", name)
    else:
        doc = frappe.new_doc("Data Access Type")
        doc.access_type = name
        doc.is_enabled = 1

    doc.label = access_type["label"]
    doc.label_en = access_type["label_en"]
    doc.source_doctype = access_type["doctype"]
    doc.field_name = access_type["field_name"]
    doc.allow_blank = int(bool(access_type.get("allow_blank")))
    return doc


def _ensure_targets(doc, targets: list[str]):
    existing = {row.target_doctype for row in doc.target_doctypes}
    for target in targets:
        if target not in existing:
            doc.append("target_doctypes", {"target_doctype": target})
