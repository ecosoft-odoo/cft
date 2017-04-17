# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Assign a Salesperson to many Customers at once.",

    'summary': """
        This module allows you to assign a Salesperson to many customers, leads, and opportunities at once
    """,

    'description': """
        This module allows you to assign a Salesperson to many customers, leads, and opportunities at once.  Thanks to this, you will save a lot of time.

        This module has been written by Atteli. We create modern software for companies. See our other products for Odoo and visit our website: atteli.com
    """,

    'author': "Atteli - Juliusz Sosinowicz, Rooms For (Hong Kong) Limited T/A OSCG",
    'website': "http://www.atteli.com, https://www.odoo-asia.com",
    'category': 'Customer Relationship Management',
    'version': '8.0.1.1.0',
    'images': ['images/SpiceShop_slide_Assign.jpg'],
    'depends': ['crm'],
    'data': [
        'wizard/assign_salesperson_to_customer_view.xml',
    ],
}
