# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID


class GoogleCalendar(models.TransientModel):
    _inherit = 'google.calendar'

    @api.model
    def generate_data(self, event, isCreating=False):
        return super(GoogleCalendar, self).generate_data(
            event.sudo(), isCreating=isCreating)
