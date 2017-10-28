# -*- coding: utf-8 -*-
from openerp import models, api
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        User = self.env.user
        module = 'sale_group_adjust_cft'
        ecommerce_ref = module + '.' + 'group_sale_ecommerce'
        marketing_ref = module + '.' + 'group_sale_marketing'
        if User.has_group(ecommerce_ref) or User.has_group(marketing_ref):
            root = etree.fromstring(res['arch'])
            root.set('delete', 'false')
            if User.has_group(marketing_ref):
                root.set('create', 'false')
                root.set('edit', 'false')
            res['arch'] = etree.tostring(root)
        return res
