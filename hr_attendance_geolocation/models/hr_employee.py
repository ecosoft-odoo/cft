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

from openerp import api, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def attendance_action_change(self):
        res = super(HrEmployee, self).attendance_action_change()
        rec = self.env['hr.attendance'].search(
            [('employee_id', '=', self.id)], order='id desc', limit=1)
        location = self.env.context.get('attendance_location', False)
        if location:
            rec.write({
                'latitude': location[0],
                'longitude': location[1],
            })
        return res
