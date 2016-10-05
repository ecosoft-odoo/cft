# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Web Export View Group",
    "version": "8.0.1.0.0",
    "author": "Ecosoft Co. Ltd.",
    "license": "AGPL-3",
    "description": """
        This module is for limiting the access
        for "Excel Export Button". To assign
        the user to a new group named Excel
        Export,the user has accessed to this
        button to export needed information.
    """,
    "category": "Base",
    "depends": [
        'web_export_view',
    ],
    "data": [
        'security/web_export_view_security.xml'
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
