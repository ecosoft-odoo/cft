# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockHistoryWizard(models.TransientModel):
    _name = 'stock.history.wizard'

    date_from = fields.Date(
        string='Date From',
    )
    date_to = fields.Date(
        string='Date To',
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Products',
    )
    product_categ_ids = fields.Many2many(
        'product.category',
        string='Categories',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Suppliers',
        domain="[('supplier', '=', True)]",
    )

    @api.multi
    def run_report(self):
        self.ensure_one()
        action = self.env.ref('stock_account.action_history_tree')
        result = action.read()[0]
        domain = []
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]
        if self.product_ids:
            domain += [('product_id', 'in', self.product_ids.ids)]
        if self.product_categ_ids:
            domain += [('product_categ_id', 'in', self.product_categ_ids.ids)]
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        result.update({
            'domain': domain,
        })
        return result
