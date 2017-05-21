# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class AccountInvoiceTeam(models.Model):

    _name = 'account.invoice.team'

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        required=False,
        ondelete='cascade',
    )
    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        required=False,
    )
    sale_team_id = fields.Many2one(
        'sale.team',
        string='Team',
        required=False,
    )
    commission_rule_id = fields.Many2one(
        'commission.rule',
        string='Applied Commission',
        required=True,
        readonly=True,
    )

    @api.onchange('sale_team_id')
    def onchange_sale_team_id(self):
        if self.sale_team_id:
            self.commission_rule_id = self.sale_team_id.commission_rule_id.id
            self.salesperson_id = False

    @api.onchange('salesperson_id')
    def onchange_salesperson_id(self):
        if self.salesperson_id:
            self.commission_rule_id = self.salesperson_id.commission_rule_id.id
            self.sale_team_id = False


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    sale_team_ids = fields.One2many(
        'account.invoice.team',
        'invoice_id',
        string='Teams',
        states={'draft': [('readonly', False)]},
    )
    worksheet_id = fields.Many2one(
        'commission.worksheet',
        string='Commission worksheet',
        readonly=True,
    )

    @api.model
    def _get_salesperson_comm(self, salesperson):
        salesperson_recs = []
        if salesperson:
            if salesperson.commission_rule_id:
                salesperson_recs.append({
                    'salesperson_id': salesperson.id,
                    'commission_rule_id': salesperson.commission_rule_id.id})
        return salesperson_recs

    @api.model
    def _get_sale_team_comm(self, user):
        team_recs = []
        if user:
            self._cr.execute("""
                select a.tid team_id, b.tid as inherit_id
                from sale_team_users_rel a
                left outer join sale_team_implied_rel b on b.hid = a.tid
                where uid = %s """, (user.id,))
            team_ids = []
            for team_id, inherit_id in self._cr.fetchall():
                if team_id not in team_ids:
                    team_ids.append(team_id)
                if inherit_id:
                    if inherit_id not in team_ids:
                        team_ids.append(inherit_id)

                    def _get_all_inherited_team(team_ids, inherit_id):
                        self._cr.execute("""
                            select tid as interit_id from sale_team_implied_rel
                            where hid = %s and tid != hid """, (inherit_id,))
                        for team_id in self._cr.fetchall():
                            if team_id[0] not in team_ids:
                                team_ids.append(team_id[0])
                            team_ids = _get_all_inherited_team(team_ids,
                                                               team_id[0])
                        return team_ids

                    team_ids = _get_all_inherited_team(team_ids, inherit_id)

            teams = self.env['sale.team'].browse(team_ids)
            for team in teams:
                team_recs.append({
                    'sale_team_id': team.id,
                    'commission_rule_id': team.commission_rule_id.id, })
        return team_recs

    @api.onchange('user_id')
    def onchange_user_id(self):
        self.sale_team_ids = False
        if self.user_id:
            salespersons = self._get_salesperson_comm(self.user_id)
            sale_teams = self._get_sale_team_comm(self.user_id)
            self.sale_team_ids = salespersons + sale_teams

    @api.model
    def create(self, vals):
        if not vals.get('sale_team_ids', False):
            user = self.env['res.users'].browse(vals.get('user_id', False))
            salespersons = self._get_salesperson_comm(user)
            sale_teams = self._get_sale_team_comm(user)
            records = []
            for record in salespersons + sale_teams:
                records.append([0, False, record])
            vals.update({'sale_team_ids': records})
        return super(AccountInvoice, self).create(vals)

    # If invoice state changed, update commission line
    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if 'state' in vals:
            # Get commission line ids from these invoice ids
            CommissionLine = self.env['commission.worksheet.line']
            lines = CommissionLine.search([('invoice_id', 'in', self.ids)])
            if lines:
                lines.update_commission_line_status()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
