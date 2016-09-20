# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.one
    @api.depends('planned_revenue', 'probability')
    def _compute_probable_revenue(self):
        self.probable_revenue = self.planned_revenue * self.probability / 100

    probable_revenue = fields.Float('Estimated Revenue',
                            compute=_compute_probable_revenue, store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: