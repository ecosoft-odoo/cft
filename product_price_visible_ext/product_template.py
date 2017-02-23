# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields, expression
import openerp.addons.decimal_precision as dp


class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'standard_price': fields.property(
            type='float',
            digits_compute=dp.get_precision('Product Price'),
            help="Cost price of the product template used for standard stock valuation in accounting and used as a base price on purchase orders. "
                 "Expressed in the default unit of measure of the product.",
            groups="product_price_visible.group_product_visible",
            string="Cost Price"),
    }
