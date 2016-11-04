# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp
from openerp import models, fields, api


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.multi
    @api.depends('user_id')
    def _get_section_id(self):
        team_obj = self.env['crm.case.section']
        for event in self:
            sales_team = False

            def get_sales_team(sales_team, team):
                if sales_team and sales_team == team.parent_id:
                    pass
                elif not sales_team:
                    sales_team = team
                return sales_team

            for team in team_obj.search([]):
                if team.user_id and team.user_id == self.user_id:
                    sales_team = get_sales_team(sales_team, team)
                for member in team.member_ids:
                    if member == self.user_id:
                        sales_team = get_sales_team(sales_team, team)
            self.section_id = sales_team


    section_id = fields.Many2one(
        'crm.case.section',
        string='Sales Team',
        compute='_get_section_id',
        store=True
    )


    # adding _get_section_id method above somehow triggers an error at event
    # creation for missing 'display_start' value.
    # Therefore, we make adjustment to the standard logic.
    @api.v7
    def get_search_fields(self, browse_event, order_fields, r_date=None):
        sort_fields = {}
        for ord in order_fields:
            if ord == 'id' and r_date:
                sort_fields[ord] = '%s-%s' % (
                browse_event[ord], r_date.strftime("%Y%m%d%H%M%S"))
            else:
                sort_fields[ord] = browse_event[ord]
                if type(browse_event[ord]) is openerp.osv.orm.browse_record:
                    name_get = browse_event[ord].name_get()
                    if len(name_get) and len(name_get[0]) >= 2:
                        sort_fields[ord] = name_get[0][1]
        if r_date:
            sort_fields['sort_start'] = r_date.strftime("%Y%m%d%H%M%S")
        else:
            #>>> Ecosoft adjust
            display_start = browse_event['display_start']
            sort_fields['sort_start'] = display_start and display_start.\
                replace(' ', '').replace('-', '') or False
            #<<< Ecosoft adjust
        return sort_fields
