# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Model Security Adjust CFT",
    "version": "8.0.2.0.0",
    "author": "Ecosoft Co. Ltd.",
    "license": "AGPL-3",
    "description": """
    """,
    "category": "Uncategorized",
    "depends": [
        'crm','purchase',
    ],
    "data": [
        'security/module_data.xml',
        'security/partner_view.xml',
        'security/product_security.xml',
        'security/base_security.xml',
        'data/ir.model.access.csv'
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