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

from openerp import models, fields, api
from openerp.tools.translate import _


class UpdateInvoiceCommission(models.TransientModel):

    _name = 'update.invoice.commission'
    _description = 'Update Invoice Commission'

    result = fields.Text(
        string='Result',
        readonly=True,
    )
    state = fields.Selection(
        [('init', 'init'), ('done', 'done')],
        string='Status',
        readonly=True,
        default='init',
    )

    @api.multi
    def update_commission(self):
        updated = 0
        Invoice = self.env['account.invoice']
        InvoiceTeam = self.env['account.invoice.team']
        # Get salepersons/team commission for users in invoices
        invoices = Invoice.search([('type', 'in',
                                    ('out_invoice', 'out_refund'))])
        users = list(set(invoices.mapped('user_id')))
        for user in users:
            # For this users, find relevant commission
            salespersons = Invoice._get_salesperson_comm(user)
            sale_teams = Invoice._get_sale_team_comm(user)
            invoice_comms = salespersons + sale_teams
            if not invoice_comms:
                continue
            # For this users, find relevant invoices
            invoices = Invoice.search([
                ('user_id', '=', user.id),
                ('type', 'in', ('out_invoice', 'out_refund'))])
            # Only for invoice without commission, create it.
            for invoice in invoices:
                if not invoice.sale_team_ids:
                    for invoice_comm in invoice_comms:
                        invoice_comm.update({'invoice_id': invoice.id})
                        InvoiceTeam.create(invoice_comm)
                    updated += 1
        # Message
        result_message = _('Number of invoice updated') + ' = ' + str(updated)

        self.write({'result': result_message, 'state': 'done'})
        res = {
            'name': _("Update Invoice's Commission"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'update.invoice.commission',
            'res_id': self.ids[0],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
