# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_available = fields.Float(
        compute='_product_available',
    )
    incoming_qty = fields.Float(
        compute='_product_available',
    )
    outgoing_qty = fields.Float(
        compute='_product_available',
    )
    virtual_available = fields.Float(
        compute='_product_available',
    )
    sale_available = fields.Float(
        compute='_product_available',
        multi='qty_available',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Available for Sales',
        search='_search_product_quantity',
        help="Sale Available (computed as Quantity On Hand - Outgoing)",
    )

    # Overwrite Method
    @api.multi
    def _product_available(self, field_names=None, arg=False):
        """
        This fuction will overide old method and add 'Available for Sale'
        - Available for Sales = Quantity On Hand - Outgoing
        """
        context = self._context.copy() or {}
        field_names = field_names or []

        domain_products = [('product_id', 'in', self.ids)]
        domain_quant, domain_move_in, domain_move_out = [], [], []
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = \
            self._get_domain_locations()
        domain_move_in += \
            self._get_domain_dates() + \
            [('state', 'not in', ('done', 'cancel', 'draft'))] + \
            domain_products
        domain_move_out += \
            self._get_domain_dates() + \
            [('state', 'not in', ('done', 'cancel', 'draft'))] + \
            domain_products
        domain_quant += domain_products

        if context.get('lot_id'):
            domain_quant.append(('lot_id', '=', context['lot_id']))
        if context.get('owner_id'):
            domain_quant.append(('owner_id', '=', context['owner_id']))
            owner_domain = ('restrict_partner_id', '=', context['owner_id'])
            domain_move_in.append(owner_domain)
            domain_move_out.append(owner_domain)
        if context.get('package_id'):
            domain_quant.append(('package_id', '=', context['package_id']))

        domain_move_in += domain_move_in_loc
        domain_move_out += domain_move_out_loc
        moves_in = self.env['stock.move'].read_group(
            domain_move_in, ['product_id', 'product_qty'], ['product_id'])
        moves_out = self.env['stock.move'].read_group(
            domain_move_out, ['product_id', 'product_qty'], ['product_id'])

        domain_quant += domain_quant_loc
        quants = self.env['stock.quant'].read_group(
            domain_quant, ['product_id', 'qty'], ['product_id'])
        quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))

        moves_in = dict(map(lambda x: (x['product_id'][0], x['product_qty']),
                            moves_in))
        moves_out = dict(map(lambda x: (x['product_id'][0], x['product_qty']),
                             moves_out))
        for product in self:
            id = product.id
            qty_available = float_round(
                quants.get(id, 0.0),
                precision_rounding=product.uom_id.rounding)
            incoming_qty = float_round(
                moves_in.get(id, 0.0),
                precision_rounding=product.uom_id.rounding)
            outgoing_qty = float_round(
                moves_out.get(id, 0.0),
                precision_rounding=product.uom_id.rounding)
            sale_available = float_round(
                quants.get(id, 0.0) - moves_out.get(id, 0.0),
                precision_rounding=product.uom_id.rounding)
            virtual_available = float_round(
                quants.get(id, 0.0) + moves_in.get(id, 0.0) -
                moves_out.get(id, 0.0),
                precision_rounding=product.uom_id.rounding)
            product.qty_available = qty_available
            product.incoming_qty = incoming_qty
            product.outgoing_qty = outgoing_qty
            product.sale_available = sale_available
            product.virtual_available = virtual_available

    @api.model
    def _search_product_quantity(self, obj, name, domain):
        return super(ProductProduct, self)._search_product_quantity(
            obj, name, domain)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qty_available = fields.Float(
        compute='_product_available',
    )
    incoming_qty = fields.Float(
        compute='_product_available',
    )
    outgoing_qty = fields.Float(
        compute='_product_available',
    )
    virtual_available = fields.Float(
        compute='_product_available',
    )
    sale_available = fields.Float(
        compute='_product_available',
        multi='qty_available',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Available for Sales',
        search='_search_product_quantity',
        help="Sale Available (computed as Quantity On Hand - Outgoing)",
    )

    # Overwrite Method
    @api.multi
    def _product_available(self):
        """
        This fuction will overide old method and add 'Available for Sale'
        - Available for Sales = Quantity On Hand - Outgoing
        """
        var_ids = []
        for product in self:
            var_ids += [p.id for p in product.product_variant_ids]
        product = self.env['product.product'].browse(var_ids)
        product._product_available()

        for product in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            sale_available = 0
            for p in product.product_variant_ids:
                qty_available += p.qty_available
                virtual_available += p.virtual_available
                incoming_qty += p.incoming_qty
                outgoing_qty += p.outgoing_qty
                sale_available += p.sale_available
            product.qty_available = qty_available
            product.virtual_available = virtual_available
            product.incoming_qty = incoming_qty
            product.outgoing_qty = outgoing_qty
            product.sale_available = sale_available

    @api.model
    def _search_product_quantity(self, obj, name, domain):
        return super(ProductTemplate, self)._search_product_quantity(
            obj, name, domain)
