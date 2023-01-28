# Copyright 2022 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = "res.doctype"

    refer_type = fields.Selection(
        selection_add=[
            ("temporary_delivery_bill", "Temporary Delivery Bill"),
        ],
    )
