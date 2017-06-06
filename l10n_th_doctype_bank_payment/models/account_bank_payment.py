# -*- coding: utf-8 -*-
from openerp import models, api


class AccountBankPayment(models.Model):
    _inherit = 'account.bank.payment'

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'bank_payment'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        return super(AccountBankPayment, self).create(vals)
