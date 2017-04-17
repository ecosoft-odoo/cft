# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class assign_salesperson_to_customer(models.TransientModel):
    _name = 'assign_salesperson_to_customer'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesperson',
        required=True,
    )
    section_id = fields.Many2one(
        comodel_name='crm.case.section',
        string='Sales Team',
        required=True,
    )


    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.section_id = self.user_id.default_section_id
        else:
            self.section_id = False

    @api.model
    def change_user_id(self, current_id, context):
        user_id = self.browse(current_id)[0].user_id.id
        section_id = self.browse(current_id)[0].section_id.id
        if context['active_model'] == 'res.partner':
            recs = self.env['res.partner'].browse(context['active_ids'])
        elif context['active_model'] == 'crm.lead':
            recs = self.env['crm.lead'].browse(context['active_ids'])
        recs.write({
            'user_id': user_id,
            'section_id': section_id,
        })
