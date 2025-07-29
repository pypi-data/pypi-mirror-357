# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Budget Plan Details - Purchase Request",
    "version": "18.0.1.1.3",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/ecosoft-odoo/budgeting",
    "depends": [
        "budget_plan_detail_purchase",
        "budget_control_purchase_request",
        "purchase_request_analytic_tag",
    ],
    "data": [
        "views/purchase_request_line_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_request_budget_move.xml",
    ],
    "installable": True,
    "auto_install": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "maintainers": ["Saran440"],
    "development_status": "Alpha",
}
