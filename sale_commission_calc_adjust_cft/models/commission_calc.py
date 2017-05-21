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


class CommissionWorksheet(models.Model):
    _inherit = 'commission.worksheet'

    kpi_criteria = fields.Boolean(
        string='KPI (Passed/Failed)',
        default=False,
    )
    sale_team_id = fields.Many2one(
        'crm.case.section',
    )

    @api.model
    def _calculate_categ_commission(self, invoice):
        categ_commission_amt = 0.0
        for line in invoice.invoice_line:
            percent_commission_categ = line.product_id.categ_id \
                                        .percent_commission
            categ_commission_rate = percent_commission_categ \
                and percent_commission_categ / 100 or 0.0
            if categ_commission_rate:
                categ_commission_amt += line.price_subtotal \
                                    * categ_commission_rate
        return categ_commission_amt

    @api.model
    def _calculate_customer_commission(self, invoice, base_amt):
        context = self._context.copy()
        cus_commission_amt = 0.0
        rank = invoice.partner_id and invoice.partner_id.customer_rank or False
        if rank:
            is_team = context.get('is_team', False)
            comm_percent = is_team and rank.sales_team_commission or \
                rank.salesperson_commission
            cus_commission_amt = base_amt * comm_percent / 100
        return cus_commission_amt

    @api.model
    def _calculate_invoice_comm_rate(self, target_amount, total_amount):
        context = self._context.copy()
        is_team = context.get('is_team', False)
        rate = False
        table = is_team and "teams_invoice_percent" or "sales_invoice_percent"
        self._cr.execute("select compare, target_percent, invoice_percent " +
                         "from " + table + " order by target_percent desc")
        for line in self._cr.fetchall():
            if line[0] == 'greater_than' and not rate:
                if total_amount > (line[1] / 100) * target_amount:
                    rate = is_team and line[2] or line[2] / 100
            elif line[0] == 'less_than':
                if total_amount < (line[1] / 100) * target_amount:
                    rate = is_team and line[2] or line[2] / 100
        return rate and rate or 0.0

    @api.model
    def _calculate_percent_sale(self, rule, worksheet, invoices):
        context = self._context.copy()
        is_team = context.get('is_team', False)
        worksheet_lines = []
        total_amount = 0.0
        target_amount = 0.0

        # Target Amount
        object = is_team and worksheet.sale_team_id or worksheet.salesperson_id
        for line in object.target_amount_ids:
            if worksheet.period_id.id == line.period_id.id:
                target_amount = line.target_amount
                break

        # Find Company
        ResCompany = self.env['res.company']
        company_id = ResCompany._company_default_get('CommissionWorksheet')
        company = ResCompany.browse(company_id)

        # Find total amount
        for invoice in invoices:
            total_amount += invoice.amount_untaxed

        # Find Invoice commission rate
        invoice_comm_rate = self._calculate_invoice_comm_rate(target_amount,
                                                              total_amount)

        # Calculate commission amount
        for invoice in invoices:
            base_amt = self._get_base_amount(invoice)
            commission_amt = 0.0
            # For Customer Commission Amount
            cus_commission_amt = self._calculate_customer_commission(invoice,
                                                                     base_amt)

            if not context.get('is_team', False):
                # For Category Commission Amount
                categ_commission_amt = self._calculate_categ_commission(
                                                invoice)
                kpi = worksheet.kpi_criteria and company.sales_kpi_pass \
                    or company.sales_kpi_fail
                commission_amt = (categ_commission_amt + cus_commission_amt +
                                  invoice_comm_rate * base_amt) * kpi
            else:
                kpi = worksheet.kpi_criteria and company.teams_kpi_pass \
                    or company.teams_kpi_fail
                if invoice.partner_id and invoice.partner_id.customer_rank:
                    rank = invoice.partner_id.customer_rank. \
                        sales_team_commission
                commission_amt = cus_commission_amt * rank / 100 * \
                    invoice_comm_rate * kpi

            res = self._prepare_worksheet_line(worksheet, invoice,
                                               base_amt, commission_amt)

            worksheet_lines.append((0, 0, res))
        worksheet.write({'worksheet_lines': worksheet_lines})
        return True

    @api.model
    def _calculate_percent_customer(self, rule, worksheet, invoices):
        worksheet_lines = []
        for invoice in invoices:
            base_amt = self._get_base_amount(invoice)
            commission_amt = self._calculate_customer_commission(invoice,
                                                                 base_amt)
            res = self._prepare_worksheet_line(worksheet, invoice,
                                               base_amt, commission_amt)
            worksheet_lines.append((0, 0, res))
        worksheet.write({'worksheet_lines': worksheet_lines})
        return True

    @api.model
    def _calculate_commission(self, rule, worksheet, invoices):
        if rule.type == 'percent_sale_commission':
            return self._calculate_percent_sale(rule, worksheet, invoices)
        if rule.type == 'percent_customer':
            return self._calculate_percent_customer(rule, worksheet, invoices)
        res = super(CommissionWorksheet, self)._calculate_commission(rule,
                                                                     worksheet,
                                                                     invoices)
        return res
