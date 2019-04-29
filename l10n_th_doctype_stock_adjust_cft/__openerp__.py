# -*- coding: utf-8 -*-
{
    "name": "CFT :: Sequence Number by Document Type for Stocks",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

New menu, > Settings > Technical > Sequences & Identifiers > Doctype

List of Doctype

* Receipt
* Internal Transfers
* Pick
* Delivery Orders

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Tharathip C.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'l10n_th_doctype_base',
        'stock',
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "data/doctype_data.xml",
    ],
}
