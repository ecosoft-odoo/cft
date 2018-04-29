# -*- coding: utf-8 -*-
from openerp import models, api


class AccountBilling(models.Model):
    _inherit = 'account.billing'

    @api.multi
    def validate_billing(self):
        # Call super
        super(AccountBilling, self).validate_billing()
        # Find doctype_id
        refer_type = 'billing'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        self.write({'number': self.env['ir.sequence'].next_by_doctype()})
