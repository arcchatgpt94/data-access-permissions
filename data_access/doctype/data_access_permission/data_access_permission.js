frappe.ui.form.on("Data Access Permission", {
    async onload(frm) {
        frm.set_query("user", () => ({
            filters: { enabled: 1, user_type: "System User" },
        }));
        await load_access_type_options(frm);
    },

    access_type(frm) {
        if (frm.doc.access_type) {
            offer_load_all_values(frm);
        }
    },

    refresh(frm) {
        frm.add_custom_button(__("Load Values"), () => load_all_values(frm), __("Tools"));
        frm.add_custom_button(__("Allow All"), () => toggle_all(frm, true), __("Tools"));
        frm.add_custom_button(__("Deny All"), () => toggle_all(frm, false), __("Tools"));
    },
});

frappe.ui.form.on("Data Access Permission Detail", {
    can_view(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.can_view) {
            frappe.model.set_value(cdt, cdn, "can_add", 0);
            frappe.model.set_value(cdt, cdn, "can_edit", 0);
            frappe.model.set_value(cdt, cdn, "can_delete", 0);
        }
    },

    can_add(frm, cdt, cdn) {
        ensure_view_when_action_enabled(cdt, cdn, "can_add");
    },

    can_edit(frm, cdt, cdn) {
        ensure_view_when_action_enabled(cdt, cdn, "can_edit");
    },

    can_delete(frm, cdt, cdn) {
        ensure_view_when_action_enabled(cdt, cdn, "can_delete");
    },
});

async function load_access_type_options(frm) {
    const response = await frappe.call("data_access.permissions.get_data_access_types");
    if (!response.message) return;

    const options = response.message.map((item) => item.name);
    frm.set_df_property("access_type", "options", ["", ...options].join("\n"));
}

function offer_load_all_values(frm) {
    if ((frm.doc.permissions_table || []).length) return;

    frappe.confirm(
        __("Load all values for {0}?", [frm.doc.access_type]),
        () => load_all_values(frm)
    );
}

async function load_all_values(frm) {
    if (!frm.doc.access_type) {
        frappe.msgprint(__("Select an access type first."));
        return;
    }

    frappe.dom.freeze(__("Loading..."));
    try {
        const response = await frappe.call({
            doc: frm.doc,
            method: "load_all_values",
        });

        const values = response.message || [];
        if (!values.length) {
            frappe.msgprint(__("No values found for this access type."));
            return;
        }

        const existing = new Set(
            (frm.doc.permissions_table || []).map((row) => row.reference_value)
        );

        values.forEach((value) => {
            if (existing.has(value)) return;

            const row = frappe.model.add_child(
                frm.doc,
                "Data Access Permission Detail",
                "permissions_table"
            );
            frappe.model.set_value(row.doctype, row.name, "reference_value", value);
        });

        frm.refresh_field("permissions_table");
        frappe.show_alert({
            message: __("Loaded {0} values.", [values.length]),
            indicator: "green",
        });
    } finally {
        frappe.dom.unfreeze();
    }
}

function toggle_all(frm, checked) {
    (frm.doc.permissions_table || []).forEach((row) => {
        frappe.model.set_value(row.doctype, row.name, "can_view", checked ? 1 : 0);
        frappe.model.set_value(row.doctype, row.name, "can_add", checked ? 1 : 0);
        frappe.model.set_value(row.doctype, row.name, "can_edit", checked ? 1 : 0);
        frappe.model.set_value(row.doctype, row.name, "can_delete", checked ? 1 : 0);
    });
    frm.refresh_field("permissions_table");
}

function ensure_view_when_action_enabled(cdt, cdn, fieldname) {
    const row = locals[cdt][cdn];
    if (row[fieldname] && !row.can_view) {
        frappe.model.set_value(cdt, cdn, "can_view", 1);
    }
}
