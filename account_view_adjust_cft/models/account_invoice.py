# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def amount_to_text_th(self, amount, currency="BAHT"):
        return amount_to_text_th(amount, currency)
