# -*- coding: utf-8 -*-
from openerp import models, fields, api


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    claim_count = fields.Integer(
        string='# Claims',
        compute='_claim_count',
    )
    crm_claim_ids = fields.One2many(
        'crm.claim',
        'opportunity_id',
        string='Opportunity',
    )

    @api.multi
    @api.depends('crm_claim_ids', 'crm_claim_ids.opportunity_id')
    def _claim_count(self):
        Claim = self.env['crm.claim']
        for lead in self:
            claim = Claim.search([('opportunity_id', '=', lead.id)])
            lead.claim_count = len(claim)
