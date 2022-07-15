# Copyright 2022 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_bill_count = fields.Integer(
        string="Delivery Bill Count",
        compute="_compute_delivery_bill_count",
    )
    delivery_bill_ids = fields.One2many(
        comodel_name="temporary.delivery.bill",
        inverse_name="order_id",
    )

    @api.multi
    @api.depends("delivery_bill_ids")
    def _compute_delivery_bill_count(self):
        for rec in self:
            rec.delivery_bill_count = len(rec.delivery_bill_ids)

    @api.multi
    def view_temporary_delivery_bill(self):
        self.ensure_one()
        action = self.env.ref(
            "sale_temporary_delivery_bill.temporary_delivery_bill_action")
        result = action.read()[0]
        # Update context
        context = self._context.copy()
        context.update({
            "default_partner_id": self.partner_id.id,
            "default_order_id": self.id,
            "default_delivery_bill_lines": [(0, 0, {
                "product_id": line.product_id.id,
                "product_uom_qty": line.product_uom_qty,
                "product_uom": line.product_uom.id
            }) for line in self.order_line]
        })
        # Update result
        result.update({
            "context": context,
            "domain": [("order_id", "=", self.id)]
        })
        return result
