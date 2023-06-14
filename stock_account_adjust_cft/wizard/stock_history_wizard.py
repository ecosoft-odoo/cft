# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockHistoryWizard(models.TransientModel):
    _name = 'stock.history.wizard'

    product_ids = fields.Many2many(
        'product.product',
        string='Products',
    )
    product_categ_ids = fields.Many2many(
        'product.category',
        string='Product Categorys',
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
        if self.product_ids:
            domain += [('product_id', 'in', self.product_ids.ids)]
        if self.product_categ_ids:
            domain += [('product_categ_id', 'in', self.product_categ_ids.ids)]
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        if domain:
            result.update({
                'domain': domain,
            })
        return result
