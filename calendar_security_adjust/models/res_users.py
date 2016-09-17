# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    company_user = fields.Boolean('Company User')
