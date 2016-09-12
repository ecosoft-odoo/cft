# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Rooms For (Hong Kong) Limited T/A OSCG
#    <https://www.odoo-asia.com>
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
from openerp.osv import fields, osv


class crm_lead_calculation(osv.osv):
    _inherit = 'crm.lead'


    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        """ Calculates Estimated Revennue.
        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param uid: The current user ID for security checks
        @param ids: List of selected IDs
        @param field_name: Name of field.
        @param arg: Argument
        @param context: A standard dictionary for contextual values
        @return: Dictionary of values.
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = {
                'planned_revenue': 0.0,
                'lead.probability': 0.0,
            }
            res[record.id]= record.planned_revenue * record.probability / 100
        return res


    _columns = {'estimated_revenue': fields.function(_amount_total,string='Estimated Revenue')
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: