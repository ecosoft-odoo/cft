# coding=utf-8
##############################################################################
#
#    account_auto_fy_sequence module for Odoo
#    Copyright (C) 2014 ACSONE SA/NV (<http://acsone.eu>)
#    @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
#
#    account_auto_fy_sequence is free software:
#    you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License v3 or later
#    as published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    account_auto_fy_sequence is distributed
#    in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License v3 or later for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    v3 or later along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_sale_team_comm(self, user):
        team_recs = []
        if user:
            self._cr.execute("""
             select section.id team_id, section.commission_rule_id rule_id
             from crm_case_section section
             left outer join sale_member_rel rel on rel.section_id = section.id
             left outer join res_users users on users.id = rel.member_id
             where users.id = %s""", (user.id,))
            for team_id, rule_id in self._cr.fetchall():
                if rule_id:
                    team_recs.append({
                        'sale_team_id': team_id,
                        'commission_rule_id': rule_id,
                    })
        return team_recs


class AccountInvoiceTeam(models.Model):
    _inherit = 'account.invoice.team'

    sale_team_id = fields.Many2one(
        'crm.case.section',
    )
