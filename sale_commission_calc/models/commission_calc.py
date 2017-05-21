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
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm

# Define the due date available for any commission rule
LAST_PAY_DATE_RULE = [
    ('invoice_duedate', 'Invoice Due Date (default)'),
    ('invoice_date_plus_cust_payterm', 'Invoice Date + Customer Payment Term'),
]

COMMISSION_LINE_STATE = [('draft', 'Not Ready'),
                         ('valid', 'Ready'),
                         ('invalid', 'Invalid'),
                         ('done', 'Done'),
                         ('skip', 'Skipped'), ]


class SaleTeam(models.Model):

    _name = 'sale.team'
    _description = 'Sales Team'

    name = fields.Char(
        string='Name',
        size=64,
        required=True,
    )
    commission_rule_id = fields.Many2one(
        'commission.rule',
        string='Commission Rule',
        required=False,
    )
    users = fields.Many2many(
        'res.users',
        'sale_team_users_rel', 'tid', 'uid',
        string='Users',
    )
    implied_ids = fields.Many2many(
        'sale.team',
        'sale_team_implied_rel', 'tid', 'hid',
        string='Inherits',
        help="Users of this group automatically inherit those groups",
    )
    require_paid = fields.Boolean(
        string='Require Paid Invoice',
        help="Require invoice to be paid in full amount.",
        default=False,
    )
    require_posted = fields.Boolean(
        string='Require Payment Detail Posted',
        help="Require that all payment detail related "
        "to payments to invoice has been posted.",
        default=False,
    )
    allow_overdue = fields.Boolean(
        string='Allow overdue payment',
        help="Allow paying commission with overdue payment.",
        default=False,
    )
    last_pay_date_rule = fields.Selection(
        LAST_PAY_DATE_RULE,
        string='Last Pay Date Rule',
    )
    buffer_days = fields.Integer(
        string='Buffer Days',
        help="Additional days after last payment date "
        "to be eligible for commission.",
        default=0,
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the team must be unique !')
    ]


