# -*- coding: utf-8 -*-
from openerp import models, api


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _lead_create_contact(self, lead, name, is_company, parent_id=False):
        partner_id = super(CRMLead, self)._lead_create_contact(
            lead, name, is_company, parent_id=parent_id
        )
        partner = self.env['res.partner'].browse(partner_id)
        vals = {
            'province_id': lead.province_id.id or False,
            'district_id': lead.district_id.id or False,
            'township_id': lead.township_id.id or False,
        }
        partner.write(vals)
        return partner_id
