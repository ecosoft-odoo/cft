# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class res_partner_rank_extension(models.Model):
    _name = 'res.partner.rank'
    _order = 'name'
    name = fields.Char(
        'Rank',
        required=True,
    )
    description = fields.Char(
        'Description'
    )
    for_sale_manager = fields.Boolean(
        string='Used by Sales Manager only',
        default=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
