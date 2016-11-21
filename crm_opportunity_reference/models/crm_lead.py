# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sale_order_ids = fields.One2many(
        'sale.order',
        'opportunity_id',
        string='Sales Orders'
    )
    reference_ids = fields.Many2many(
        'res.partner',
        'opportunity_id',
        string='References'
    )
