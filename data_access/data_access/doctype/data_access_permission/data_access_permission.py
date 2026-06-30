import frappe
from frappe import _
from frappe.model.document import Document

from data_access.config.data_access_types import get_all_names, get_type_by_name
from data_access.permissions import clear_user_cache


class DataAccessPermission(Document):
    def validate(self):
        self._validate_user_or_group()
        self._validate_access_type()
        self._validate_permission_rows()
        self._check_duplicate()

    def on_update(self):
        self._clear_cache()

    def on_trash(self):
        self._clear_cache()

    def _validate_user_or_group(self):
        if not self.user and not self.user_group:
            frappe.throw(_("Select either a user or a user group."))

        if self.user and self.user_group:
            frappe.throw(_("Select a user or a user group, not both."))

    def _validate_access_type(self):
        valid_types = get_all_names()
        if self.access_type not in valid_types:
            frappe.throw(
                _("Unsupported access type '{0}'. Available types: {1}").format(
                    self.access_type,
                    ", ".join(valid_types),
                )
            )

    def _validate_permission_rows(self):
        for row in self.permissions_table or []:
            if not row.can_view and (row.can_add or row.can_edit or row.can_delete):
                frappe.throw(
                    _("Row '{0}' must allow View before Add, Edit, or Delete.").format(
                        row.reference_value
                    )
                )

    def _check_duplicate(self):
        filters = {
            "access_type": self.access_type,
            "name": ["!=", self.name],
        }

        if self.user:
            filters["user"] = self.user
        else:
            filters["user_group"] = self.user_group

        existing = frappe.db.exists("Data Access Permission", filters)
        if existing:
            frappe.throw(
                _("Duplicate Data Access Permission exists: {0}").format(existing)
            )

    def _clear_cache(self):
        if self.user:
            clear_user_cache(self.user)
        else:
            clear_user_cache()

    @frappe.whitelist()
    def load_all_values(self):
        type_config = get_type_by_name(self.access_type)
        if not type_config:
            return []

        records = frappe.get_all(
            type_config["doctype"],
            fields=["name"],
            order_by="name asc",
        )
        return [record["name"] for record in records]
