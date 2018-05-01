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
        'pabi_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
        'reports/product_stock_ledger_wizard.xml',
        'reports/product_stock_ledger_view.xml',
    ],
    'active': False,
    'application': False,
    'installable': True
}
