# -*- coding: utf-8 -*-
# Copyright 2016-2017 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale View Adjust CFT",
    "version": "8.0.1.4.0",
    "author": "Ecosoft Co. Ltd.",
    "license": "AGPL-3",
    "description": """
    """,
    "category": "Sales",
    "depends": [
        'crm',
        'model_security_adjust_cft',
        'sale',
        'sale_partner_with_sales',
        'account',
    ],
    "data": [
        'security/crm_security.xml',
        'security/partner_security.xml',
        'data/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/crm_phonecall_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
    ],
    "js": [
    ],
    "css": [
    ],
    "auto_install": False,
    "installable": True,
    "external_dependencies": {
        'python': [],
    },
}
