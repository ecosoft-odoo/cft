# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _
from openerp.tools import float_compare, float_round
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.constrains('order_line')
    def _check_unit_price_discount(self):
        for line in self.order_line:
            if line.product_uom_qty:
                raw_price = line.price_subtotal / line.product_uom_qty
                round_price = float_round(line.price_subtotal /
                                          line.product_uom_qty, 2)
                if float_compare(raw_price, round_price, 4) != 0:
                    raise ValidationError(
                        _("%s\nYour discount %s%% result in unit price after "
                          "discount = %s (> 2 decimal points).\n"
                          "You should adjust unit price manually!") %
                        (line.name, line.discount, raw_price, ))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
