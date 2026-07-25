/**
 * Sales Order Integration — Schedule Service Button & Polished Dialog (Stage 8)
 *
 * Adds a "Schedule Service" button to submitted Sales Orders.
 * Opens an interactive slot-picker dialog with:
 *   - Auto-detected equipment tags badge from SO items
 *   - Est. duration badge (P80)
 *   - Date navigation arrows (prev/next day)
 *   - Holiday awareness (prevents scheduling on holidays)
 *   - Full slot grid with clickable buttons & per-slot dual-resource counts
 *   - Dual-resource capacity bottleneck summary & lunch break indicator
 *   - Technician utilization preview
 *   - Overlap and leave warning banners
 *   - Auto bay assignment with required equipment tag match
 */
frappe.ui.form.on("Sales Order", {
	refresh: function (frm) {
		// Only show button on submitted SOs
		if (frm.doc.docstatus !== 1) return;

		// Check if an active Schedule Entry already exists for this SO
		frappe.db.count("Schedule Entry", {
			filters: {
				sales_order: frm.doc.name,
				docstatus: ["!=", 2],
			},
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
 * Fetches estimated duration and required equipment tags before rendering.
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

	// Fetch estimated duration and required equipment tags in parallel
	frappe.call({
		method: "induct_shop.api.estimation_service.get_total_estimate",
		args: { item_codes: JSON.stringify(item_operations) },
		callback: function (est_r) {
			const estimated_duration = est_r.message || 0;

			frappe.call({
				method: "induct_shop.api.scheduling.get_required_equipment_tags",
				args: { sales_order: frm.doc.name },
				callback: function (tag_r) {
					const required_tags = tag_r.message || [];
					show_schedule_dialog(frm, estimated_duration, required_tags);
				},
				error: function () {
					show_schedule_dialog(frm, estimated_duration, []);
				},
			});
		},
		error: function () {
			show_schedule_dialog(frm, 0, []);
		},
	});
}

/**
 * Renders the polished Schedule Service dialog.
 */
function show_schedule_dialog(frm, estimated_duration, required_tags) {
	const today = frappe.datetime.get_today();

	const d = new frappe.ui.Dialog({
		title: __("Schedule Service — {0}", [frm.doc.name]),
		size: "large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "badges_header",
				options: get_header_badges_html(estimated_duration, required_tags),
			},
			{
				fieldtype: "Section Break",
				fieldname: "section_date",
				label: __("Select Date & Slot"),
			},
			{
				fieldtype: "HTML",
				fieldname: "date_nav_html",
				options: get_date_nav_html(),
			},
			{
				fieldtype: "Date",
				fieldname: "scheduled_date",
				label: __("Date"),
				default: today,
				reqd: 1,
				change: function () {
					refresh_slots(d, estimated_duration);
					update_date_nav_display(d);
					check_technician_status(d, estimated_duration);
				},
			},
			{
				fieldtype: "HTML",
				fieldname: "slots_area",
				options:
					'<div class="schedule-slots-loading text-muted text-center" style="padding: 20px;">' +
					'<i class="fa fa-spinner fa-spin"></i> ' +
					__("Loading available slots...") +
					"</div>",
			},
			{
				fieldtype: "Section Break",
				fieldname: "section_assignment",
				label: __("Assignment & Notes"),
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
				change: function () {
					update_technician_preview(d);
					check_technician_status(d, estimated_duration);
				},
			},
			{
				fieldtype: "HTML",
				fieldname: "tech_preview_area",
				options: "",
			},
			{
				fieldtype: "HTML",
				fieldname: "tech_warning_area",
				options: "",
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

			// Step 1: Auto-assign bay with equipment tag matching
			frappe.call({
				method: "induct_shop.api.scheduling.auto_assign_bay",
				args: {
					date: values.scheduled_date,
					start_time: selected_slot,
					duration_minutes: estimated_duration,
					required_tags: JSON.stringify(d.required_tags || []),
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

	// Attach custom properties to dialog instance
	d.selected_slot = null;
	d.required_tags = required_tags || [];

	d.show();

	// Bind Date Navigation arrows click handlers
	bind_date_nav_events(d, estimated_duration);
	update_date_nav_display(d);

	// Auto-load slots for today
	refresh_slots(d, estimated_duration);
}

/**
 * Generates HTML for badges at the top of the dialog (Duration & Required Equipment).
 */
function get_header_badges_html(duration, required_tags) {
	let html = '<div style="margin-bottom: 15px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">';

	// Est. Duration badge
	if (duration) {
		const hours = Math.floor(duration / 60);
		const mins = duration % 60;
		const time_str = hours > 0 ? __("{0}h {1}m", [hours, mins]) : __("{0} min", [mins]);
		html +=
			'<span class="indicator-pill whitespace-nowrap blue">' +
			'<span>' + __("Est. Duration") + ': <strong>' + time_str + '</strong> (P80)</span>' +
			'</span>';
	} else {
		html += '<span class="text-muted">' + __("No estimation available") + '</span>';
	}

	// Required Equipment Tags badge
	if (required_tags && required_tags.length > 0) {
		const tag_str = required_tags.join(", ");
		html +=
			'<span class="indicator-pill whitespace-nowrap purple">' +
			'<span>' + __("Required Equipment") + ': <strong>' + frappe.utils.escape_html(tag_str) + '</strong></span>' +
			'</span>';
	}

	html += '</div>';
	return html;
}

/**
 * Returns HTML layout for Date Navigation controls (Prev/Next Day buttons).
 */
function get_date_nav_html() {
	return (
		'<div class="schedule-date-nav" style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">' +
		'<button type="button" class="btn btn-default btn-xs date-nav-prev"><i class="fa fa-chevron-left"></i> ' + __("Prev Day") + '</button>' +
		'<span class="date-nav-current-display font-weight-bold" style="font-size: var(--text-md);"></span>' +
		'<button type="button" class="btn btn-default btn-xs date-nav-next">' + __("Next Day") + ' <i class="fa fa-chevron-right"></i></button>' +
		'</div>'
	);
}

/**
 * Binds click events for Date Navigation prev/next buttons.
 */
function bind_date_nav_events(dialog, estimated_duration) {
	const nav_wrapper = dialog.fields_dict.date_nav_html.$wrapper;

	nav_wrapper.find(".date-nav-prev").on("click", function () {
		const current_date = dialog.get_value("scheduled_date") || frappe.datetime.get_today();
		const prev_date = frappe.datetime.add_days(current_date, -1);
		dialog.set_value("scheduled_date", prev_date);
	});

	nav_wrapper.find(".date-nav-next").on("click", function () {
		const current_date = dialog.get_value("scheduled_date") || frappe.datetime.get_today();
		const next_date = frappe.datetime.add_days(current_date, 1);
		dialog.set_value("scheduled_date", next_date);
	});
}

/**
 * Updates the text display in the date navigation header.
 */
function update_date_nav_display(dialog) {
	const date_val = dialog.get_value("scheduled_date");
	if (!date_val) return;
	const formatted = frappe.datetime.str_to_user(date_val);
	dialog.fields_dict.date_nav_html.$wrapper.find(".date-nav-current-display").text(formatted);
}

/**
 * Fetches available time slots for the selected date, checking holiday status first.
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

	// Reset selected slot on date change
	dialog.selected_slot = null;
	clear_technician_warning(dialog);

	// Check holiday status first
	frappe.call({
		method: "induct_shop.api.scheduling.is_holiday",
		args: { date: date },
		callback: function (hol_r) {
			const hol_info = hol_r.message;
			if (hol_info && hol_info.is_holiday) {
				const hol_desc = hol_info.description ? " (" + hol_info.description + ")" : "";
				slots_area.html(
					'<div class="alert alert-warning text-center" style="margin: 15px 0;">' +
					'<i class="fa fa-calendar-times-o"></i> <strong>' +
					__("{0} is a holiday{1}.", [frappe.datetime.str_to_user(date), hol_desc]) +
					'</strong><br>' + __("No service slots are available on this date.") +
					'</div>'
				);
				return;
			}

			// If not a holiday, fetch available slots
			frappe.call({
				method: "induct_shop.api.scheduling.get_available_slots",
				args: {
					date: date,
					duration_minutes: estimated_duration || 30,
					required_tags: JSON.stringify(dialog.required_tags || []),
				},
				callback: function (r) {
					const slots = r.message || [];
					render_slots(dialog, slots, date, estimated_duration);
				},
				error: function () {
					slots_area.html(
						'<div class="text-muted text-center" style="padding: 20px;">' +
						__("Error loading slots. Please try again.") +
						"</div>"
					);
				},
			});
		},
	});
}

/**
 * Renders slot buttons inside the dialog's slots_area with bottleneck summary and lunch notice.
 */
function render_slots(dialog, slots, date, estimated_duration) {
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
		'<div style="margin-bottom: 12px; color: var(--text-muted); font-size: var(--text-sm); display: flex; align-items: center; justify-content: space-between;">' +
		'<span><strong>' + total_slot_count + '</strong> ' + __("slots available on") + ' ' + frappe.datetime.str_to_user(date) + '</span>';
	if (primary_bottleneck) {
		summary_html +=
			'<span class="badge badge-subtle uppercase text-muted">' +
			__("Bottleneck") + ': ' + __(primary_bottleneck) +
			'</span>';
	}
	summary_html += '</div>';

	let buttons_html = '<div class="schedule-slot-grid" style="display: flex; flex-wrap: wrap; gap: 8px;">';

	slots.forEach((slot) => {
		const time_display = format_slot_time(slot.start_time);
		const bays_text = slot.available_bays != null ? slot.available_bays + " " + (slot.available_bays === 1 ? __("bay") : __("bays")) : "";
		const tech_text = slot.available_technicians != null ? slot.available_technicians + " " + (slot.available_technicians === 1 ? __("tech") : __("techs")) : "";

		let sub_info = "";
		if (bays_text) sub_info += bays_text;
		if (tech_text) sub_info += (sub_info ? " · " : "") + tech_text;

		buttons_html +=
			'<button type="button" class="btn btn-default btn-sm schedule-slot-btn" ' +
			'data-slot="' + slot.start_time + '" ' +
			'style="min-width: 100px; padding: 8px 12px; text-align: center; border-radius: 6px;">' +
			'<div style="font-weight: 600; font-size: var(--text-md);">' + time_display + '</div>' +
			'<div style="font-size: var(--text-xs); color: var(--text-muted);">' + sub_info + '</div>' +
			'</button>';
	});

	buttons_html += '</div>';

	// Lunch break note
	buttons_html +=
		'<div style="margin-top: 10px; font-size: var(--text-xs); color: var(--text-light); font-style: italic;">' +
		'<i class="fa fa-info-circle"></i> ' + __("(12:00–12:30 lunch break excluded)") +
		'</div>';

	slots_area.html(summary_html + buttons_html);

	// Bind click handlers
	slots_area.find(".schedule-slot-btn").on("click", function () {
		slots_area.find(".schedule-slot-btn").removeClass("btn-primary").addClass("btn-default");
		$(this).removeClass("btn-default").addClass("btn-primary");
		dialog.selected_slot = $(this).data("slot");

		// Check warning for selected technician if set
		check_technician_status(dialog, estimated_duration);
	});
}

/**
 * Updates the technician utilization preview text.
 */
function update_technician_preview(dialog) {
	const emp = dialog.get_value("assigned_technician");
	const date = dialog.get_value("scheduled_date");
	const preview_wrapper = dialog.fields_dict.tech_preview_area.$wrapper;

	if (!emp || !date) {
		preview_wrapper.html("");
		return;
	}

	frappe.call({
		method: "induct_shop.api.technician_availability.get_technician_queue",
		args: { employee: emp, date: date },
		callback: function (r) {
			const info = r.message;
			if (!info) {
				preview_wrapper.html("");
				return;
			}

			const name = info.employee_name || emp;
			const jobs = info.total_jobs || 0;
			const total_min = info.total_minutes || 0;
			const util = info.utilization_pct || 0;

			const hours = Math.floor(total_min / 60);
			const mins = total_min % 60;
			const time_str = hours > 0 ? __("{0}h {1}m", [hours, mins]) : __("{0}m", [mins]);

			preview_wrapper.html(
				'<div style="font-size: var(--text-xs); color: var(--text-muted); margin-top: 6px;">' +
				'<i class="fa fa-user-circle"></i> <strong>' + frappe.utils.escape_html(name) + '</strong> · ' +
				jobs + ' ' + (jobs === 1 ? __("job") : __("jobs")) + ' · ' +
				time_str + ' · ' +
				util + '% ' + __("utilized") +
				'</div>'
			);
		},
	});
}

/**
 * Checks for technician availability issues (leave or overlap) and updates warning banner.
 */
function check_technician_status(dialog, estimated_duration) {
	const emp = dialog.get_value("assigned_technician");
	const date = dialog.get_value("scheduled_date");
	const slot = dialog.selected_slot;

	if (!emp || !date || !slot) {
		clear_technician_warning(dialog);
		return;
	}

	frappe.call({
		method: "induct_shop.api.technician_availability.check_technician_availability",
		args: {
			employee: emp,
			date: date,
			start_time: slot,
			duration_minutes: estimated_duration || 30,
		},
		callback: function (r) {
			const res = r.message;
			const warning_wrapper = dialog.fields_dict.tech_warning_area.$wrapper;

			if (!res) {
				clear_technician_warning(dialog);
				return;
			}

			if (res.on_leave) {
				warning_wrapper.html(
					'<div class="alert alert-danger" style="margin-top: 10px; margin-bottom: 0; padding: 8px 12px; font-size: var(--text-xs);">' +
					'<i class="fa fa-exclamation-triangle"></i> <strong>' + __("Warning") + ':</strong> ' +
					__("Selected technician is on approved leave on this date.") +
					'</div>'
				);
			} else if (res.reason === "overlap" || (res.conflicts && res.conflicts.length > 0)) {
				const slot_formatted = format_slot_time(slot);
				warning_wrapper.html(
					'<div class="alert alert-warning" style="margin-top: 10px; margin-bottom: 0; padding: 8px 12px; font-size: var(--text-xs);">' +
					'<i class="fa fa-exclamation-triangle"></i> <strong>' + __("Warning") + ':</strong> ' +
					__("Selected technician has an overlapping assignment at {0}.", [slot_formatted]) +
					'</div>'
				);
			} else {
				clear_technician_warning(dialog);
			}
		},
	});
}

function clear_technician_warning(dialog) {
	if (dialog.fields_dict && dialog.fields_dict.tech_warning_area) {
		dialog.fields_dict.tech_warning_area.$wrapper.html("");
	}
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
