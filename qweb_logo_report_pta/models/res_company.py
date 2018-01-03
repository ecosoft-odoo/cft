# -*- coding: utf-8 -*-
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    logo_qweb = fields.Binary(
        string="Custom Logo",
    )
