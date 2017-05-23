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

# Available commission rule
COMMISSION_RULE = [
    ('percent_fixed', 'Fixed Commission Rate'),
    ('percent_product_category', 'Product Category Commission Rate'),
    ('percent_product', 'Product Commission Rate'),
    ('percent_product_step', 'Product Commission Rate Steps'),
    ('percent_amount', 'Commission Rate By Order Amount')]

# COMMENT: All PEP8 + put string in fields
# Fix context if possible
# Performance on create worksheet line (last_loop ???)


class CommissionRule(models.Model):

    _name = 'commission.rule'
    _description = 'Commission Rule'

    name = fields.Char(
        string='Name',
        size=64,
        required=True,
    )
    type = fields.Selection(
        COMMISSION_RULE,
        string='Type',
        required=True,
    )
    fix_percent = fields.Float(
        string='Fix Percentage',
    )
    rule_rates = fields.One2many(
        'commission.rule.rate',
        'commission_rule_id',
        string='Rates',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    sale_team_ids = fields.One2many(
        'crm.case.section',
        'commission_rule_id',
        string='Teams',
    )
    salesperson_ids = fields.One2many(
        'res.users',
        'commission_rule_id',
        string='Salesperson',
    )


class CommissionRuleRate(models.Model):

    _name = 'commission.rule.rate'
    _description = 'Commission Rule Rate'
    _order = 'id'

    commission_rule_id = fields.Many2one(
        'commission.rule',
        string='Commission Rule',
    )
    amount_over = fields.Float(
        string='Amount Over',
        required=True,
    )
    amount_upto = fields.Float(
        string='Amount Up-To',
        required=True,
    )
    percent_commission = fields.Float(
        string='Commission (%)',
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
