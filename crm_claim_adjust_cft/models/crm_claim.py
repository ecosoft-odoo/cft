# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CRMClaim(models.Model):
    _inherit = 'crm.claim'

    sale_ids = fields.Many2many(
        comodel_name='sale.order',
        string='Sales Order',
    )


class CrmClaimStage(models.Model):
    _inherit = 'crm.claim.stage'
