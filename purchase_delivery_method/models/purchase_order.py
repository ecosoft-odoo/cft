# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_method = fields.Char('Delivery Method')
