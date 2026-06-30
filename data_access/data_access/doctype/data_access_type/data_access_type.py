import frappe
from frappe import _
from frappe.model.document import Document

from data_access.permissions import clear_user_cache


class DataAccessType(Document):
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
            if row.target_doctype in seen:
                frappe.throw(_("Target DocType '{0}' is duplicated.").format(row.target_doctype))
            seen.add(row.target_doctype)
