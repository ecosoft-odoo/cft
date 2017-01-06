# -*- coding: utf-8 -*-
# Copyright 2017 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountBillingAdjust(models.Model):
    _inherit = 'account.billing'

# overriding the method to remove billing_date_condition
# so that all the outstanding invoices for the customer
# can be listed up when applying billing function
    @api.multi
    def onchange_partner_id(self, company_id,
                            partner_id, currency_id, date):
        ctx = self._context.copy()
        # ctx.update(
        #    {'billing_date_condition': ['|',
        #                               ('date_maturity', '=', False),
        #                              ('date_maturity', '<=', date)]}
        # )
        if not currency_id:
            return {'value': {'line_cr_ids': []}}
        res = self.with_context(ctx).recompute_billing_lines(
            company_id, partner_id, currency_id, date)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: