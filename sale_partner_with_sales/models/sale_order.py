# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    def action_button_confirm(self):
        if not self.partner_id.has_sales:
            self.partner_id.has_sales = True
        super(SaleOrder, self).action_button_confirm()
