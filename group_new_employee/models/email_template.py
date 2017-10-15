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
        if User.has_group('group_new_employee.group_marketing_user_readonly'):
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            root.set('edit', 'false')
            root.set('delete', 'false')
            res['arch'] = etree.tostring(root)
        return res
