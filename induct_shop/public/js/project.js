frappe.ui.form.on('Project', {
	setup: function(frm) {
		frm.set_df_property('monitor_progress_tab', 'hidden', 1);
		const progress_fields = ['collect_progress', 'holiday_list', 'frequency', 'from_time', 'to_time', 'first_email', 'second_email', 'daily_time_to_send', 'day_to_send', 'weekly_time_to_send', 'message', 'subject'];
		progress_fields.forEach(f => frm.set_df_property(f, 'hidden', 1));
	},
	refresh: function(frm) {
		frm.set_df_property('monitor_progress_tab', 'hidden', 1);
		frm.toggle_display('monitor_progress_tab', false);
		const progress_fields = ['collect_progress', 'holiday_list', 'frequency', 'from_time', 'to_time', 'first_email', 'second_email', 'daily_time_to_send', 'day_to_send', 'weekly_time_to_send', 'message', 'subject'];
		progress_fields.forEach(f => {
			frm.set_df_property(f, 'hidden', 1);
			frm.toggle_display(f, false);
		});
	}
});
