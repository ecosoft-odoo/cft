from openerp import models, api
from lxml import etree


class EmailTemplate(models.Model):
    _inherit = 'email.template'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(EmailTemplate, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        User = self.env.user
        root = etree.fromstring(res['arch'])
        if User.has_group('marketing.group_marketing_user'):
            root.set('create', 'true')
            root.set('edit', 'true')
            root.set('delete', 'false')
        if User.has_group('base.group_system'):
            root.set('create', 'true')
            root.set('edit', 'true')
            root.set('delete', 'true')
        res['arch'] = etree.tostring(root)
        return res
