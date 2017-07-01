# -*- coding: utf-8 -*-
{
    'name': 'Comforta Jasper Forms',
    'version': '8.0.1.0.1',
    'author': 'Ecosoft',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'jasper_reports',
        'account_billing',
        'sale_customer_attn',
        'purchase_delivery_method',
        'l10n_th_amount_text_ext',
    ],
    'data': [
        "security/jasper_forms_cft_security.xml",
        "jasper_data.xml",
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
