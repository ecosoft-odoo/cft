# -*- coding: utf-8 -*-
{
    "name": "Purchase Adjust CFT",
    "version": "8.0.1.0.0",
    "author": "Tharathip C.",
    "license": "AGPL-3",
    "description": """
    """,
    "category": "Purchase",
    "depends": [
        'purchase',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
        'views/res_currency_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    'application': False,
}
