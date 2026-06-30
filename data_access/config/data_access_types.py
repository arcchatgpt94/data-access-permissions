from __future__ import annotations


DATA_ACCESS_TYPES = [
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


def get_type_by_name(name: str) -> dict | None:
    return next((item for item in DATA_ACCESS_TYPES if item["name"] == name), None)


def get_types_for_doctype(doctype: str) -> list[dict]:
    return [item for item in DATA_ACCESS_TYPES if doctype in item.get("apply_to", [])]


def get_all_names() -> list[str]:
    return [item["name"] for item in DATA_ACCESS_TYPES]
