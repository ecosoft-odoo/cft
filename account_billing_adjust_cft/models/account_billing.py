# -*- coding: utf-8 -*-
#
#    Author: Kitti Upariphutthiphong
#    Copyright 2014-2015 Ecosoft Co., Ltd.
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
#


from openerp import models, fields, api, _


class AccountBillingAdjust(models.Model):
    _inherit = 'account.billing'

    @api.multi
    def onchange_partner_id(self, company_id,
                            partner_id, currency_id, date):
        ctx = self._context.copy()

        if not currency_id:
            return {'value': {'line_cr_ids': []}}
        res = self.with_context(ctx).recompute_billing_lines(
            company_id, partner_id, currency_id, date)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: