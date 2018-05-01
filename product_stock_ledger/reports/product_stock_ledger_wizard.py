# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _


class ProductStockLedgerWizard(models.TransientModel):

    _name = 'product.stock.ledger.wizard'

    filter_by = fields.Selection(
        selection=[
            ('product', 'Product'),
            ('category', 'Category'),
            ('partner', 'Partner'),
        ],
        string="Filter By",
        required=True,
        default='product',
    )
    product_ids = fields.Many2many(
        'product.product',
        'stock_ledger_wizard_product_rel',
        'wizard_id',
        'product_id',
        string='Product',
    )
    category_id = fields.Many2one(
        'product.category',
        string='Category',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    from_date = fields.Date(
        string='From Date',
    )
    to_date = fields.Date(
        string='To Date',
    )
    # Report Result
    results = fields.Many2many(
        'product.stock.ledger',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['product.stock.ledger']
        self.results = Result.search([], order="id")

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        self.product_id = False
        self.category_id = False
        self.partner_id = False

    @api.multi
    def _compute_product_stock_ledger(self):
        self.ensure_one()
        product_ids = self.env['product.product'].search([]).ids
        partner_id, date_start, date_end = False, False, False
        if self.product_ids:
            product_ids = self.product_ids.ids
        if self.category_id:
            product_ids = self.env['product.template'] \
                .search([('categ_id', '=', self.category_id.id)]).ids
            product_ids = self.env['product.product'] \
                .search([('product_tmpl_id', 'in', product_ids)])
        if self.partner_id:
            partner_id = self.partner_id.id
        if self.from_date:
            date_start = self.from_date
        if self.to_date:
            date_end = self.to_date
        self.env['product.stock.ledger']._compute_product_stock_ledger(
            product_ids, partner_id, date_start, date_end)

    @api.multi
    def open_product_stock_ledger(self):
        self._compute_product_stock_ledger()
        return {
            'name': _('Stock Ledger'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.stock.ledger',
            'type': 'ir.actions.act_window',
            'context': {'search_default_by_product': 1},
        }

    @api.multi
    def export_product_stock_ledger(self):
        self._compute_product_stock_ledger()
        return {
            'name': _('Export Stock Ledger'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'export.xlsx.template',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
