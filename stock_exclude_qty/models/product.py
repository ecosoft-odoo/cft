# -*- coding: utf-8 -*-
from openerp import models, api

ACTIVE_MODEL = ['stock.location', ]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _get_domain_locations(self):
        res = super(ProductProduct, self)._get_domain_locations()
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = res
        context = self._context.copy()
        domain_exclude_loc = []
        domain_exclude_dest_loc = []
        if context.get('active_model', False) not in ACTIVE_MODEL:
            Location = self.env['stock.location']
            exclude_ids = Location.search([('exclude_qty', '=', True)]).ids
            domain_exclude_loc = [('location_id', 'not in', exclude_ids)]
            domain_exclude_dest_loc = [('location_dest_id', 'not in',
                                        exclude_ids)]
        return (
            domain_exclude_loc + domain_quant_loc,
            domain_exclude_loc + domain_exclude_dest_loc + domain_move_in_loc,
            domain_exclude_loc + domain_exclude_dest_loc + domain_move_out_loc
        )
