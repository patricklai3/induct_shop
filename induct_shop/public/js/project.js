frappe.ui.form.on('Project', {
	refresh: function(frm) {
		frm.set_df_property('monitor_progress_tab', 'hidden', 1);
	}
});