class CommissionWorksheet(models.Model):

    _name = 'commission.worksheet'
    _description = 'Commission Worksheet'
    _order = 'id desc'

    name = fields.Char(
        string='Name',
        size=64,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/',
    )
    sale_team_id = fields.Many2one(
        'sale.team',
        string='Team',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self._get_period(),
    )
    worksheet_lines = fields.One2many(
        'commission.worksheet.line',
        'worksheet_id',
        string='Calculation Lines',
        ondelete='cascade',
        readonly=False,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')],
        string='Status',
        required=True,
        readonly=True,
        help="* The \'Draft\' status is set when the work sheet "
             "in draft status."
             "\n* The \'Confirmed\' status is set when the work sheet is "
             "confirmed by related parties."
             "\n* The \'Done\' status is set when the work sheet is ready to "
             "pay for commission. This state can not be undone."
             "\n* The \'Cancelled\' status is set when "
             "a user cancel the work sheet.",
        default='draft',
    )
    invoice_ids = fields.One2many(
        'account.invoice',
        'worksheet_id',
        string='Invoices',
        readonly=True,
    )
    amount_draft = fields.Float(
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        string='Not Ready',
        store=True,
    )
    amount_valid = fields.Float(
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        string='Ready',
        store=True,
    )
    amount_invalid = fields.Float(
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        string='Invalid',
        store=True,
    )
    amount_done = fields.Float(
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        string='Done',
        store=True,
    )
    amount_skip = fields.Float(
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        string='Skipped',
        store=True,
    )
    amount_total = fields.Float(
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        string='Total Amount',
        store=True,
    )
    commission_rule_id = fields.Many2one(
        'commission.rule',
        compute='_compute_other_info',
        string='Applied Commission',
    )
    last_pay_date_rule = fields.Selection(
        LAST_PAY_DATE_RULE,
        compute='_compute_other_info',
        string='Last Pay Date Rule',
    )
    require_paid = fields.Boolean(
        compute='_compute_other_info',
        string='Require Paid Invoice',
    )
    require_posted = fields.Boolean(
        compute='_compute_other_info',
        string='Require Payment Detail Posted',
    )
    allow_overdue = fields.Boolean(
        compute='_compute_other_info',
        string='Allow Overdue Payment',
    )
    buffer_days = fields.Integer(
        compute='_compute_other_info',
        string='Buffer Days',
    )

    _sql_constraints = [
        ('unique_sale_team_period',
         'unique(sale_team_id, period_id)', 'Duplicate Sale Team / Period'),
        ('unique_salesperson_period',
         'unique(salesperson_id, period_id)', 'Duplicate Salesperson / Period')
    ]

    @api.model
    def _get_period(self):
        context = self._context.copy()
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.env['account.period'].with_context(ctx).find()
        return periods and periods[0] or False

    @api.multi
    @api.depends('worksheet_lines.done',
                 'worksheet_lines.force',
                 'worksheet_lines.adjust_amt',
                 'worksheet_lines.commission_state',
                 'worksheet_lines.invoice_id.state')
    def _amount_all(self):
        for worksheet in self:
            worksheet.amount_draft = 0.0
            worksheet.amount_valid = 0.0
            worksheet.amount_invalid = 0.0
            worksheet.amount_done = 0.0
            worksheet.amount_skip = 0.0
            worksheet.amount_total = 0.0
            total = 0.0
            # Update line status first.
            worksheet.worksheet_lines.update_commission_line_status()
            # Start calculation.
            for line in worksheet.worksheet_lines:
                if line.commission_state == 'draft':
                    worksheet.amount_draft += line.amount_subtotal
                if line.commission_state == 'valid':
                    worksheet.amount_valid += line.amount_subtotal
                if line.commission_state == 'invalid':
                    worksheet.amount_invalid += line.amount_subtotal
                if line.commission_state == 'done':
                    worksheet.amount_done += line.amount_subtotal
                if line.commission_state == 'skip':
                    worksheet.amount_skip += line.amount_subtotal
                total += line.amount_subtotal
            worksheet.amount_total = total

    @api.multi
    @api.depends()
    def _compute_other_info(self):
        for sheet in self:
            object = sheet.salesperson_id or sheet.sale_team_id or False
            if object:
                self.commission_rule_id = object.commission_rule_id and \
                    object.commission_rule_id.id or False
                self.last_pay_date_rule = object.last_pay_date_rule
                self.require_paid = object.require_paid
                self.require_posted = object.require_posted
                self.allow_overdue = object.allow_overdue
                self.buffer_days = object.buffer_days

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            IrSequence = self.env['ir.sequence']
            vals['name'] = IrSequence.get('commission.worksheet') or '/'
        return super(CommissionWorksheet, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_confirm(self):
        # Only if today has passed the period, allow to confirm
        warning = "You cannot confirm this worksheet. Period not yet over!"
        for worksheet in self:
            period = worksheet.period_id
            if time.strftime('%Y-%m-%d') <= period.date_stop:
                raise except_orm(_('Warning!'), _(warning))
        # Confirm all worksheet
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def action_cancel(self):
        # Only allow cancel if no commission has been paid yet.
        warning = "Worksheet(s) has issued commission(s) \
                   and can not be cancelled!"
        WorksheetLine = self.env['commission.worksheet.line']
        for worksheet in self:
            lines = WorksheetLine.search([('worksheet_id', '=', worksheet.id),
                                          ('done', '=', True)])
            if lines:
                raise except_orm(_('Warning!'), _(warning))
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True

    @api.model
    def _get_matched_invoices_by_period(self, salesperson_id,
                                        sale_team_id, period):
        res_id = salesperson_id or sale_team_id
        condition = salesperson_id and 't.salesperson_id = %s' \
            or 't.sale_team_id = %s'
        self._cr.execute("select ai.id from account_invoice ai \
                         join account_invoice_team t on ai.id = t.invoice_id \
                         where ai.state in ('open','paid') \
                         and ai.type in ('out_invoice','out_refund') \
                         and date_invoice >= %s and date_invoice <= %s \
                         and " + condition + " order by ai.id",
                         (period.date_start, period.date_stop, res_id))
        invoice_ids = map(lambda x: x[0], self._cr.fetchall())
        return invoice_ids

    @api.multi
    def action_calculate(self):
        WorksheetLine = self.env['commission.worksheet.line']
        Invoice = self.env['account.invoice']

        # For each work sheet, reset the calculation
        error = "No commission rule specified for this salesperson/team!"
        for worksheet in self:
            salesperson = worksheet.salesperson_id
            team = worksheet.sale_team_id
            salesperson_id = salesperson and salesperson.id or False
            sale_team_id = team and team.id or False
            period = worksheet.period_id
            if not (salesperson_id or sale_team_id) or not period:
                continue
            rule = (salesperson and salesperson.commission_rule_id) \
                or (team and team.commission_rule_id)
            if not rule:
                raise except_orm(_('Error!'), _(error))

            # Delete old lines
            wl = WorksheetLine.search([('worksheet_id', '=', worksheet.id)])
            wl.unlink()

            # Search for matched Completed Invoice for this work sheet
            # (either salesperson or sales team)
            invoice_ids = self._get_matched_invoices_by_period(salesperson_id,
                                                               sale_team_id,
                                                               period)
            invoices = Invoice.browse(invoice_ids)
            self._calculate_commission(rule, worksheet, invoices)
        return True

    @api.model
    def final_update_invoice(self, inv_rec):
        # Prepare for hook
        return inv_rec

    @api.model
    def final_update_invoice_line(self, inv_rec_line):
        # Prepare for hook
        return inv_rec_line

    @api.multi
    def action_create_invoice(self):
        ctx = self._context.copy()
        ctx.update({'type': 'in_invoice'})
        WorksheetLine = self.env['commission.worksheet.line']
        Inv = self.env['account.invoice']
        InvLine = self.env['account.invoice.line']
        invoice_ids = []
        product_id = self._get_product_commission()
        for worksheet in self:
            users = []
            if worksheet.salesperson_id:
                users = [worksheet.salesperson_id]
            elif worksheet.sale_team_id:
                users = worksheet.sale_team_id.users
            else:
                continue

            lines = WorksheetLine.search([('worksheet_id', '=', worksheet.id),
                                          ('commission_state', '=', 'valid')])
            if not lines:
                raise except_orm(_('Warning!'),
                                 _("No Commission Invoice(s) can be created \
                                 for Worksheet %s" % (worksheet.name)))

            # Create invoice for each sale person in team
            for user in users:
                # initial value of invoice
                inv_rec = Inv.with_context(ctx).default_get([
                    'type', 'state', 'journal_id', 'currency_id', 'company_id',
                    'reference_type', 'check_total', 'internal_number',
                    'user_id', 'sent'])
                inv_rec.update(Inv.onchange_partner_id(
                                   'in_invoice', user.partner_id.id,
                                   company_id=inv_rec['company_id'])['value'])
                inv_rec.update({'origin': worksheet.name,
                                'worksheet_id': worksheet.id,
                                'type': 'in_invoice',
                                'partner_id': user.partner_id.id,
                                'date_invoice': time.strftime('%Y-%m-%d'),
                                'comment': ctx.get('comment', False)})
                inv_rec = self.with_context(ctx).final_update_invoice(inv_rec)
                invoice = Inv.with_context(ctx).create(inv_rec)
                invoice_ids.append(invoice.id)
                for line in lines:
                    # initial value of invoice lines
                    inv_line_rec = (InvLine.product_id_change(
                                    product_id, False, 1, name=False,
                                    type='in_invoice',
                                    partner_id=user.partner_id.id,
                                    fposition_id=False,
                                    price_unit=0,
                                    currency_id=inv_rec['currency_id'],
                                    company_id=inv_rec['company_id'])['value'])
                    inv_line_rec.update({
                        'name': _('Period: ') + worksheet.period_id.name +
                        _(', Invoice: ') + line.invoice_id.number,
                        'origin': worksheet.name,
                        'invoice_id': invoice.id,
                        'product_id': product_id,
                        'partner_id': user.partner_id.id,
                        'company_id': inv_rec['company_id'],
                        'currency_id': inv_rec['currency_id'],
                        'price_unit': line.amount_subtotal,
                        'price_subtotal': line.amount_subtotal, })
                    InvLine.with_context(ctx).create(inv_line_rec)
                    # Update worksheet line was paid commission
                    line.with_context(ctx).write({'done': True,
                                                  'commission_state': 'done'})
            if WorksheetLine.search_count([('worksheet_id', '=', worksheet.id),
                                           ('commission_state', 'in',
                                            ('draft', 'valid'))]) <= 0:
                # All worksheet lines has been paid will update state
                # of worksheet is done.
                worksheet.write({'state': 'done'})
        # Show new Invoice
        Mod = self.env['ir.model.data']
        Act = self.env['ir.actions.act_window']
        result = Mod.get_object_reference('account', 'action_invoice_tree2')
        id = result and result[1] or False
        act = Act.browse([id])
        result = act.with_context(ctx).read()[0]
        result['domain'] = "[('id','in', [" + ',' \
            .join(map(str, invoice_ids)) + "])]"
        result['name'] = 'Commission invoice(s)'
        return result

    @api.model
    def _calculate_commission(self, rule, worksheet, invoices):
        if rule.type == 'percent_fixed':
            return self._calculate_percent_fixed(rule, worksheet, invoices)
        if rule.type == 'percent_product_category':
            return self._calculate_percent_product_category(rule, worksheet,
                                                            invoices)
        if rule.type == 'percent_product':
            return self._calculate_percent_product(rule, worksheet, invoices)
        if rule.type == 'percent_product_step':
            return self._calculate_percent_product_step(rule, worksheet,
                                                        invoices)
        if rule.type == 'percent_amount':
            return self._calculate_percent_amount(rule, worksheet, invoices)
        # No matched rule return False as signal.
        return False

    @api.model
    def _prepare_worksheet_line(self, worksheet, invoice, base_amt,
                                commission_amt):
        # Invoice or Refund
        sign = invoice.type == 'out_refund' and -1 or 1
        res = {
            'worksheet_id': worksheet.id,
            'invoice_id': invoice.id,
            'date_invoice': invoice.date_invoice,
            'invoice_amt': base_amt * sign,
            'commission_amt': commission_amt * sign,
        }
        return res

    @api.model
    def _get_base_amount(self, invoice):
        # Generic case
        base_amt = invoice.amount_untaxed
        return base_amt
    # --- This sections provide logics for each rules ---

    # COMMENT ****** Please do performance tuning on create Worksheet Line

    @api.model
    def _calculate_percent_fixed(self, rule, worksheet, invoices):
        commission_rate = rule.fix_percent / 100
        worksheet_lines = []
        for invoice in invoices:
            base_amt = self._get_base_amount(invoice)
            # For each order, find its match rule line
            commission_amt = 0.0
            if commission_rate:
                commission_amt = base_amt * commission_rate
            res = self._prepare_worksheet_line(worksheet, invoice,
                                               base_amt, commission_amt)
            worksheet_lines.append((0, 0, res),)
        worksheet.write({'worksheet_lines': worksheet_lines})
        return True

    @api.model
    def _calculate_percent_product_category(self, rule, worksheet, invoices):
        commission_rate = 0.0
        worksheet_lines = []
        for invoice in invoices:
            base_amt = self._get_base_amount(invoice)
            # For each product line
            commission_amt = 0.0
            for line in invoice.invoice_line:
                percent_commission = line.product_id.categ_id \
                                     .percent_commission
                commission_rate = percent_commission \
                    and percent_commission / 100 or 0.0
                if commission_rate:
                    commission_amt += line.price_subtotal * commission_rate
            res = self._prepare_worksheet_line(worksheet, invoice,
                                               base_amt, commission_amt)
            worksheet_lines.append((0, 0, res),)
        worksheet.write({'worksheet_lines': worksheet_lines})
        return True

    @api.model
    def _calculate_percent_product(self, rule, worksheet, invoices):
        commission_rate = 0.0
        worksheet_lines = []
        for invoice in invoices:
            base_amt = self._get_base_amount(invoice)
            # For each product line
            commission_amt = 0.0
            for line in invoice.invoice_line:
                # Make sure the product price each the limit_price,
                # before assign commission
                percent_commission = (line.price_unit >=
                                      line.product_id.limit_price) \
                                     and line.product_id.percent_commission \
                                     or 0.0
                commission_rate = percent_commission \
                    and percent_commission / 100 or 0.0
                if commission_rate:
                    commission_amt += line.price_subtotal * commission_rate
            res = self._prepare_worksheet_line(worksheet, invoice,
                                               base_amt, commission_amt)
            worksheet_lines.append((0, 0, res),)
        worksheet.write({'worksheet_lines': worksheet_lines})
        return True

    @api.model
    def _calculate_percent_product_step(self, rule, worksheet, invoices):
        commission_rate = 0.0
        ProductUom = self.env['product.uom']
        worksheet_lines = []
        for invoice in invoices:
            base_amt = self._get_base_amount(invoice)
            # For each product line
            commission_amt = 0.0
            for line in invoice.invoice_line:
                percent_commission = 0.0
                # Getting steps commission
                product = line.product_id
                if not product:
                    continue
                default_uom = product.uom_id and product.uom_id.id
                q = ProductUom._compute_qty(line.uos_id.id, 1, default_uom)
                uom_price_unit = line.price_unit / (q or 1.0)
                if product.rate_step_ids:
                    rate_steps = [(x.amount_over, x.percent_commission)
                                  for x in product.rate_step_ids]
                    rate_steps = sorted(rate_steps, reverse=True)
                    for rate_step in rate_steps:
                        if uom_price_unit >= rate_step[0]:
                            percent_commission = rate_step[1]
                            break
                        else:
                            continue
                commission_rate = percent_commission \
                    and percent_commission / 100 or 0.0
                if commission_rate:
                    commission_amt += line.price_subtotal * commission_rate
            res = self._prepare_worksheet_line(worksheet, invoice,
                                               base_amt, commission_amt)
            worksheet_lines.append((0, 0, res),)
        worksheet.write({'worksheet_lines': worksheet_lines})
        return True

    @api.model
    def _calculate_percent_amount(self, rule, worksheet, invoices):
        worksheet_lines = []
        for invoice in invoices:
            base_amt = self._get_base_amount(invoice)
            # For each order, find its match rule line
            commission_amt = 0.0
            ranges = rule.rule_rates
            for range in ranges:
                commission_rate = range.percent_commission / 100
                if base_amt <= range.amount_upto:
                    commission_amt = base_amt * commission_rate
                    break
            res = self._prepare_worksheet_line(worksheet, invoice,
                                               base_amt, commission_amt)
            worksheet_lines.append((0, 0, res),)
        worksheet.write({'worksheet_lines': worksheet_lines})
        return True

    # --- END ---

    @api.model
    def _get_product_commission(self):
        IrModelData = self.env['ir.model.data']
        product = IrModelData.get_object('sale_commission_calc',
                                         'product_product_commission')
        return product.id


class CommissionWorksheetLine(models.Model):

    _name = "commission.worksheet.line"
    _description = "Commission Worksheet Lines"
    _order = 'id'

    worksheet_id = fields.Many2one(
        'commission.worksheet',
        string='Commission Worksheet',
        ondelete='cascade',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='invoice_id.partner_id',
        readonly=True,
    )
    date_invoice = fields.Date(
        string='Invoice Date',
        readonly=True,
    )
    invoice_amt = fields.Float(
        string='Amount',
        readonly=True,
    )
    commission_amt = fields.Float(
        string='Commission',
        readonly=True,
    )
    adjust_amt = fields.Float(
        string='Adjust',
        readonly=True,
        states={'confirmed': [('readonly', False)]},
        help="Adjustment can be both positive or negative",
    )
    amount_subtotal = fields.Float(
        compute='_amount_subtotal',
        digits_compute=dp.get_precision('Account'),
        string='Total',
        store=True,
    )
    invoice_state = fields.Selection(
        [('open', 'Open'), ('paid', 'Paid'), ('cancel', 'Cancelled')],
        string='Status',
        related='invoice_id.state',
        readonly=True,
    )
    paid_date = fields.Date(
        string='Paid Date',
        readonly=True,
        help="The date of payment that make this invoice marked as paid",
    )
    last_pay_date = fields.Date(
        string='Due Date',
        readonly=True,
        help="Last payment date that will make commission valid. "
             "This date is calculated by the due date condition",
    )
    overdue = fields.Boolean(
        string='Overdue',
        readonly=True,
        help="For the paid invoice, is it over due?",
    )
    commission_state = fields.Selection(
        COMMISSION_LINE_STATE,
        string='State',
        readonly=True,
    )
    posted = fields.Boolean(
        string='Posted',
        readonly=True,
        help="This flag show whether all payment has been posted "
             "as Payment Details",
    )
    done = fields.Boolean(
        string='Done',
        readonly=True,
        help="This flag show whether the commission has been issued.",
        default=False,
    )
    force = fields.Selection(
        [('skip', 'Skip'), ('allow', 'Allow')],
        string='Force',
        readonly=True,
        states={'confirmed': [('readonly', False)]},
    )
    note = fields.Text(
        string='Note',
        help="Reason for forcing",
        readonly=True,
        states={'confirmed': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('done', 'Done'), ('cancel', 'Cancelled')],
        string='Worksheet State',
        related='worksheet_id.state',
    )

    @api.multi
    @api.depends('commission_amt', 'adjust_amt')
    def _amount_subtotal(self):
        for line in self:
            line.amount_subtotal = line.commission_amt + line.adjust_amt

    @api.model
    def _get_date_maturity(self, invoice, date_start):
        payment_term_id = invoice.partner_id.property_payment_term \
                              and invoice.partner_id.property_payment_term.id \
                              or False
        if payment_term_id:
            AccountPaymentTerm = self.env['account.payment.term']
            pterm_list = AccountPaymentTerm.compute(payment_term_id, value=1,
                                                    date_ref=date_start)
            if pterm_list:
                pterm_list = [l[0] for l in pterm_list]
                pterm_list.sort()
                date_maturity = pterm_list[-1]
                return date_maturity
        return False

    @api.model
    def _calculate_last_pay_date(self, rule, invoice):
        if rule == 'invoice_duedate':
            return invoice.date_due
        elif rule == 'invoice_date_plus_cust_payterm':
            date_start = invoice.date_invoice
            return self._get_date_maturity(invoice, date_start) \
                or invoice.date_due
        else:
            return None

    @api.multi
    def _get_commission_params(self):
        res = {
            'require_paid': False,
            'require_posted': False,
            'allow_overdue': False,
            'last_pay_date_rule': False,
            'buffer_days': 0,
        }
        if self:
            worksheet = self[0].worksheet_id
            i = worksheet.salesperson_id or worksheet.sale_team_id
            if i:
                res['require_paid'] = i.require_paid
                res['require_posted'] = i.require_posted
                res['allow_overdue'] = i.allow_overdue
                res['last_pay_date_rule'] = i.last_pay_date_rule
                res['buffer_days'] = i.buffer_days
        return res

    @api.model
    def _get_invoice_related_payment_amt(self, invoice):
        """
        This method will get amount of all payment related to this invoice.
        Note that, the amount will also cover other invoices
        """
        ids = [x.id for x in invoice.payment_ids]
        if not ids:
            return 0.0
        self._cr.execute("select sum(av.amount) from account_voucher av \
                        where av.id in ( \
                           select mv.id from account_move_line ml \
                           inner join account_move m on m.id = ml.move_id \
                           inner join account_voucher mv on mv.move_id = m.id \
                           where ml.id in %s \
                        ) \
                        and state = 'posted'", (tuple(ids),))
        sum_payments = ids and self._cr.fetchone()[0] or 0.0
        return sum_payments

    @api.model
    def _get_invoice_related_payment_detail_amt(self, invoice):
        """
        This method will get amount of all payment details related
        to this invoice. Note that, the amount will also cover other invoices
        """
        ids = [x.id for x in invoice.payment_ids]
        if not ids:
            return 0.0
        self._cr.execute("select sum(pd.amount) from payment_register pd \
                       inner join account_voucher av on av.id = pd.voucher_id \
                       where av.id in ( \
                           select mv.id from account_move_line ml \
                           inner join account_move m on m.id = ml.move_id \
                           inner join account_voucher mv on mv.move_id = m.id \
                           where ml.id in %s \
                       ) \
                       and pd.state = 'posted'", (tuple(ids),))
        sum_registers = ids and self._cr.fetchone()[0] or 0.0
        return sum_registers

    @api.model
    def _is_pay_posted(self, invoice):
        payment_amt = self._get_invoice_related_payment_amt(invoice) or 0.0
        paid_amt = self._get_invoice_related_payment_detail_amt(invoice) or 0.0
        # Payment is posted if total in posted payment_details >= total pay
        # about in payments
        if paid_amt >= payment_amt:
            return True
        return False

    @api.model
    def _check_commission_line_status(self, line, params):
        res = {}
        # Params
        require_paid = params['require_paid']
        require_posted = params['require_posted']
        allow_overdue = params['allow_overdue']
        last_pay_date_rule = params['last_pay_date_rule']
        buffer_days = params['buffer_days']
        # Checks
        invoice = line.invoice_id
        # Calculate each field,
        # 1) paid_date
        paid_date = invoice.state == 'paid' and invoice.payment_ids \
            and invoice.payment_ids[-1].date or None
        # 2) last_pay_date
        last_pay_date = self._calculate_last_pay_date(last_pay_date_rule,
                                                      invoice)
        # Add buffer
        days = buffer_days or 0
        last_pay_date = (datetime.strptime(last_pay_date, '%Y-%m-%d') +
                         relativedelta(days=days)).strftime('%Y-%m-%d')
        # 3) posted payment?
        # 3.1) invoie's payment and paid amount

        # required payment register #
        # posted = invoice.state == 'paid' and self._is_pay_posted(invoice)
        # or False
        # -- #
        posted = True

        # 4) is overdue
        # If allow commission overdue, this will never be overdue.
        # Else, check paid_date against last pay date
        overdue = not allow_overdue and \
            last_pay_date and \
            paid_date and \
            (datetime.strptime(paid_date, '%Y-%m-%d') >
             datetime.strptime(last_pay_date, '%Y-%m-%d')) or \
            False
        # 5) commission_state
        state = 'draft'
        if line.done:
            # Done, always done and do nothing.
            state = 'done'
        elif line.invoice_state == 'cancel':
            # Cancelled invoice, always invalid
            state = 'invalid'
        elif line.force == 'skip':
            # Skip, always skip.
            state = 'skip'
        elif line.force == 'allow':
            # Allow, always valid.
            state = 'valid'
        elif line.invoice_state == 'open':
            # Allow unpaid, always valid.
            if not require_paid:
                state = 'valid'
        elif line.invoice_state == 'paid':
            if posted:
                if not overdue:
                    # Paid + posted + Not Overdue
                    state = 'valid'
                else:
                    if allow_overdue:
                        # Paid + posted + Overdue, but allow over due
                        state = 'valid'
                    else:
                        # otherwise invalid
                        state = 'invalid'
            else:
                if not require_posted:
                    if not overdue:
                        # Paid + posted + Not Overdue
                        state = 'valid'
                    else:
                        if allow_overdue:
                            # Paid + posted + Overdue, but allow over due
                            state = 'valid'
                        else:
                            # otherwise invalid
                            state = 'invalid'
                else:
                    # Paid + Not posted
                    state = 'draft'
        # Updates
        res = {
            'paid_date': paid_date,
            'last_pay_date': last_pay_date,
            'posted': posted,
            'overdue': overdue,
            'commission_state': state
        }
        return res

    @api.multi
    def update_commission_line_status(self):
        res = {}
        # Prepare parameter from worksheet
        params = self._get_commission_params()
        # For each worksheet line,
        for line in self:

            # If Not Invoice Lines
            if not line.invoice_id:
                return True
            res = self._check_commission_line_status(line, params)
            self._cr.execute('update commission_worksheet_line set \
                                  paid_date = %s, \
                                  last_pay_date = %s, \
                                  posted = %s, \
                                  overdue = %s, \
                                  commission_state = %s \
                              where id = %s', (res['paid_date'],
                                               res['last_pay_date'],
                                               res['posted'],
                                               res['overdue'],
                                               res['commission_state'],
                                               line.id))
        return True

    @api.multi
    def unlink(self):
        lines = self.search([('id', 'in', self.ids), ('done', '=', True)])
        if lines and len(lines) > 0:
            invoice_numbers = [line.invoice_id.number for line in lines]
            raise except_orm(_('Error!'),
                             _("You can't delete this Commission Worksheet, \
                                because commission has been issued for \
                                Invoice No. %s" % (",".join(invoice_numbers))))
        else:
            return super(CommissionWorksheetLine, self).unlink()


class ResUsers(models.Model):

    _inherit = "res.users"

    commission_rule_id = fields.Many2one(
        'commission.rule',
        string='Applied Commission',
        required=False,
        readonly=False,
    )
    require_paid = fields.Boolean(
        string='Require Paid Invoice',
        help="Require invoice to be paid in full amount.",
        default=False,
    )
    require_posted = fields.Boolean(
        string='Require Payment Detail Posted',
        help="Require that all payment detail related to payments "
             "to invoice has been posted.",
        default=False,
    )
    allow_overdue = fields.Boolean(
        string='Allow Overdue Payment',
        help="Allow paying commission with overdue payment.",
        default=False,
    )
    last_pay_date_rule = fields.Selection(
        LAST_PAY_DATE_RULE,
        string='Last Pay Date Rule',
    )
    buffer_days = fields.Integer(
        string='Buffer Days',
        default=0,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
