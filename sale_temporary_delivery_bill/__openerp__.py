# Copyright 2022 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "CFT - Sale Temporary Delivery Bill",
    "summary": "Create temporary delivery bill from sale order",
    "version": "8.0.1.0.0",
    "author": "Ecosoft",
    "license": "AGPL-3",
    "website": "https://github.com/ecosoft-odoo/cft",
    "category": "Sales Management",
    "depends": ["sale", "stock"],
    "data": [
        "data/ir_sequence_data.xml",
        "data/doctype_data.xml",
        "data/report_data.xml",
        "security/ir.model.access.csv",
        "views/temporary_delivery_bill_views.xml",
        "views/sale_views.xml",
    ],
    "installable": True,
    "maintainers": ["newtratip"],
}
