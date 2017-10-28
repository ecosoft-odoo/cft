# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
from openerp.addons.base.res import res_request


@api.model
def referencable_models(self):
    return res_request.referencable_models(
        self, self.env.cr, self.env.uid, context=self.env.context)


class CRMClaim(models.Model):
    _inherit = 'crm.claim'

    sale_ids = fields.Many2many(
        comodel_name='sale.order',
        string='Sales Order',
    )
    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Opportunities',
    )
    reference = fields.Char(
        string='Reference / Description',
    )
    ref2 = fields.Reference(
        string='Reference',
        selection=referencable_models,
    )
    ref3 = fields.Reference(
        string='Reference',
        selection=referencable_models,
    )


class CrmClaimStage(models.Model):
    _inherit = 'crm.claim.stage'
