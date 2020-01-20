# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2019 Eficent Business and IT Consulting Services S.L..
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import fields, models
import openerp.addons.decimal_precision as dp

UNIT = dp.get_precision("Location")


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    latitude = fields.Float(
        string="Latitude",
        digits=UNIT,
        readonly=True
    )
    longitude = fields.Float(
        string="Longitude",
        digits=UNIT,
        readonly=True
    )
