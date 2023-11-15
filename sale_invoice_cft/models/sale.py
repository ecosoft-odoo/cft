# -*- coding: utf-8 -*-

from openerp import models, fields, api


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    date_invoice = fields.Char(
        string="Invoice Date",
        compute="_compute_invoice_info",
    )
    invoice_number = fields.Char(
        string="Invoice Number",
        compute="_compute_invoice_info",
    )

    @api.depends("invoice_lines")
    def _compute_invoice_info(self):
        for rec in self:
            invoices = rec.invoice_lines.mapped("invoice_id")
            rec.update({
                "date_invoice": ", ".join(
                    list(
                        set(
                            [
                                "{}-{}-{}".format(
                                    inv.date_invoice.year,
                                    inv.date_invoice.month,
                                    inv.date_invoice.day
                                ) for inv in invoices if inv.date_invoice]
                            )
                        )
                    ),
                "invoice_number": ", ".join(
                    list(
                        set(
                            [
                                inv.number for inv in invoices if inv.number]
                            )
                        )
                    ),
            })
