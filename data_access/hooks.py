app_name = "data_access"
app_title = "Data Access Permissions"
app_publisher = "Your Company"
app_description = "Row-level data access permissions for Frappe/ERPNext"
app_version = "1.1.0"

after_install = "data_access.install.sync_data_access_types"
after_migrate = "data_access.install.sync_data_access_types"

add_to_apps_screen = [
    {
        "name": "data_access",
        "logo": "/assets/data_access/images/data-access.svg",
        "title": "Data Access Permissions",
        "route": "/app/data-access",
    }
]


def _restricted_doctypes() -> list[str]:
    from data_access.config.data_access_types import DATA_ACCESS_TYPES

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
