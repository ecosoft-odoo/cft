# -*- encoding: utf-8 -*-
{
    'name': 'CFT :: Partner External Maps Adjust',
    'version': '8.0.1.0.0',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'author': 'Tharathip C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'base_geolocalize',
        'l10n_th_address',
        'partner_external_maps',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'application': False,
    'installable': True,
}
