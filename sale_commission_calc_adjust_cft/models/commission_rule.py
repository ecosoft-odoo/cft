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

COMMISSION_RULE = [
    ('percent_fixed', 'Fixed Commission Rate'),
    ('percent_product_category', 'Product Category Commission Rate'),
    ('percent_product', 'Product Commission Rate'),
    ('percent_product_step', 'Product Commission Rate Steps'),
    ('percent_amount', 'Commission Rate By Order Amount'),
    ('percent_customer', 'Customer Commission Rate'),
    ('percent_sale_commission', 'Sale Commission Rate'), ]


class CommissionRule(models.Model):
    _inherit = 'commission.rule'

    type = fields.Selection(
        COMMISSION_RULE,
        default='percent_sale_commission',
    )
