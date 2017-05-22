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

COMPARE = [('greater_than', 'Greater Than'),
           ('less_than', 'Less Than'), ]


class SalesInvoicePercent(models.Model):
    _name = 'sales.invoice.percent'

    company_ids = fields.Many2one(
        'res.company',
        string='Company',
    )
    compare = fields.Selection(
        COMPARE,
        string='Compare',
    )
    target_percent = fields.Float(
        string='Target (%)',
    )
    invoice_percent = fields.Float(
        string='Invoice (%)',
    )


class TeamsInvoicePercent(models.Model):
    _name = 'teams.invoice.percent'

    company_ids = fields.Many2one(
        'res.company',
        string='Company',
    )
    compare = fields.Selection(
        COMPARE,
        string='Compare',
    )
    target_percent = fields.Float(
        string='Target (%)',
    )
    invoice_percent = fields.Float(
        string='Invoice (%)',
    )
