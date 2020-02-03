# -*- coding: utf-8 -*-
# Copyright 2020 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

UNIT = dp.get_precision("Location (CFT)")


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    latitude = fields.Float(
        string="Latitude",
        digits=UNIT,
        readonly=True,
        copy=False,
    )
    longitude = fields.Float(
        string="Longitude",
        digits=UNIT,
        readonly=True,
        copy=False,
    )
    location = fields.Char(
        copy=False,
    )

    @api.multi
    def button_check_in(self):
        return True

    @api.multi
    def view_map(self):
        self.ensure_one()
        q = self.location
        if self.latitude and self.longitude:
            q = '%s,%s' % (self.latitude, self.longitude)
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://www.google.com/maps?q=%s' % (q, ),
            'target': 'new',
        }
