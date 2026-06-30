frappe.ui.form.on("Data Permission Dimension", {
    refresh(frm) {
        frm.add_custom_button(__("Discover Fields"), () => discover_fields(frm), __("Tools"));
    },

    source_doctype(frm) {
        if (!frm.doc.source_doctype) return;
        if ((frm.doc.target_doctypes || []).length) return;
        discover_fields(frm);
    },
});

async function discover_fields(frm) {
    if (!frm.doc.source_doctype) {
        frappe.msgprint(__("Select a Source DocType first."));
        return;
    }

    frappe.dom.freeze(__("Discovering fields..."));
    try {
        const response = await frappe.call({
            method: "data_access.permissions.discover_targets_for_source",
            args: {
                source_doctype: frm.doc.source_doctype,
            },
        });

        const targets = response.message || [];
        if (!targets.length) {
            frappe.msgprint(__("No Link fields found for this Source DocType."));
            return;
        }

        frm.clear_table("target_doctypes");
        targets.forEach((target) => {
            const row = frm.add_child("target_doctypes");
            row.target_doctype = target.target_doctype;
            row.field_name = target.field_name;
        });
        frm.refresh_field("target_doctypes");
        frm.dirty();

        frappe.show_alert({
            message: __("Discovered {0} fields.", [targets.length]),
            indicator: "green",
        });
    } finally {
        frappe.dom.unfreeze();
    }
}
