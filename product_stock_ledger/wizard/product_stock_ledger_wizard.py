# -*- coding: utf-8 -*-
from openerp import models, fields, api
from lxml import etree
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

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        context = self._context.copy() or {}
        res = super(ProductStockLedgerWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu
        )
        if len(context.get('active_ids', [])) > 1:
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//button[@name='open_stock_ledger']")
            for node in nodes:
                node.set('modifiers', '{"invisible": true}')
            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def open_stock_ledger(self):
        # Compute Stock Ledger
        self.env['product.stock.ledger'].init()

        context = self._context.copy() or {}
        stock_ledger_wizard = self.read(['product_id', 'from_date', 'to_date'])
        domain = []
        ctx = {}
        if stock_ledger_wizard:
            # Found Product.
            if stock_ledger_wizard[0]['product_id']:
                product_id = stock_ledger_wizard[0]['product_id'][0]
                domain += [('product_id', '=', product_id)]
            else:
                product_id = context.get('active_id', False)
                domain += [('product_id', '=', product_id)]

            # Found Date Start Or Date End.
            if stock_ledger_wizard[0]['from_date']:
                date_start = stock_ledger_wizard[0]['from_date']
                domain += [('date_invoice', '>=', date_start)]
            if stock_ledger_wizard[0]['to_date']:
                date_end = stock_ledger_wizard[0]['to_date']
                domain += [('date_invoice', '<=', date_end)]

        return {
            'name': _('Stock Ledger'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.stock.ledger',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain,
        }

    @api.multi
    def print_stock_ledger(self):
        StockLedger = self.env['product.stock.ledger']
        # Compute Stock Ledger
        StockLedger.init()

        stock_ledger_wizard = self.read(['product_id', 'from_date', 'to_date'])
        context = self._context.copy() or {}
        domain = []
        parameters = {}
        product_id = False
        if stock_ledger_wizard:
            # Found Product.
            if stock_ledger_wizard[0]['product_id']:
                product_id = stock_ledger_wizard[0]['product_id'][0]
                domain += [('product_id', '=', product_id)]
                parameters.update({'product_id': product_id})
            else:
                product_id = context.get('active_id', False)
                domain += [('product_id', '=', product_id)]
                parameters.update({'product_id': product_id})

            if product_id:
                product = self.env['product.product'].sudo().browse(product_id)
                # pass parameter price unit
                parameters.update({'price_unit': product.standard_price})

            # Compute Amount (in_qty, out_qty, balance, amount_total)
            StockLedger.search([('product_id', '=', product_id)]) \
                ._compute_amount()

            # Found Date Start Or Date End.
            if stock_ledger_wizard[0]['from_date']:
                date_start = stock_ledger_wizard[0]['from_date']
                domain += [('date_invoice', '>=', date_start)]
                parameters.update({'from_date': date_start})
            if stock_ledger_wizard[0]['to_date']:
                date_end = stock_ledger_wizard[0]['to_date']
                domain += [('date_invoice', '<=', date_end)]
                parameters.update({'to_date': date_end})

        data = self.read()[-1]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.product.normal.stock.ledger',
            'report_type': 'xls',
            'context': context,
            'domain': domain,
            'datas': {
                'model': 'product.product',
                'id': product_id,
                'ids': [product_id],
                'form': data,
                'parameters': parameters
            }
        }
