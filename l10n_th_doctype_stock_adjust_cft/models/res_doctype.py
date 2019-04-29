# -*- coding: utf-8 -*-
from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    refer_type = fields.Selection(
        selection_add=[
            ('receipt', 'Receipt'),
            ('internal_transfer', 'Internal Transfer'),
            ('pick', 'Pick'),
            ('delivery_order', 'Delivery Order'),
        ],
    )
