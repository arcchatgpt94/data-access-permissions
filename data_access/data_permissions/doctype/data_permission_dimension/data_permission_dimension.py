import frappe
from frappe import _
from frappe.model.document import Document

from data_access.permissions import clear_user_cache


class DataPermissionDimension(Document):
    def validate(self):
        self._validate_targets()

    def on_update(self):
        clear_user_cache()

    def on_trash(self):
        clear_user_cache()

    def _validate_targets(self):
        if not self.target_doctypes:
            frappe.throw(_("Add at least one target DocType."))

        seen = set()
        for row in self.target_doctypes:
            key = (row.target_doctype, row.field_name)
            if key in seen:
                frappe.throw(
                    _("Target '{0}.{1}' is duplicated.").format(
                        row.target_doctype,
                        row.field_name,
                    )
                )
            seen.add(key)
