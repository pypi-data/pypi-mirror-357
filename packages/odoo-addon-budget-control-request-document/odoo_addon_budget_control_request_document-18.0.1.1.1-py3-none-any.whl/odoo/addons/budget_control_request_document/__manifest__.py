# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Budget Control on Request Document",
    "version": "18.0.1.1.1",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/ecosoft-odoo/budgeting",
    "depends": ["budget_control", "request_document"],
    "data": [
        "security/ir.model.access.csv",
        "views/budget_period_view.xml",
        "views/budget_control_view.xml",
        "views/request_order_view.xml",
        "views/request_document_view.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
    "development_status": "Alpha",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
