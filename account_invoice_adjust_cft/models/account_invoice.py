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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    order_id = fields.Many2one(
        'sale.order',
        compute='_compute_order_id',
    )
    flag_ignore_si_number = fields.Boolean(
        string='Ignore SI Number',
        copy=False,
    )

    @api.multi
    @api.depends('origin')
    def _compute_order_id(self):
        Order = self.env['sale.order']
        Picking = self.env['stock.picking']
        for invoice in self:
            invoice.order_id = False
            order = False
            picking = False
            old_picking = False
            origins = invoice.origin and invoice.origin.split(':') or []
            for origin in origins:
                origin = origin.strip()

                # Find order from origin
                order = Order.search([('name', '=', origin)])
                if order:
                    break

                # Find picking from origin
                picking = Picking.search([('name', '=', origin)])
                if picking:
                    old_picking = picking
                else:
                    picking = old_picking
            # Assign order_id in invoice
            if order:
                invoice.order_id = order.id
            elif picking:
                origins = picking.origin and picking.origin.split(':') or []
                for origin in origins:
                    origin = origin.strip()

                    # Find order from origin
                    order = Order.search([('name', '=', origin)])
                    if order:
                        invoice.order_id = order.id
                        break

    @api.multi
    def invoice_validate(self):
        supplier_invoice_number = self[0].supplier_invoice_number
        if supplier_invoice_number:
            invoices = self.search(
                [('supplier_invoice_number', '=', supplier_invoice_number)])
            if len(invoices) > 1 and not self[0].flag_ignore_si_number:
                raise except_orm(
                    _('Warning!'),
                    _('Supplier Invoice Number have duplicate document '
                      'if you want to continue, '
                      'please select Ignore SI Number in tab Other Info')
                )
        return super(AccountInvoice, self).invoice_validate()
