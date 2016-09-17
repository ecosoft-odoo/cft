# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.onchange('user_id')
    def onchange_use_id(self):
        team_obj = self.env['crm.case.section']
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
    )
