frappe.listview_settings["Schedule Entry"] = {
	add_fields: [
		"scheduled_date",
		"scheduled_time",
		"estimated_duration",
		"service_bay",
		"assigned_technician",
		"customer",
		"repair_vehicle",
		"status"
	],

	get_indicator: function (doc) {
		const status_colors = {
			"Scheduled": "blue",
			"In Progress": "orange",
			"Needs Review": "red",
			"Completed": "green",
			"Cancelled": "gray",
			"Draft": "gray"
		};
		const color = status_colors[doc.status] || "gray";
		return [__(doc.status), color, `status,=,${doc.status}`];
	},

	formatters: {
		service_bay: function (val) {
			if (!val) {
				return `<span class="text-muted" style="font-style: italic;">${__("Unassigned")}</span>`;
			}
			return `<span class="badge badge-secondary" style="font-weight: 500; padding: 3px 7px;">${frappe.utils.escape_html(val)}</span>`;
		},

		assigned_technician: function (val) {
			if (!val) {
				return `<span class="badge badge-warning" style="background-color: #feebc8; color: #744210; border: 1px solid #fbd38d; font-weight: 500; padding: 3px 7px;">${__("Unassigned")}</span>`;
			}
			return `<span class="badge badge-info" style="background-color: #ebf8ff; color: #2b6cb0; border: 1px solid #bee3f8; font-weight: 500; padding: 3px 7px;">${frappe.utils.escape_html(val)}</span>`;
		},

		estimated_duration: function (val) {
			if (val === null || val === undefined) return "";
			return `<span style="font-family: monospace; font-size: 11px;">${val} min (P80)</span>`;
		}
	},

	onload: function (listview) {
		const group_name = __("Quick Filters");

		const apply_filter = function (filters) {
			listview.filter_area.clear().then(() => {
				if (filters && filters.length) {
					listview.filter_area.add(filters);
				} else {
					listview.refresh();
				}
			});
		};

		listview.page.add_inner_button(__("All Entries"), function () {
			apply_filter([]);
		}, group_name);

		listview.page.add_inner_button(__("Today's Jobs"), function () {
			apply_filter([
				["Schedule Entry", "scheduled_date", "=", frappe.datetime.get_today()]
			]);
		}, group_name);

		listview.page.add_inner_button(__("Needs Review"), function () {
			apply_filter([
				["Schedule Entry", "status", "=", "Needs Review"]
			]);
		}, group_name);

		listview.page.add_inner_button(__("Unassigned Tech"), function () {
			apply_filter([
				["Schedule Entry", "assigned_technician", "is", "not set"]
			]);
		}, group_name);

		listview.page.add_inner_button(__("In Progress"), function () {
			apply_filter([
				["Schedule Entry", "status", "=", "In Progress"]
			]);
		}, group_name);
	}
};
