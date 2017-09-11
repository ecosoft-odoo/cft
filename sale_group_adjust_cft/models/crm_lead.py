# -*- coding: utf-8 -*-
from openerp import models, api
from lxml import etree


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(CRMLead, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        User = self.env.user
        module = 'sale_group_adjust_cft'
        after_service_ref = module + '.' + 'group_sale_after_service'
        if User.has_group(after_service_ref):
            root = etree.fromstring(res['arch'])
            root.set('delete', 'false')
            res['arch'] = etree.tostring(root)
        return res
