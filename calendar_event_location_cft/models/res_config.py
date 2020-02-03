# -*- coding: utf-8 -*-
# Copyright 2020 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    google_map_api_key = fields.Char(
        string='API Key',
    )

    @api.multi
    def set_google_map_api_key(self):
        params = self.env['ir.config_parameter']
        params.set_param(
            'google_map_api_key', (self.google_map_api_key or '').strip(),
            groups=['base.group_system'])

    @api.multi
    def get_default_google_map_api_key(self):
        params = self.env['ir.config_parameter']
        google_map_api_key = params.get_param('google_map_api_key', default='')
        return {'google_map_api_key': google_map_api_key}
