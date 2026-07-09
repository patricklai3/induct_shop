frappe.ui.form.on('Quotation', {
	setup: function(frm) {
		// If the form is opened with a project already set (e.g. from dashboard)
		if (frm.is_new() && frm.doc.project && !frm.doc.party_name) {
			frm.trigger('project');
		}
	},
	project: function(frm) {
		if (frm.doc.project && !frm.doc.party_name) {
			frappe.db.get_value('Project', frm.doc.project, 'customer', function(r) {
				if (r && r.customer) {
					frm.set_value('quotation_to', 'Customer');
					frm.set_value('party_name', r.customer);
				}
			});
		}
	}
});
