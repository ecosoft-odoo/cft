#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# try:
#     import simplejson as json
# except ImportError:
import json
import geocoder
import googlemaps
import requests
import os
import urllib2
import openerp
from openerp import models, fields, api


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # location_address = fields.Char(
    #     string='Address',
    # )

    @api.multi
    def button_check_in(self):
        self.ensure_one()
        action = self.env.ref(
            'calendar_event_location_cft.action_check_in')
        vals = action.read()[0]
        print("=============>", action)
        print("------------->", vals)


        # g = geocoder.ip('me')
        # print("==================================================>", g)
        # location = g.address
        # self.write({'location': location})
    # ^^^ this function show Bangkok, Thailand

        # API_KEY = 'AIzaSyB8rh1CrWaEfoaTirgByTkTxP8fd4tkaS4'
        # gmaps = googlemaps.Client(key=API_KEY)
        # locations = gmaps.geolocate()
        # latitude = locations['location']['lat']
        # longitude = locations['location']['lng']
        # g = geocoder.google([latitude, longitude], method='reverse')
        # get_json_values = g.json
        # my_current_position = get_json_values['address']
        # self.write({'location': my_current_position})
