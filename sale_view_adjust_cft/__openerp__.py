# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale View Adjust CFT",
    "version": "8.0.0.8.0",
    "author": "Ecosoft Co. Ltd.",
    "license": "AGPL-3",
    "description": """
    """,
    "category": "Sales",
    "depends": [
        'crm',
    ],
    "data": [
        'security/crm_security.xml',
        'views/crm_lead_view.xml',
        'views/crm_phonecall_view.xml',
        'views/res_partner_view.xml'
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
