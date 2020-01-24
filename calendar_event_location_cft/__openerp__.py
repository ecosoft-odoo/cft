# -*- coding: utf-8 -*-
# Copyright 2020 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Calendar Event Location",
    "summary": "",
    "version": "8.0.1.0.0",
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
    "js": [
        "static/src/js/check_in.js",
    ],
    "data": [
        "views/assets.xml",
        "views/calendar_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
