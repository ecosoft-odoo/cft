# -*- coding: utf-8 -*-
from openerp import models, api
from lxml import etree


class CRMClaim(models.Model):
    _inherit = 'crm.claim'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(CRMClaim, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        User = self.env.user
        module = 'sale_group_adjust_cft'
        ecommerce_ref = module + '.' + 'group_sale_ecommerce'
        after_service_ref = module + '.' + 'group_sale_after_service'
        if User.has_group(ecommerce_ref) or User.has_group(after_service_ref):
            root = etree.fromstring(res['arch'])
            root.set('delete', 'false')
            res['arch'] = etree.tostring(root)
        return res
