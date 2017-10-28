# -*- coding: utf-8 -*-
# Copyright 2016-2017 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class res_partner_rank(models.Model):
    _inherit = 'res.partner'

    customer_rank = fields.Many2one(
        'res.partner.rank',
        'Rank'
    )
    verified_partner = fields.Boolean(
        string='Verified Partner',
    )


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_sale_manager = fields.Boolean(
        string='Is Sale Manager?',
        compute='_set_is_sale_manager',
        default=lambda self: self._get_is_sale_manager(),
    )

    @api.model
    def _get_is_sale_manager(self):
        return self.env['res.users'].has_group('base.group_sale_manager')

    @api.multi
    def _set_is_sale_manager(self):
        for partner in self:
            partner.is_sale_manager = partner._get_is_sale_manager()
