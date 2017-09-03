# -*- coding: utf-8 -*-
from openerp import models, fields, api


class CRMLead(models.Model):
    _inherit = 'crm.lead',

    province_id = fields.Many2one(
        'res.country.province',
        domain="[('country_id','=',country_id)]",
        ondelete='restrict'
    )
    district_id = fields.Many2one(
        'res.country.district',
        domain="[('province_id','=',province_id)]",
        ondelete='restrict'
    )
    township_id = fields.Many2one(
        'res.country.township',
        domain="[('district_id','=',district_id)]",
        ondelete='restrict'
    )

    @api.onchange('township_id')
    def _onchange_township_id(self):
        township = self.township_id
        if township:
            self.zip = township.zip
            self.province_id = township.province_id and township.province_id.id
            self.district_id = township.district_id and township.district_id.id
            self.country_id = township.country_id and township.country_id.id
