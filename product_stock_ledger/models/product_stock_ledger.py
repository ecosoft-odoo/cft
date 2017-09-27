# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import openerp.addons.decimal_precision as dp


class ProductStockLedger(models.Model):
    _name = 'product.stock.ledger'
    _rec_name = 'product_id'
    _description = 'Product Stock Ledger'
    _auto = False
    _order = 'product_id,date_invoice,invoice_number'

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product Name',
        readonly=True,
    )
    date_invoice = fields.Date(
        string='Date',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice ID',
        readonly=True,
    )
    invoice_number = fields.Char(
        string='Invoice Number',
        readonly=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        related='product_id.standard_price',
        method=True,
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    in_qty = fields.Float(
        string='In',
        compute='_compute_amount',
        method=True,
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    out_qty = fields.Float(
        string='Out',
        compute='_compute_amount',
        method=True,
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    balance = fields.Float(
        string='Balance',
        compute='_compute_amount',
        method=True,
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount',
        method=True,
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'product_stock_ledger')
        cr.execute("""CREATE OR REPLACE VIEW product_stock_ledger AS
                      (SELECT ROW_NUMBER() OVER (ORDER BY line.product_id, inv.date_invoice, line.invoice_id, inv.number ASC) AS id,
                              line.product_id AS product_id,
                              inv.date_invoice AS date_invoice,
                              line.invoice_id AS invoice_id,
                              inv.number AS invoice_number
                       FROM account_invoice_line line
                       LEFT JOIN account_invoice inv ON inv.id = line.invoice_id
                       WHERE inv.state in ('open', 'paid')
                       GROUP BY line.product_id, inv.date_invoice, line.invoice_id, inv.number
                       ORDER BY line.product_id, inv.date_invoice, inv.number);""")

    @api.multi
    def _compute_amount(self):
        UOM = self.env['product.uom']
        InvLine = self.env['account.invoice.line']
        balance = 0.0

        self = sorted(self, key=lambda x: (x.product_id, x.date_invoice,
                                           x.invoice_number))
        for stock_ledger in self:
            # Initial
            in_qty = 0.0
            out_qty = 0.0
            qty = 0.0

            inv_lines = InvLine.search([
                ('product_id', '=', stock_ledger.product_id.id),
                ('invoice_id', '=', stock_ledger.invoice_id.id)])

            for inv_line in inv_lines:
                qty += UOM._compute_qty_obj(inv_line.uos_id, inv_line.quantity,
                                            inv_line.product_id.uom_id)

            if stock_ledger.invoice_id.type in ('in_invoice', 'in_refund'):
                if stock_ledger.invoice_id.type == 'in_invoice':
                    in_qty = qty
                else:
                    in_qty = (-1) * qty
                balance += in_qty
            elif stock_ledger.invoice_id.type in ('out_invoice', 'out_refund'):
                if stock_ledger.invoice_id.type == 'out_invoice':
                    out_qty = qty
                else:
                    out_qty = (-1) * qty
                balance -= out_qty

            amount_total = balance * stock_ledger.price_unit
            # Assign Value
            stock_ledger.in_qty = in_qty
            stock_ledger.out_qty = out_qty
            stock_ledger.balance = balance
            stock_ledger.amount_total = amount_total


class ProductProduct(models.Model):
    _inherit = "product.product"
    stock_ledger_ids = fields.One2many(
        'product.stock.ledger',
        'product_id',
        string='Stock Ledger',
    )

    @api.one
    def copy(self, default={}):
        default['stock_ledger_ids'] = []
        return super(ProductProduct, self).copy(default)
