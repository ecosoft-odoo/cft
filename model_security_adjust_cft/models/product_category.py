# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    section_ids = fields.Many2many(
        'crm.case.section',
        string='Sales Teams'
    )
