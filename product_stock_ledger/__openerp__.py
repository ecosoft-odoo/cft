# -*- coding: utf-8 -*-
{
    'name': 'Product Stock Ledger',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """Product Stock Ledger""",
    'author': 'Tharathip C.',
    'website': 'http://www.ecosoft.co.th',
    'depends': [
        'product',
        'account',
        'product_price_visible',
        'jasper_reports',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_stock_ledger_wizard.xml',
        'views/product_stock_ledger_view.xml',
        'views/reports.xml',
    ],
    'active': False,
    'application': False,
    'installable': True
}
