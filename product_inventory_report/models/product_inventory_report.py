# -*- coding: utf-8 -*-
from openerp import models, fields, tools


class ProductInventoryReport(models.Model):
    _name = 'product.inventory.report'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product Name',
        readonly=True,
    )
    categ_id = fields.Many2one(
        'product.category',
        string='Internal Category',
        readonly=True,
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='PO.No.',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier Name',
        readonly=True,
    )
    in_date = fields.Datetime(
        string='Incoming Date',
        readonly=True,
    )
    qty = fields.Float(
        string='Quantity',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'product_inventory_report')
        cr.execute("""CREATE OR REPLACE VIEW product_inventory_report AS
                   (SELECT q.id,
                           q.product_id,
                           t.categ_id,
                           (SELECT po.id
                            FROM purchase_order po
                            LEFT JOIN purchase_order_line pol
                                ON po.id = pol.order_id
                            LEFT JOIN stock_move m
                                ON pol.id = m.purchase_line_id
                            LEFT JOIN stock_quant_move_rel r
                                ON m.id = r.move_id
                            WHERE r.quant_id = q.id
                            LIMIT 1) AS order_id,
                           (SELECT po.partner_id
                            FROM purchase_order po
                            LEFT JOIN purchase_order_line pol
                                ON po.id = pol.order_id
                            LEFT JOIN stock_move m
                                ON pol.id = m.purchase_line_id
                            LEFT JOIN stock_quant_move_rel r
                                ON m.id = r.move_id
                            WHERE r.quant_id = q.id
                            LIMIT 1) AS partner_id,
                           q.in_date,
                           q.qty
                    FROM stock_quant q
                    LEFT JOIN product_product p ON q.product_id = p.id
                    LEFT JOIN product_template t ON p.product_tmpl_id = t.id)
                    """)
