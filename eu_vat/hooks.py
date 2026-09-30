app_name = "eu_vat"
app_title = "EU-VAT check"
app_publisher = "pia diagnostika"
app_description = "Check in VIES if VAT is valid"
app_email = "piadiagnostika@gmail.com"
app_license = "GPLv3"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "eu_vat",
# 		"logo": "/assets/eu_vat/logo.png",
# 		"title": "EU-VAT check",
# 		"route": "/eu_vat",
# 		"has_permission": "eu_vat.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/eu_vat/css/eu_vat.css"
# app_include_js = "/assets/eu_vat/js/eu_vat.js"

# include js, css files in header of web template
# web_include_css = "/assets/eu_vat/css/eu_vat.css"
# web_include_js = "/assets/eu_vat/js/eu_vat.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "eu_vat/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "eu_vat/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

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
# 	"methods": "eu_vat.utils.jinja_methods",
# 	"filters": "eu_vat.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "eu_vat.install.before_install"
# after_install = "eu_vat.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "eu_vat.uninstall.before_uninstall"
# after_uninstall = "eu_vat.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "eu_vat.utils.before_app_install"
# after_app_install = "eu_vat.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "eu_vat.utils.before_app_uninstall"
# after_app_uninstall = "eu_vat.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "eu_vat.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "eu_vat.notifications.get_notification_config"

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


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"eu_vat.tasks.all"
# 	],
# 	"daily": [
# 		"eu_vat.tasks.daily"
# 	],
# 	"hourly": [
# 		"eu_vat.tasks.hourly"
# 	],
# 	"weekly": [
# 		"eu_vat.tasks.weekly"
# 	],
# 	"monthly": [
# 		"eu_vat.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "eu_vat.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "eu_vat.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "eu_vat.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "eu_vat.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["eu_vat.utils.before_request"]
# after_request = ["eu_vat.utils.after_request"]

# Job Events
# ----------
# before_job = ["eu_vat.utils.before_job"]
# after_job = ["eu_vat.utils.after_job"]

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
# 	"eu_vat.auth.validate"
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

doc_events = {
    "Customer": {
        "validate": "eu_vat.utils.vat_validation.validate_eu_vat"
    },
    "Supplier": {
        "validate": "eu_vat.utils.vat_validation.validate_eu_vat"
    },
    "Sales Invoice": {
        "validate": "eu_vat.api.validate_eu_vat"
    }
}
after_install = "eu_vat.install.after_install"
# Automatically load custom form client scripts for Customer and Supplier
doctype_js = {
    "Customer": "public/js/customer.js",
    "Supplier": "public/js/supplier.js"
}

# Export custom fields automatically during bench migrate
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["module", "=", "EU-VAT check"]
        ]
    }
]
