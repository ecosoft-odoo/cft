# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _


class ProductStockLedgerWizard(models.TransientModel):

    _name = 'product.stock.ledger.wizard'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    from_date = fields.Date(
        string='From Date',
    )
    to_date = fields.Date(
        string='To Date',
    )

    @api.multi
    def open_stock_ledger(self):
        context = self._context.copy() or {}
        stock_ledger_wizard = self.read(['product_id', 'from_date', 'to_date'])

        products = []
        date_start = False
        date_end = False
        if stock_ledger_wizard:
            if stock_ledger_wizard[0]['product_id']:
                products = [stock_ledger_wizard[0]['product_id'][0]]
            else:
                products = context.get('active_ids', [])

            if stock_ledger_wizard[0]['from_date']:
                date_start = stock_ledger_wizard[0]['from_date']
            if stock_ledger_wizard[0]['to_date']:
                date_end = stock_ledger_wizard[0]['to_date']

        self.env['product.stock.ledger']._compute_stock_ledger(
            products=products, date_start=date_start, date_end=date_end
        )

        return {
            'name': _('Stock Ledger'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.stock.ledger',
            'type': 'ir.actions.act_window',
            'context': {'search_default_by_product': 1},
        }

    @api.multi
    def print_stock_ledger(self):
        context = self._context.copy() or {}
        stock_ledger_wizard = self.read(['product_id', 'from_date', 'to_date'])

        products = []
        date_start = False
        date_end = False
        if stock_ledger_wizard:
            if stock_ledger_wizard[0]['product_id']:
                products = [stock_ledger_wizard[0]['product_id'][0]]
            else:
                products = context.get('active_ids', [])

            if stock_ledger_wizard[0]['from_date']:
                date_start = stock_ledger_wizard[0]['from_date']
            if stock_ledger_wizard[0]['to_date']:
                date_end = stock_ledger_wizard[0]['to_date']

        self.env['product.stock.ledger']._compute_stock_ledger(
            products=products, date_start=date_start, date_end=date_end
        )

        data = self.read()[-1]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.product.normal.stock.ledger',
            'report_type': 'xls',
            'datas': {
                'model': 'product.product',
                'id': products and products[0] or False,
                'ids': products,
                'form': data,
            }
        }
