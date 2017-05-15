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

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    order_id = fields.Many2one(
        'sale.order',
        compute='_compute_order_id',
        store=True,
    )

    @api.multi
    @api.depends('origin')
    def _compute_order_id(self):
        Order = self.env['sale.order']
        Picking = self.env['stock.picking']
        for invoice in self:
            origin = invoice.origin and invoice.origin.split(':')[0] or False
            invoice.order_id = False
            if origin:

                # Find order_name for stock picking
                if origin.find('WH') != -1:
                    picking = Picking.search([('name', '=', origin)])
                    origin = picking and picking.origin.split(':')[0] or False

                # Find order_id
                if origin and origin.find('SO') != -1:
                    order = Order.search([('name', '=', origin)])
                    invoice.order_id = order and order.id or False
