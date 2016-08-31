# -*- coding: utf-8 -*-
# Copyright 2016 Ecosoft Co. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv


class crm_lead(osv.osv):
    _inherit = 'crm.lead'

    def action_schedule_meeting(self, cr, uid, ids, context=None):
        res = super(crm_lead, self).action_schedule_meeting(cr, uid, ids, context=context)
        lead = self.browse(cr, uid, ids[0], context)
        res['context'].update({
            'search_default_opportunity_id': lead.id or False,
            'default_opportunity_id': lead.id or False})
        return res
