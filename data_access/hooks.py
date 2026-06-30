app_name = "data_access"
app_title = "Data Permissions"
app_publisher = "Your Company"
app_description = "Row-level data access permissions for Frappe/ERPNext"
app_version = "1.1.0"

after_install = "data_access.install.sync_data_permission_dimensions"
after_migrate = "data_access.install.sync_data_permission_dimensions"

add_to_apps_screen = [
    {
        "name": "data_access",
        "logo": "/assets/data_access/images/data-access.svg",
        "title": "Data Permissions",
        "route": "/app/data-permissions",
    }
]


def _restricted_doctypes() -> list[str]:
    from data_access.config.data_permission_dimensions import (
        DATA_PERMISSION_DIMENSIONS,
        get_configured_dimensions,
    )

    doctypes = set()
    try:
        dimensions = get_configured_dimensions(enabled_only=True)
    except Exception:
        dimensions = DATA_PERMISSION_DIMENSIONS

    for dimension in dimensions:
        doctypes.update(dimension.get("apply_to", []))
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
        "filters": [["module", "=", "Data Permissions"]],
    }
]
