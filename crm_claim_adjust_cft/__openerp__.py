# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Adjustments to CRM Claim",
    "version": "8.0.1.0.0",
    "author": "Rooms For (Hong Kong) Limited",
    "website": "https://www.odoo-asia.com",
    "license": "AGPL-3",
    "description": """
    """,
    "category": "CRM",
    "depends": [
        'crm_claim',
        'sale',
    ],
    "data": [
        'views/crm_claim_views.xml',
        'views/crm_claim_menu.xml',
        'security/ir.model.access.csv',
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
