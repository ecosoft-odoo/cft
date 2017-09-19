# -*- coding: utf-8 -*-
{
    'name': 'CFT: Sale Group Adjust',
    'version': '8.0.1.0.0',
    'author': 'Tharathip C.',
    'description': """
    """,
    'category': 'Hidden',
    'website': 'http://www.ecosoft.co.th',
    'depends': [
        'product',
        'stock',
        'sale',
        'crm_claim',
        'crm',
        'customer_product_code',
    ],
    'data': [
        'security/sale_group_adjust_security.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
