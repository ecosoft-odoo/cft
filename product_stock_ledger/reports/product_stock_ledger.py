# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import openerp.addons.decimal_precision as dp


class ProductStockLedger(models.Model):
    _name = 'product.stock.ledger'
    _description = 'Product Stock Ledger'
    _auto = False
    _order = "id"

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
    standard_price = fields.Float(
        string='Cost Price',
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
    def _get_condition(self, product_ids, partner_id, date_start, date_end):
        condition = ""
        # Products
        if len(product_ids) == 1:
            condition += "line.product_id = %s" % (str(product_ids[0]), )
        else:
            condition += "line.product_id IN %s" % (str(tuple(product_ids)), )

        # Partner
        if partner_id:
            condition += " AND inv.partner_id = %s" % (str(partner_id), )

        # Start Date
        if date_start:
            condition += " AND inv.date_invoice >= '%s'" % (date_start, )

        # End Date
        if date_end:
            condition += " AND inv.date_invoice <= '%s'" % (date_end, )
        return condition

    @api.model
    def _compute_product_stock_ledger(self, product_ids, partner_id,
                                      date_start, date_end):
        condition = self._get_condition(
            product_ids, partner_id, date_start, date_end)

        sql = """
            SELECT ROW_NUMBER()
                    OVER (ORDER BY line.product_id, inv.date_invoice,
                          inv.number, line.price_unit, line.uos_id,
                          line.price_subtotal,
                          line.quantity) AS id,
                   line.product_id AS product_id,
                   inv.date_invoice AS date_invoice,
                   inv.number AS invoice_number,
                   SUM(CASE inv.type WHEN 'in_invoice' THEN line.quantity
                       WHEN 'in_refund' THEN (-1) * line.quantity ELSE 0.0 END)
                       AS in_qty,
                   SUM(CASE inv.type WHEN 'out_invoice' THEN line.quantity
                       WHEN 'out_refund' THEN (-1) * line.quantity
                       ELSE 0.0 END) AS out_qty,
                   (SUM(SUM(CASE inv.type WHEN 'in_invoice' THEN line.quantity
                            WHEN 'in_refund' THEN (-1) * line.quantity
                            ELSE 0.0 END) -
                        SUM(CASE inv.type WHEN 'out_invoice' THEN line.quantity
                            WHEN 'out_refund' THEN (-1) * line.quantity
                            ELSE 0.0 END))
                    OVER (PARTITION BY line.product_id
                          ORDER BY line.product_id, inv.date_invoice,
                                   inv.number, line.price_unit, line.uos_id,
                                   line.price_subtotal, line.quantity))
                   AS balance_qty,
                   (SELECT value_float
                    FROM ir_property
                    WHERE name = 'standard_price' AND
                          res_id = (SELECT CONCAT('product.template,',
                                                  product.product_tmpl_id)
                                    FROM product_product product
                                    WHERE id = line.product_id) LIMIT 1)
                   AS standard_price,
                   (SUM(line.price_subtotal) / SUM(line.quantity))
                   AS price_unit,
                   line.uos_id AS uos_id,
                   SUM(line.price_subtotal) AS amount_total,
                   ((SUM(SUM(CASE inv.type WHEN 'in_invoice' THEN line.quantity
                             WHEN 'in_refund' THEN (-1) * line.quantity
                             ELSE 0.0 END) -
                         SUM(CASE inv.type
                             WHEN 'out_invoice' THEN line.quantity
                             WHEN 'out_refund' THEN (-1) * line.quantity
                             ELSE 0.0 END))
                     OVER (PARTITION BY line.product_id
                           ORDER BY line.product_id, inv.date_invoice,
                                    inv.number, line.price_unit, line.uos_id,
                                    line.price_subtotal, line.quantity))
                     * (SELECT value_float
                        FROM ir_property
                        WHERE name = 'standard_price'
                        AND res_id = (SELECT CONCAT('product.template,',
                                                    product.product_tmpl_id)
                                      FROM product_product product
                                      WHERE id = line.product_id)
                        LIMIT 1)) AS price_balance
            FROM account_invoice_line line
            LEFT JOIN account_invoice inv ON inv.id = line.invoice_id
            WHERE inv.state IN ('paid') AND %s
            GROUP BY line.product_id, inv.date_invoice, inv.number,
                     line.price_unit, line.uos_id, line.price_subtotal,
                     line.quantity
            ORDER BY line.product_id, inv.date_invoice, inv.number,
                     line.price_unit, line.uos_id, line.price_subtotal,
                     line.quantity
        """ % (condition, )

        tools.drop_view_if_exists(self._cr, 'product_stock_ledger')
        self._cr.execute("""CREATE OR REPLACE VIEW product_stock_ledger AS
                         (%s)""" % (sql, ))
