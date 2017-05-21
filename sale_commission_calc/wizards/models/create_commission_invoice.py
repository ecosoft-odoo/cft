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
import openerp.addons.decimal_precision as dp


class CreateCommissionInvoice(models.TransientModel):

    """Create Commission Invoice"""

    _name = 'create.commission.invoice'
    _description = 'Create Commission Invoice'

    commission_amt = fields.Float(
        string='Commission Amount',
        digits_compute=dp.get_precision('Account'),
        readonly=True,
        default=lambda self: self._get_commission_amt(),
    )
    comment = fields.Text(
        string='Comment',
    )

    @api.model
    def _get_commission_amt(self):
        CommissionWorksheet = self.env['commission.worksheet']
        worksheet = CommissionWorksheet.browse(self._context['active_id'])
        if worksheet:
            return worksheet.amount_valid
        return False

    @api.multi
    def create_commission_invoice(self):
        ctx = self._context.copy()
        form_data = self.read(['comment'])[0]
        ctx.update({'comment': form_data['comment']})
        CommissionWorksheet = self.env['commission.worksheet']
        commission_worksheet = CommissionWorksheet.browse([ctx['active_id']])
        return commission_worksheet.with_context(ctx).action_create_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
