# coding=utf-8
##############################################################################
#
#    account_auto_fy_sequence module for Odoo
#    Copyright (C) 2014 ACSONE SA/NV (<http://acsone.eu>)
#    @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
#
#    account_auto_fy_sequence is free software:
#    you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License v3 or later
#    as published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    account_auto_fy_sequence is distributed
#    in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License v3 or later for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    v3 or later along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields

LAST_PAY_DATE_RULE = [
    ('invoice_duedate', 'Invoice Due Date (default)'),
    ('invoice_date_plus_cust_payterm', 'Invoice Date + Customer Payment Term'),
]


class SalesTeam(models.Model):
    _inherit = 'crm.case.section'

    target_amount_ids = fields.One2many(
        'target.amount', 'team_ids',
        string='Target Amount',
    )
    commission_rule_id = fields.Many2one(
        'commission.rule',
        string='Applied Commission',
        required=False,
        readonly=False,
    )
    require_paid = fields.Boolean(
        string='Require Paid Invoice',
        help="Require invoice to be paid in full amount.",
        default=False,
    )
    require_posted = fields.Boolean(
        string='Require Payment Detail Posted',
        help="Require that all payment detail related to payments "
             "to invoice has been posted.",
        default=False,
    )
    allow_overdue = fields.Boolean(
        string='Allow Overdue Payment',
        help="Allow paying commission with overdue payment.",
        default=False,
    )
    last_pay_date_rule = fields.Selection(
        LAST_PAY_DATE_RULE,
        string='Last Pay Date Rule',
    )
    buffer_days = fields.Integer(
        string='Buffer Days',
        default=0,
    )
