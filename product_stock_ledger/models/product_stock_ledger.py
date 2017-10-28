# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp


class ProductStockLedger(models.Model):
    _name = 'product.stock.ledger'
    _description = 'Product Stock Ledger'
    _auto = False
    _order = 'product_id,date_invoice,invoice_number,price_unit,uos_id'

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
    invoice_number = fields.Char(
        string='Invoice Number',
        readonly=True,
    )
    in_qty = fields.Float(
        string='In',
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    out_qty = fields.Float(
        string='Out',
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    balance_qty = fields.Float(
        string='Balance',
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    price_unit = fields.Float(
        string='Unit Price',
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    uos_id = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total Amount',
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )
    price_balance = fields.Float(
        string='Balance Price',
        readonly=True,
        digits_compute=dp.get_precision('Account'),
    )

    @api.model
    def _compute_stock_ledger(self, products=[],
                              date_start=False, date_end=False):
        if not products:
            raise ValidationError(_("Not Products!!"))

        condition = ""

        # Products
        if len(products) == 1:
            condition += " line.product_id = " + str(products[0])
        else:
            condition += " line.product_id in " + str(tuple(products))

        # Start Date
        if date_start:
            condition += " and inv.date_invoice >= " + "'" + date_start + "'"

        # End Date
        if date_end:
            condition += " and inv.date_invoice <= " + "'" + date_end + "'"

        tools.drop_view_if_exists(self._cr, 'product_stock_ledger')
        self._cr.execute("""CREATE OR REPLACE VIEW product_stock_ledger AS
                         (SELECT ROW_NUMBER() OVER (ORDER BY line.product_id, inv.date_invoice, inv.number, line.price_unit, line.uos_id) AS id,
                                 line.product_id AS product_id,
                                 inv.date_invoice AS date_invoice,
                                 inv.number AS invoice_number,
                                 SUM(CASE inv.type WHEN 'in_invoice' THEN line.quantity WHEN 'in_refund' THEN (-1) * line.quantity ELSE 0.0 END) AS in_qty,
                                 SUM(CASE inv.type WHEN 'out_invoice' THEN line.quantity WHEN 'out_refund' THEN (-1) * line.quantity ELSE 0.0 END) AS out_qty,
                                 (SUM(SUM(CASE inv.type WHEN 'in_invoice' THEN line.quantity WHEN 'in_refund' THEN (-1) * line.quantity ELSE 0.0 END) - SUM(CASE inv.type WHEN 'out_invoice' THEN line.quantity WHEN 'out_refund' THEN (-1) * line.quantity ELSE 0.0 END)) OVER (PARTITION BY line.product_id ORDER BY line.product_id, inv.date_invoice, inv.number, line.price_unit, line.uos_id)) AS balance_qty,
                                 line.price_unit AS price_unit,
                                 line.uos_id AS uos_id,
                                 ((SUM(CASE inv.type WHEN 'in_invoice' THEN line.quantity WHEN 'in_refund' THEN (-1) * line.quantity ELSE 0.0 END) + SUM(CASE inv.type WHEN 'out_invoice' THEN line.quantity WHEN 'out_refund' THEN (-1) * line.quantity ELSE 0.0 END)) * line.price_unit) AS amount_total,
                                 ((SUM(SUM(CASE inv.type WHEN 'in_invoice' THEN line.quantity WHEN 'in_refund' THEN (-1) * line.quantity ELSE 0.0 END) - SUM(CASE inv.type WHEN 'out_invoice' THEN line.quantity WHEN 'out_refund' THEN (-1) * line.quantity ELSE 0.0 END)) OVER (PARTITION BY line.product_id ORDER BY line.product_id, inv.date_invoice, inv.number, line.price_unit, line.uos_id)) * (SELECT value_float FROM ir_property WHERE name = 'standard_price' and res_id = concat('product.template,', line.product_id) LIMIT 1)) AS price_balance
                          FROM account_invoice_line line
                          LEFT JOIN account_invoice inv ON inv.id = line.invoice_id
                          WHERE inv.state in ('paid') and %s
                          GROUP BY line.product_id, inv.date_invoice, inv.number, line.price_unit, line.uos_id
                          ORDER BY line.product_id, inv.date_invoice, inv.number, line.price_unit, line.uos_id)""" % (condition))


class ProductProduct(models.Model):
    _inherit = "product.product"
    stock_ledger_ids = fields.One2many(
        'product.stock.ledger',
        'product_id',
        string='Stock Ledger',
    )
