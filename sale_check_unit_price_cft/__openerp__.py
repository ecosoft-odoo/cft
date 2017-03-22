# -*- coding: utf-8 -*-
# Copyright 2016-2017 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sales, check unit price for magic number",
    "version": "8.0.1.0.0",
    "author": "Ecosoft Co. Ltd.",
    "license": "AGPL-3",
    "description": """
Warning for sale_order_line with Magic Number,

quantity    price_unit  discount(%)  price_afd     price_subtotal
10          1615.00	    3.5          1558.475      15584.75

If price after discount has > 2 decimal, i.e., 1558.475, give user warning.

    """,
    "category": "Sales",
    "depends": [
        'sale',
    ],
    "data": [
    ],
    "auto_install": False,
    "installable": True,
    "external_dependencies": {
        'python': [],
    },
}
