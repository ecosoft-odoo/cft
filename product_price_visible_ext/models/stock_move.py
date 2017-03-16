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


    # override the method to use sudo() to update standard_price
    @api.multi
    def product_price_update_before_done(self):
        tmpl_dict = {}
        for move in self:
            # adapt standard price on incomming moves if the product cost_method is 'average'
            if (move.location_id.usage == 'supplier') and (
                move.product_id.cost_method == 'average'):
                product = move.product_id
                prod_tmpl_id = move.product_id.product_tmpl_id.id
                qty_available = move.product_id.product_tmpl_id.qty_available
                if tmpl_dict.get(prod_tmpl_id):
                    product_avail = qty_available + tmpl_dict[
                        prod_tmpl_id]
                else:
                    tmpl_dict[prod_tmpl_id] = 0
                    product_avail = qty_available
                if product_avail <= 0:
                    new_std_price = move.price_unit
                else:
                    # Get the standard pricee
                    # amount_unit = product.standard_price  # del [OSCG]
                    amount_unit = product.sudo().standard_price  # add [OSCG]
                    new_std_price = ((amount_unit * product_avail) + (
                    move.price_unit * move.product_qty)) / (
                                    product_avail + move.product_qty)
                tmpl_dict[prod_tmpl_id] += move.product_qty
                # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
                move.product_id.with_context(
                    force_company=move.company_id.id
                ).sudo().standard_price = new_std_price
