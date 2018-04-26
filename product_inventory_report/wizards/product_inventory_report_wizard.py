# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _


class ProductInventoryReportWizard(models.TransientModel):
    _name = 'product.inventory.report.wizard'

    age_inventory = fields.Integer(
        string='Age Inventory',
    )

    @api.multi
    def open_inventory(self):
        self.ensure_one()
        self._cr.execute("""
            SELECT id
            FROM product_inventory_report
            WHERE DATE_PART('day', '%s' - in_date) + 1 >= %s"""
                         % (fields.Date.today(), self.age_inventory))
        report_ids = list(map(lambda l: l[0], self._cr.fetchall()))
        return {
            'name': _('Inventory Report'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.inventory.report',
            'view_id': self.env.ref(
                        'product_inventory_report'
                        '.view_product_inventory_report_tree').id,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', report_ids)],
            'context': {'search_default_internal_loc': 1},
        }
