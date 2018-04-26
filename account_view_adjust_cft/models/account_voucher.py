# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'
    _order = 'amount desc, move_line_id'
