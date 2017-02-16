# -*- coding: utf-8 -*-
{
    'name': "Assign a Salesperson to many Customers at once.",

    'summary': """
        This module allows you to assign a Salesperson to many customers, leads, and opportunities at once
    """,

    'description': """
        This module allows you to assign a Salesperson to many customers, leads, and opportunities at once.  Thanks to this, you will save a lot of time.

        This module has been written by Atteli. We create modern software for companies. See our other products for Odoo and visit our website: atteli.com
    """,

    'author': "Atteli - Juliusz Sosinowicz",
    'website': "http://www.atteli.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Customer Relationship Management',
    'version': '0.1',

    'images': ['images/SpiceShop_slide_Assign.jpg'],

    # any module necessary for this one to work correctly
    'depends': ['crm'],

    # always loaded
    'data': [
        'views/assign_salesperson_to_customer.xml',
    ],
}
