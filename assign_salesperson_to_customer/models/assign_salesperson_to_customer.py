# -*- coding: utf-8 -*-

from openerp import api, models, fields


class assign_salesperson_to_customer(models.TransientModel):
    _name = 'assign_salesperson_to_customer'

    user_id = fields.Many2one(string='Salesperson', comodel_name='res.users')

    @api.model
    def change_user_id(self, current_id, context):

        if self.browse(current_id)[0].user_id:
            user_id = self.browse(current_id)[0].user_id.id
        else:
            return

        if not user_id:
            return

        if context['active_model'] == 'res.partner':
            partner_model = self.env['res.partner'].browse(context['active_ids'])
            partner_model.write({'user_id': user_id})
        elif context['active_model'] == 'crm.lead':
            lead_model = self.env['crm.lead'].browse(context['active_ids'])
            lead_model.write({'user_id': user_id})
