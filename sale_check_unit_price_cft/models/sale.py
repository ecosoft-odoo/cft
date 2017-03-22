# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _
from openerp.tools import float_compare, float_round
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for sale in self:
            for line in sale.order_line:
                if line.product_uom_qty:
                    raw_price = line.price_subtotal / line.product_uom_qty
                    round_price = float_round(line.price_subtotal /
                                              line.product_uom_qty, 2)
                    if float_compare(raw_price, round_price, 4) != 0:
                        raise ValidationError(
                            _("Your discount %s%% result in unit price after "
                              "discount = %s (> 2 decimal points).\n"
                              "You should adjust unit price manually!") %
                            (line.discount, raw_price, ))
        return super(SaleOrder, self).action_button_confirm()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
