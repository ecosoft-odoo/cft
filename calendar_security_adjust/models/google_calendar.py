# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID


class GoogleCalendar(models.TransientModel):
    _inherit = 'google.calendar'

    @api.model
    def generate_data(self, event, isCreating=False):
        return super(GoogleCalendar, self).generate_data(
            event.sudo(), isCreating=isCreating)

    @api.v7
    def remove_references(self, cr, uid, context=None):
        # Overwrite
        current_user = self.pool["res.users"].browse(cr, SUPERUSER_ID, uid, context=context)
        reset_data = {
            "google_calendar_rtoken": False,
            "google_calendar_token": False,
            "google_calendar_token_validity": False,
            "google_calendar_last_sync_date": False,
            "google_calendar_cal_id": False,
        }

        all_my_attendees = self.pool["calendar.attendee"].search(cr, uid, [("partner_id", "=", current_user.partner_id.id)], context=context)
        self.pool["calendar.attendee"].write(cr, uid, all_my_attendees, {"oe_synchro_date": False, "google_internal_event_id": False}, context=context)
        self.pool.get("res.users").write(cr, SUPERUSER_ID, [current_user.id], reset_data, context=context)
        return True
