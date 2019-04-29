# -*- coding: utf-8 -*-
from openerp import models, api


class StockPickng(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        fiscalyear_id = self.env['account.fiscalyear'].find()
        self = self.with_context(fiscalyear_id=fiscalyear_id)
        return super(StockPickng, self).create(vals)
