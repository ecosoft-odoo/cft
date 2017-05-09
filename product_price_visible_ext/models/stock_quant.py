# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # override the standard method to use `sudo()` to access standard_price
    @api.model
    def _get_inventory_value(self, quant):
        if quant.product_id.cost_method in ('real'):
            return quant.cost * quant.qty
        return quant.product_id.sudo().standard_price * quant.qty
