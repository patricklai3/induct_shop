/**
 * Sales Order Integration — Schedule Service Button & Dialog
 *
 * Adds a "Schedule Service" button to submitted Sales Orders.
 * The button opens a slot-picker dialog that creates a Schedule Entry.
 *
 * Stage 7 (basic dialog). Stage 8 will add:
 *   - Full slot grid with clickable buttons + dual-resource indicators
 *   - Date navigation arrows
 *   - Technician utilization preview
 *   - Overlap warning banners
 *   - Holiday awareness
 *   - Equipment tag auto-detection from SO items (deferred from Stage 7)
 */
frappe.ui.form.on("Sales Order", {
	refresh: function (frm) {
		// Only show button on submitted SOs
		if (frm.doc.docstatus !== 1) return;

		// Check if a Schedule Entry already exists for this SO
		frappe.db.count("Schedule Entry", {
			sales_order: frm.doc.name,
		}).then((count) => {
			if (count === 0) {
				frm.add_custom_button(
					__("Schedule Service"),
					function () {
						open_schedule_dialog(frm);
					},
					__("Actions")
				);
			}
		});
	},
});

/**
 * Opens the Schedule Service dialog for a submitted Sales Order.
 * Fetches estimated duration, loads available slots, and creates a Schedule Entry on submit.
 */
function open_schedule_dialog(frm) {
	// Collect item codes from SO for estimation
	const item_operations = [];
	(frm.doc.items || []).forEach((item) => {
		if (!item.item_code) return;
		const op = { item_code: item.item_code };
		if (item.custom_frt) {
			op.flat_rate_hours = item.custom_frt;
		} else if (item.qty) {
			const uom = (item.uom || item.stock_uom || "").toLowerCase();
			const is_hour_uom = ["hour", "hours", "hr", "hrs"].includes(uom);
			if (is_hour_uom) {
				op.flat_rate_hours = item.qty;
			}
		}
		item_operations.push(op);
	});

	// Fetch estimated duration first
	frappe.call({
		method: "induct_shop.api.estimation_service.get_total_estimate",
		args: { item_codes: JSON.stringify(item_operations) },
		callback: function (r) {
			const estimated_duration = r.message || 0;
			show_schedule_dialog(frm, estimated_duration);
		},
		error: function () {
			// Fall back to 0 if estimation fails
			show_schedule_dialog(frm, 0);
		},
	});
}

/**
 * Renders the Schedule Service dialog with date picker, slots, technician selector, and notes.
 */
function show_schedule_dialog(frm, estimated_duration) {
	const today = frappe.datetime.get_today();

	const d = new frappe.ui.Dialog({
		title: __("Schedule Service — {0}", [frm.doc.name]),
		size: "large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "duration_badge",
				options: get_duration_badge_html(estimated_duration),
			},
			{
				fieldtype: "Date",
				fieldname: "scheduled_date",
				label: __("Date"),
				default: today,
				reqd: 1,
				change: function () {
					refresh_slots(d, estimated_duration);
				},
			},
			{
				fieldtype: "HTML",
				fieldname: "slots_area",
				options: '<div class="schedule-slots-loading text-muted text-center" style="padding: 20px;">' + __("Select a date to view available slots") + "</div>",
			},
			{
				fieldtype: "Section Break",
				fieldname: "section_options",
			},
			{
				fieldtype: "Link",
				fieldname: "assigned_technician",
				label: __("Technician (Optional)"),
				options: "Employee",
				get_query: function () {
					return {
						filters: {
							status: "Active",
							designation: frappe.boot.sysdefaults
								? frappe.boot.sysdefaults.technician_designation || "Technician"
								: "Technician",
						},
					};
				},
			},
			{
				fieldtype: "Column Break",
			},
			{
				fieldtype: "Small Text",
				fieldname: "notes",
				label: __("Notes"),
			},
		],
		primary_action_label: __("Schedule"),
		primary_action: function (values) {
			const selected_slot = d.selected_slot;
			if (!selected_slot) {
				frappe.msgprint(__("Please select a time slot."));
				return;
			}
			if (!values.scheduled_date) {
				frappe.msgprint(__("Please select a date."));
				return;
			}

			d.disable_primary_action();

			// Step 1: Auto-assign bay via backend
			frappe.call({
				method: "induct_shop.api.scheduling.auto_assign_bay",
				args: {
					date: values.scheduled_date,
					start_time: selected_slot,
					duration_minutes: estimated_duration,
					// required_tags: null — deferred to Stage 8 (equipment tag auto-detection)
				},
				callback: function (bay_r) {
					const bay_name = bay_r.message;
					if (!bay_name) {
						frappe.msgprint(__("No available bay found for the selected slot."));
						d.enable_primary_action();
						return;
					}

					// Step 2: Create Schedule Entry
					frappe.call({
						method: "frappe.client.insert",
						args: {
							doc: {
								doctype: "Schedule Entry",
								sales_order: frm.doc.name,
								scheduled_date: values.scheduled_date,
								scheduled_time: selected_slot,
								service_bay: bay_name,
								assigned_technician: values.assigned_technician || "",
								notes: values.notes || "",
								status: "Scheduled",
							},
						},
						callback: function (se_r) {
							if (se_r.message) {
								d.hide();
								frappe.show_alert({
									message: __("Schedule Entry {0} created.", [
										se_r.message.name,
									]),
									indicator: "green",
								});
								frappe.set_route(
									"Form",
									"Schedule Entry",
									se_r.message.name
								);
							}
						},
						error: function () {
							d.enable_primary_action();
						},
					});
				},
				error: function () {
					d.enable_primary_action();
				},
			});
		},
	});

	// Track selected slot on the dialog instance
	d.selected_slot = null;

	d.show();

	// Auto-load slots for today
	refresh_slots(d, estimated_duration);
}

