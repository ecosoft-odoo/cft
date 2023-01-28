# Copyright 2022 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
 

class TemporaryDeliveryBill(models.Model):
    _name = "temporary.delivery.bill"
    _description = "Temporary Delivery Bill"

    name = fields.Char(
        string="Number",
        required=True,
        readonly=True,
        default="/",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        readonly=True,
        index=True,
    )
    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Order Reference",
        required=True,
        readonly=True,
        index=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )
    delivery_bill_lines = fields.One2many(
        comodel_name="temporary.delivery.bill.line",
        inverse_name="bill_id",
        string="Delivery Bill Lines",
    )

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            # Find doctype_id
            refer_type = "temporary_delivery_bill"
            doctype = self.env["res.doctype"].get_doctype(refer_type)
            fiscalyear_id = self.env["account.fiscalyear"].find()
            # --
            self = self.with_context(doctype_id=doctype.id,
                                     fiscalyear_id=fiscalyear_id)
            vals["name"] = self.env["ir.sequence"].next_by_doctype()
        return super(TemporaryDeliveryBill, self).create(vals)


class TemporaryDeliveryBillLine(models.Model):
    _name = "temporary.delivery.bill.line"
    _description = "Temporary Delivery Bill Lines"

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        index=True,
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        required=True,
        digits_compute=dp.get_precision("Product Unit of Measure"),
    )
    product_uom = fields.Many2one(
        comodel_name="product.uom",
        string="Unit of Measure",
        required=True,
        index=True,
    )
    bill_id = fields.Many2one(
        comodel_name="temporary.delivery.bill",
        string="Delivery Bill",
        index=True,
    )
