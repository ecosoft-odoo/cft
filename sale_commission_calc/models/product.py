# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):

    _inherit = 'product.product'

    percent_commission = fields.Float(
        string='Commission (%)',
        digits=(16, 2),
        readonly=False,
    )
    limit_price = fields.Float(
        string='Limit Price',
        digits_compute=dp.get_precision('Product Price'),
        readonly=False,
        help="Minimum product selling price to get commission",
    )
    rate_step_ids = fields.One2many(
        'commission.rate.step',
        'product_id',
        string='Commission Rate Steps',
        readonly=False,
    )


class CommissionRateStep(models.Model):

    _name = 'commission.rate.step'
    _order = 'amount_over'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
        ondelete='cascade',
        select=True,
    )
    amount_over = fields.Float(
        string='From Unit Price',
        digits_compute=dp.get_precision('Product Price'),
        readonly=False,
    )
    percent_commission = fields.Float(
        string='Commission (%)',
        digits=(16, 2),
        readonly=False,
    )


class ProductCategory(models.Model):

    _inherit = 'product.category'

    percent_commission = fields.Float(
        string='Commission (%)',
        digits=(16, 2),
        readonly=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
