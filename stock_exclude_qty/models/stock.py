# -*- coding: utf-8 -*-
from openerp import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    exclude_qty = fields.Boolean(
        string='Exclude QTY',
    )
