app_name = "induct_shop"
app_title = "Induct Shop"
app_publisher = "Induct"
app_description = "Shop Management System"
app_email = "admin@example.com"
app_license = "mit"

fixtures = ["Custom Field", "Property Setter"]

app_home = "/desk/shop-floor"

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "induct_shop",
		"logo": "/assets/induct_shop/images/induct-shop-logo.svg",
		"title": "Induct Shop",
		"route": "/desk/shop-floor",
		"has_permission": "induct_shop.utilities.permission.check_app_permission"
	}
]


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/induct_shop/css/induct_shop.css"
# app_include_js = "/assets/induct_shop/js/induct_shop.js"

# include js, css files in header of web template
# web_include_css = "/assets/induct_shop/css/induct_shop.css"
# web_include_js = "/assets/induct_shop/js/induct_shop.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "induct_shop/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Project": "public/js/project.js",
    "Quotation": [
        "public/js/service_parts_selector.bundle.js",
        "public/js/quotation.js"
    ],
    "Sales Order": [
        "public/js/service_parts_selector.bundle.js",
        "public/js/sales_order.js"
    ],
    "Sales Invoice": "public/js/service_parts_selector.bundle.js",
    "Purchase Receipt": "public/js/service_parts_selector.bundle.js",
    "Stock Entry": "public/js/service_parts_selector.bundle.js"
}
doctype_calendar_js = {
    "Schedule Entry": "public/js/schedule_entry_calendar.js"
}

doctype_list_js = {
    "Schedule Entry": "public/js/schedule_entry_list.js"
}


# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "induct_shop/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

website_route_rules = [
	{"from_route": "/frontend/<path:app_path>", "to_route": "frontend"},
	{"from_route": "/frontend", "to_route": "frontend"},
]

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "induct_shop.utils.jinja_methods",
# 	"filters": "induct_shop.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "induct_shop.install.before_install"
after_install = "induct_shop.install.after_install"

# Uninstallation
# ------------

before_uninstall = "induct_shop.uninstall.before_uninstall"
# after_uninstall = "induct_shop.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "induct_shop.utils.before_app_install"
# after_app_install = "induct_shop.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "induct_shop.utils.before_app_uninstall"
# after_app_uninstall = "induct_shop.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "induct_shop.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "induct_shop.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Delivery Note": {
		"on_submit": "induct_shop.induct_shop.overrides.project.update_project_costing",
		"on_cancel": "induct_shop.induct_shop.overrides.project.update_project_costing"
	},
	"Sales Invoice": {
		"validate": "induct_shop.api.service_parts_selector.auto_assign_parent_services",
		"on_submit": [
			"induct_shop.induct_shop.overrides.project.update_project_costing",
			"induct_shop.api.service_parts_selector.update_associations"
		],
		"on_cancel": "induct_shop.induct_shop.overrides.project.update_project_costing"
	},
	"Stock Entry": {
		"on_submit": "induct_shop.induct_shop.overrides.project.update_project_costing",
		"on_cancel": "induct_shop.induct_shop.overrides.project.update_project_costing"
	},
	"Quotation": {
		"validate": "induct_shop.api.service_parts_selector.auto_assign_parent_services",
		"on_submit": "induct_shop.api.service_parts_selector.update_associations"
	},
	"Sales Order": {
		"validate": "induct_shop.api.service_parts_selector.auto_assign_parent_services",
		"on_submit": [
			"induct_shop.api.service_parts_selector.update_associations",
			"induct_shop.api.sales_order_hooks.handle_amendment"
		]
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"induct_shop.tasks.all"
# 	],
# 	"daily": [
# 		"induct_shop.tasks.daily"
# 	],
# 	"hourly": [
# 		"induct_shop.tasks.hourly"
# 	],
# 	"weekly": [
# 		"induct_shop.tasks.weekly"
# 	],
# 	"monthly": [
# 		"induct_shop.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "induct_shop.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "induct_shop.custom.task.CustomTaskMixin"
# }

override_doctype_class = {
	"Project": "induct_shop.induct_shop.overrides.project.CustomProject"
}

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "induct_shop.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Project": "induct_shop.induct_shop.overrides.project_dashboard.override_dashboard"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["induct_shop.utils.before_request"]
# after_request = ["induct_shop.utils.after_request"]

# Job Events
# ----------
# before_job = ["induct_shop.utils.before_job"]
# after_job = ["induct_shop.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"induct_shop.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

