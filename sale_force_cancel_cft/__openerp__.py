# -*- coding: utf-8 -*-
{
    'name': 'sale_force_cancel_cft',
    'author': "Jutamat K",
    'category': 'Sales Management',
    'version': '8.0.1.0.0',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_view.xml',
        'security/security.xml',
        'workflow/sale_force_cancel_cft_workflow.xml',
    ],
}