/**
 * Returns HTML for the estimated duration badge displayed at the top of the dialog.
 */
function get_duration_badge_html(duration) {
	if (!duration) {
		return '<div class="text-muted" style="margin-bottom: 10px;">' + __("No estimation available for this Sales Order.") + "</div>";
	}
	const hours = Math.floor(duration / 60);
	const mins = duration % 60;
	const time_str = hours > 0 ? __("{0}h {1}m", [hours, mins]) : __("{0} min", [mins]);

	return (
		'<div style="margin-bottom: 15px;">' +
		'<span class="indicator-pill whitespace-nowrap blue">' +
		'<span>' + __("Est. Duration") + ': <strong>' + time_str + '</strong> (P80)' + '</span>' +
		'</span>' +
		'</div>'
	);
}

/**
 * Fetches available time slots for the selected date and renders them in the dialog.
 */
function refresh_slots(dialog, estimated_duration) {
	const date = dialog.get_value("scheduled_date");
	if (!date) return;

	const slots_area = dialog.fields_dict.slots_area.$wrapper;
	slots_area.html(
		'<div class="text-muted text-center" style="padding: 20px;">' +
		'<i class="fa fa-spinner fa-spin"></i> ' + __("Loading available slots...") +
		"</div>"
	);

	// Reset selected slot
	dialog.selected_slot = null;

	frappe.call({
		method: "induct_shop.api.scheduling.get_available_slots",
		args: {
			date: date,
			duration_minutes: estimated_duration || 30,
			// required_tags: null — deferred to Stage 8
		},
		callback: function (r) {
			const slots = r.message || [];
			render_slots(dialog, slots, date);
		},
		error: function () {
			slots_area.html(
				'<div class="text-muted text-center" style="padding: 20px;">' +
				__("Error loading slots. Please try again.") +
				"</div>"
			);
		},
	});
}

/**
 * Renders slot buttons inside the dialog's slots_area.
 * Each button shows the start time, available bays, and available technicians.
 */
function render_slots(dialog, slots, date) {
	const slots_area = dialog.fields_dict.slots_area.$wrapper;

	if (!slots.length) {
		slots_area.html(
			'<div class="text-muted text-center" style="padding: 20px;">' +
			__("No available slots on {0}.", [frappe.datetime.str_to_user(date)]) +
			"</div>"
		);
		return;
	}

	// Determine overall bottleneck for summary text
	let total_slot_count = slots.length;
	let bottleneck_counts = { technicians: 0, bays: 0 };
	slots.forEach((s) => {
		if (s.bottleneck) bottleneck_counts[s.bottleneck]++;
	});
	let primary_bottleneck = null;
	if (bottleneck_counts.technicians > bottleneck_counts.bays && bottleneck_counts.technicians > 0) {
		primary_bottleneck = "Technicians";
	} else if (bottleneck_counts.bays > 0) {
		primary_bottleneck = "Bays";
	}

	let summary_html =
		'<div style="margin-bottom: 12px; color: var(--text-muted); font-size: var(--text-sm);">' +
		total_slot_count + " " + __("slots available on") + " " + frappe.datetime.str_to_user(date);
	if (primary_bottleneck) {
		summary_html += " · " + __("Bottleneck") + ": " + __(primary_bottleneck);
	}
	summary_html += "</div>";

	let buttons_html = '<div class="schedule-slot-grid" style="display: flex; flex-wrap: wrap; gap: 8px;">';

	slots.forEach((slot) => {
		const time_display = format_slot_time(slot.start_time);
		const bays_text = slot.available_bays != null ? slot.available_bays + " " + (slot.available_bays === 1 ? __("bay") : __("bays")) : "";
		const tech_text = slot.available_technicians != null ? slot.available_technicians + " " + (slot.available_technicians === 1 ? __("tech") : __("techs")) : "";

		let sub_info = "";
		if (bays_text) sub_info += bays_text;
		if (tech_text) sub_info += (sub_info ? " · " : "") + tech_text;

		buttons_html +=
			'<button class="btn btn-default btn-sm schedule-slot-btn" ' +
			'data-slot="' + slot.start_time + '" ' +
			'style="min-width: 100px; padding: 8px 12px; text-align: center; border-radius: 6px;">' +
			'<div style="font-weight: 600; font-size: var(--text-md);">' + time_display + "</div>" +
			'<div style="font-size: var(--text-xs); color: var(--text-muted);">' + sub_info + "</div>" +
			"</button>";
	});

	buttons_html += "</div>";

	// Lunch break note
	buttons_html +=
		'<div style="margin-top: 10px; font-size: var(--text-xs); color: var(--text-light);">' +
		__("Lunch break slots are excluded.") +
		"</div>";

	slots_area.html(summary_html + buttons_html);

	// Bind click handlers
	slots_area.find(".schedule-slot-btn").on("click", function () {
		slots_area.find(".schedule-slot-btn").removeClass("btn-primary").addClass("btn-default");
		$(this).removeClass("btn-default").addClass("btn-primary");
		dialog.selected_slot = $(this).data("slot");
	});
}

/**
 * Formats a time string (HH:MM) into user-friendly display (e.g., "8:00 AM").
 */
function format_slot_time(time_str) {
	if (!time_str) return "";
	const parts = time_str.split(":");
	let hours = parseInt(parts[0], 10);
	const minutes = parts[1] || "00";
	const ampm = hours >= 12 ? "PM" : "AM";
	if (hours === 0) hours = 12;
	else if (hours > 12) hours -= 12;
	return hours + ":" + minutes + " " + ampm;
}
