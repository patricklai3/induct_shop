frappe.provide("frappe.views.calendar");

frappe.views.calendar["Schedule Entry"] = {
	field_map: {
		start: "start",
		end: "end",
		id: "name",
		title: "title",
		allDay: "allDay",
		status: "status"
	},
	get_events_method: "induct_shop.api.scheduling_views.get_calendar_events",
	get_css_class: function (d) {
		const status = d.status || d.extendedProps?.status;
		if (status === "Scheduled") return "blue";
		if (status === "In Progress") return "orange";
		if (status === "Needs Review") return "red";
		if (status === "Completed") return "green";
		if (status === "Cancelled") return "gray";
		return "blue";
	},
	options: {
		editable: false,
		eventDidMount: function (info) {
			const event = info.event;
			const props = event.extendedProps || {};
			const $el = $(info.el);

			const status = props.status || event.title;
			const color_map = {
				"Scheduled": "#2b6cb0",
				"In Progress": "#d69e2e",
				"Needs Review": "#dc3545",
				"Completed": "#28a745",
				"Cancelled": "#6c757d",
				"Draft": "#718096"
			};
			const border_color = color_map[status] || "#2b6cb0";

			$el.css({
				"border-left": "5px solid " + border_color,
				"padding-left": "4px"
			});

			let badges_html = "";
			if (props.service_bay) {
				badges_html += `<span class="badge badge-secondary" style="margin-right: 4px; font-size: 10px;">${frappe.utils.escape_html(props.service_bay)}</span>`;
			}
			if (props.spans_lunch) {
				badges_html += `<span class="badge badge-warning" style="background-color: #feebc8; color: #744210; border: 1px solid #fbd38d; font-size: 10px;">🍱 Spans Lunch</span>`;
			}

			if (badges_html) {
				const title_el = $el.find(".fc-event-title, .fc-title");
				if (title_el.length) {
					title_el.append(`<div class="schedule-entry-badges" style="margin-top: 3px;">${badges_html}</div>`);
				} else {
					$el.append(`<div class="schedule-entry-badges" style="margin-top: 3px; padding: 2px;">${badges_html}</div>`);
				}
			}

			const tooltip_content = `
				<div class="schedule-entry-popover" style="text-align: left; padding: 4px; font-size: 12px;">
					<div style="font-weight: bold; margin-bottom: 4px;">${frappe.utils.escape_html(event.title || '')}</div>
					<div><b>Status:</b> ${frappe.utils.escape_html(props.status || '')}</div>
					<div><b>Service Bay:</b> ${frappe.utils.escape_html(props.service_bay || 'Unassigned')}</div>
					<div><b>Technician:</b> ${frappe.utils.escape_html(props.assigned_technician || 'Unassigned')}</div>
					<div><b>Duration:</b> ${props.estimated_duration || 0} min (P80)</div>
					${props.spans_lunch ? '<div style="color: #b7791f; font-weight: 500; margin-top: 2px;">🍱 Job spans lunch break</div>' : ''}
					${props.items_summary ? `<div style="margin-top: 4px; color: #4a5568;"><b>Services:</b> ${frappe.utils.escape_html(props.items_summary)}</div>` : ''}
				</div>
			`;

			if ($.fn.popover) {
				$el.popover({
					title: `<span style="font-weight: 600;">${frappe.utils.escape_html(event.id)}</span>`,
					content: tooltip_content,
					html: true,
					trigger: "hover",
					placement: "auto",
					container: "body"
				});
			} else {
				$el.attr("title", `${event.title} | ${props.status} | Bay: ${props.service_bay || 'Unassigned'}`);
			}
		}
	}
};
