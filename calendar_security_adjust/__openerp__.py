# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Calendar Security Adjustments",
    "summary": "",
    "version": "8.0.1.2.0",
    "category": "Sale",
    "website": "http://ecosoft.co.th/",
    "author": "Ecosoft Co. Ltd.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "calendar",
        "sales_team",
    ],
    "data": [
        "security/calendar_security.xml",
        "views/res_users_view.xml",
        "views/calendar_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
