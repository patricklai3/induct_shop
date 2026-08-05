frappe.ui.form.on('Schedule Entry', {
	refresh(frm) {
		frm.trigger('setup_field_visibility');
		frm.trigger('setup_buttons');
	},

	entry_type(frm) {
		frm.trigger('setup_field_visibility');
	},

	customer(frm) {
		frm.trigger('setup_field_visibility');
	},

	repair_vehicle(frm) {
		frm.trigger('setup_field_visibility');
	},

	sales_order(frm) {
		frm.trigger('setup_field_visibility');
	},

	setup_field_visibility(frm) {
		if (frm.doc.entry_type) {
			frappe.db.get_value('Schedule Entry Type', frm.doc.entry_type, 'requires_sales_order', (r) => {
				const reqd_so = r && r.requires_sales_order;
				frm.toggle_display('sales_order', Boolean(frm.doc.sales_order || reqd_so));
			});
		} else {
			frm.toggle_display('sales_order', Boolean(frm.doc.sales_order));
		}

		frm.toggle_display('provisional_customer_name', !frm.doc.customer || Boolean(frm.doc.provisional_customer_name));
		frm.toggle_display('provisional_vehicle_info', !frm.doc.repair_vehicle || Boolean(frm.doc.provisional_vehicle_info));
		frm.toggle_display('project', Boolean(frm.doc.project));
		frm.toggle_display('vehicle_check_in', Boolean(frm.doc.vehicle_check_in));
	},

	setup_buttons(frm) {
		if (!frm.is_new() && frm.doc.status === 'Scheduled' && !frm.doc.vehicle_check_in) {
			frm.add_custom_button(__('Vehicle Check-in'), function () {
				frappe.route_options = {
					schedule_entry: frm.doc.name,
					customer: frm.doc.customer || '',
					vehicle: frm.doc.repair_vehicle || ''
				};
				frappe.new_doc('Vehicle Check-in');
			}).addClass('btn-primary');
		}
	}
});
