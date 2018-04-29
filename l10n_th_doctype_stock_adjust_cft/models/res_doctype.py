# -*- coding: utf-8 -*-
from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    refer_type = fields.Selection(
        selection_add=[
            ('in', 'Receipt'),
            ('internal', 'Internal Transfer'),
            ('picking', 'Pick'),
            ('out', 'Delivery Order'),
        ],
    )
