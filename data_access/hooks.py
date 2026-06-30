from data_access.config.data_access_types import DATA_ACCESS_TYPES


app_name = "data_access"
app_title = "Data Access Permissions"
app_publisher = "Your Company"
app_description = "Row-level data access permissions for Frappe/ERPNext"
app_version = "1.1.0"


def _restricted_doctypes() -> list[str]:
    doctypes = set()
    for access_type in DATA_ACCESS_TYPES:
        doctypes.update(access_type.get("apply_to", []))
    return sorted(doctypes)


permission_query_conditions = {
    doctype: "data_access.permissions.get_permission_query_condition"
    for doctype in _restricted_doctypes()
}


doc_events = {
    doctype: {
        "before_insert": "data_access.permissions.validate_document_access",
        "before_save": "data_access.permissions.validate_document_access",
        "on_trash": "data_access.permissions.validate_document_access",
    }
    for doctype in _restricted_doctypes()
}


fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["module", "=", "Data Access"]],
    }
]
