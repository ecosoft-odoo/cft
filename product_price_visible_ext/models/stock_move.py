# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'


    # override the method to use sudo() to access standard_price
    @api.model
    def attribute_price(self, move):
        if not move.price_unit:
            price = move.product_id.sudo().standard_price
            move.price_unit = price

    # below code did not work even though uid was set to 1
    # @api.v7
    # def attribute_price(self, cr, uid, move, context=None):
    #     super(StockMove, self).attribute_price(
    #         cr, SUPERUSER_ID, move, context=context)
