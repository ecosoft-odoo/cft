# -*- coding: utf-8 -*-
from openerp import models, fields, api


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def force_cancel(self):
        # self.write({'state': 'cancel'})
        self.signal_workflow('force_cancel')
        return True
